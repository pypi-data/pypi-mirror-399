import os, json, time, logging
from typing import Optional, Tuple, List, Dict
import datetime  # Needed for timestamp-based sheet names

import pandas as pd
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes necesarios para acceder a Google Drive y Sheets
SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
logger = logging.getLogger(__name__)

def _load_credentials(scopes: List[str] = SCOPES):
    """
    Carga las credenciales de Google API usando tres métodos en orden de prioridad:
    1. Service Account JSON desde variable de entorno GOOGLE_SERVICE_ACCOUNT_JSON
    2. Service Account desde archivo especificado en GOOGLE_APPLICATION_CREDENTIALS
    3. OAuth2 flow usando GOOGLE_OAUTH_CLIENT_SECRET_FILE
    
    Args:
        scopes: Lista de permisos requeridos para la API
        
    Returns:
        Credentials object válido para autenticación
        
    Raises:
        RuntimeError: Si no se pueden cargar credenciales válidas
    """
    # Método 1: Service Account desde variable de entorno (JSON string)
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            info = json.loads(sa_json)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("Invalid GOOGLE_SERVICE_ACCOUNT_JSON (must be a JSON string)") from e
        try:
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("Failed to load credentials from GOOGLE_SERVICE_ACCOUNT_JSON") from e
        return creds
        
    
    # Método 2: Service Account desde archivo
    
    sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_path: 
        try:
            creds = service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("Failed to load credentials from GOOGLE_APPLICATION_CREDENTIALS") from e
        return creds
    
    # Método 3: OAuth2 flow para autenticación de usuario
    client_secret_file = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET_FILE")
    token_path = os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "token.json")
    oauth_client_id = (os.getenv("OAUTH2_CLIENT_ID") or os.getenv("GOOGLE_OAUTH_CLIENT_ID") or "").strip()
    oauth_client_secret = (os.getenv("OAUTH2_CLIENT_SECRET") or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()
    has_oauth_env = bool(oauth_client_id and oauth_client_secret)

    if client_secret_file or has_oauth_env:
        creds: Optional[UserCredentials] = None
        
        # Intentar cargar token existente
        if os.path.exists(token_path):
            try: 
                creds = UserCredentials.from_authorized_user_file(token_path, scopes)
            except Exception: 
                creds = None
        
        # Si no hay credenciales válidas, refrescar o crear nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try: 
                    creds.refresh(Request())
                except Exception: 
                    creds = None
            
            # Si no se puede refrescar, iniciar nuevo flow OAuth
            if not creds:
                if client_secret_file:
                    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes=scopes)
                else:
                    client_config = {
                        "installed": {
                            "client_id": oauth_client_id,
                            "client_secret": oauth_client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost"],
                        }
                    }
                    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
                creds = flow.run_local_server(port=int(os.getenv("GOOGLE_OAUTH_PORT", "0")))
            
            # Guardar token para uso futuro
            try:
                with open(token_path, "w", encoding="utf-8") as f: 
                    f.write(creds.to_json())
            except Exception: 
                logger.warning("Failed to persist OAuth token to %s", token_path)
        
        return creds
    
    raise RuntimeError("Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_OAUTH_CLIENT_SECRET_FILE or OAUTH2_CLIENT_ID/OAUTH2_CLIENT_SECRET")

def _build_services(scopes: List[str] = SCOPES):
    """
    Construye los objetos de servicio para Google Sheets y Drive APIs.
    
    Args:
        scopes: Lista de permisos requeridos
        
    Returns:
        Tuple con (sheets_service, drive_service) listos para usar
    """
    creds = _load_credentials(scopes)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return sheets, drive

def _retry(call, retries: int = 3, base: float = 1.0):
    """
    Implementa reintentos con backoff exponencial para llamadas a la API.
    Reintenta automáticamente en caso de errores 429 (rate limit) y 5xx (server errors).
    
    Args:
        call: Función lambda a ejecutar
        retries: Número máximo de reintentos
        base: Tiempo base en segundos para el backoff
        
    Returns:
        Resultado de la llamada exitosa
        
    Raises:
        HttpError: Si falla después de todos los reintentos
    """
    for i in range(retries + 1):
        try: 
            return call()
        except HttpError as e:
            # Extraer código de estado del error
            status = getattr(e, "status_code", None) or getattr(getattr(e, "resp", None), "status", None)
            
            # Reintentar solo para errores específicos y si quedan reintentos
            if status in [429, 500, 502, 503, 504] and i < retries:
                time.sleep(base * (2 ** i))  # Backoff exponencial: 1s, 2s, 4s...
                continue
            raise

def _df_to_values(df: pd.DataFrame) -> List[List]:
    """
    Convierte un DataFrame de pandas a formato de valores para Google Sheets.
    Maneja valores nulos y NaN convirtiéndolos a strings vacíos.
    
    Args:
        df: DataFrame de pandas a convertir
        
    Returns:
        Lista de listas donde cada lista interna es una fila del DataFrame
        La primera fila contiene los nombres de las columnas
    """
    # Crear header con nombres de columnas
    header = [str(c) for c in df.columns.tolist()]
    values: List[List] = [header]
    
    # Convertir cada fila del DataFrame
    for row in df.itertuples(index=False, name=None):
        # Manejar valores nulos y NaN
        clean_row = ["" if (v is None or (isinstance(v, float) and pd.isna(v))) else v for v in row]
        values.append(clean_row)
    
    return values

def _find_spreadsheet_by_title(drive, title: str, folder_id: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Busca un spreadsheet existente en Google Drive por su título.
    
    Args:
        drive: Servicio de Google Drive API
        title: Título del spreadsheet a buscar
        folder_id: ID de carpeta donde buscar (opcional)
        
    Returns:
        Diccionario con información del spreadsheet encontrado o None si no existe
        Contiene: id, name, webViewLink
    """
    if not title: return None
    safe = title.replace("'", "\\'")
    q = f"mimeType='application/vnd.google-apps.spreadsheet' and trashed=false and name='{safe}'"
    if folder_id: q += f" and '{folder_id}' in parents"
    res = _retry(lambda: drive.files().list(
        q=q,
        fields="files(id,name,webViewLink)",
        pageSize=1,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        corpora="allDrives"
    ).execute())
    files = res.get("files", [])
    return files[0] if files else None

def _ensure_spreadsheet(sheets, drive, spreadsheet_title: Optional[str], spreadsheet_id: Optional[str], folder_id: Optional[str]) -> Dict[str, str]:
    """
    Asegura que existe un spreadsheet, ya sea usando uno existente o creando uno nuevo.
    
    Args:
        sheets: Servicio de Google Sheets API
        drive: Servicio de Google Drive API
        spreadsheet_title: Título del spreadsheet (opcional si se proporciona ID)
        spreadsheet_id: ID del spreadsheet existente (opcional)
        folder_id: ID de carpeta donde crear el spreadsheet (opcional)
        
    Returns:
        Diccionario con información del spreadsheet: id, name, url
    """
    # Si se proporciona ID, obtener información del spreadsheet existente
    if spreadsheet_id:
        # Prefer Sheets API to avoid Drive 404 on permission quirks
        meta = _retry(lambda: sheets.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="spreadsheetId,properties(title),spreadsheetUrl"
        ).execute())
        return {"id": meta["spreadsheetId"], "name": meta["properties"]["title"], "url": meta.get("spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}")}


    
    # Buscar spreadsheet existente por título
    found = _find_spreadsheet_by_title(drive, spreadsheet_title, folder_id)
    if found: 
        return {"id": found["id"], "name": spreadsheet_title, "url": found.get("webViewLink", "")}
    
    # Crear nuevo spreadsheet
    body = {"name": spreadsheet_title, "mimeType": "application/vnd.google-apps.spreadsheet"}
    if folder_id: 
        body["parents"] = [folder_id]
    
    created = _retry(lambda: drive.files().create(
        body=body,
        fields="id,webViewLink",
        supportsAllDrives=True
    ).execute())
    return {"id": created["id"], "name": spreadsheet_title, "url": created.get("webViewLink", "")}

def _ensure_sheet_exists(sheets, spreadsheet_id: str, sheet_name: str) -> int:
    """
    Asegura que existe una hoja específica dentro del spreadsheet.
    Si no existe, la crea automáticamente.
    
    Args:
        sheets: Servicio de Google Sheets API
        spreadsheet_id: ID del spreadsheet
        sheet_name: Nombre de la hoja a verificar/crear
        
    Returns:
        ID numérico de la hoja (sheetId)
    """
    # Obtener metadatos del spreadsheet para verificar hojas existentes
    meta = _retry(lambda: sheets.spreadsheets().get(spreadsheetId=spreadsheet_id, fields="sheets(properties(sheetId,title))").execute())
    
    # Buscar la hoja por nombre
    for s in meta.get("sheets", []):
        p = s.get("properties", {})
        if p.get("title") == sheet_name: 
            return int(p.get("sheetId"))
    
    # Si no existe, crear nueva hoja
    req = {"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}
    resp = _retry(lambda: sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=req).execute())
    
    return int(resp["replies"][0]["addSheet"]["properties"]["sheetId"])

def upsert_google_sheet(
    df: pd.DataFrame,
    spreadsheet_title: Optional[str] = None,
    sheet_name: Optional[str] = None,
    folder_id: Optional[str] = None,
    spreadsheet_id: Optional[str] = None,
    clear: bool = True,
    value_input_option: str = "USER_ENTERED",
    rename_sheet: bool = True,
    rename_sheet_to: Optional[str] = None
) -> Dict[str, str]:
    """
    Función principal para subir o actualizar un DataFrame en Google Sheets.
    Si `sheet_name` se proporciona, se usará esa hoja (creándola si no existe). Si no,
    se usará la primera hoja del spreadsheet.
    Si `clear` es True, se limpia la hoja antes de subir los datos.
    Si `rename_sheet` es True, la hoja se renombra (por defecto a una marca de tiempo).
    
    Esta función:
    1. Valida los parámetros de entrada
    2. Autentica con Google APIs
    3. Encuentra o crea el spreadsheet
    4. Asegura que existe al menos una hoja y obtiene su ID y nombre actual
    5. Limpia la hoja (si `clear` es True)
    6. Sube los datos del DataFrame
    7. Renombra la hoja a la marca de tiempo actual.
    
    Args:
        df: DataFrame de pandas con los datos a subir
        spreadsheet_title: Título del spreadsheet (opcional si se usa spreadsheet_id)
        sheet_name: Nombre de la hoja dentro del spreadsheet (si no existe, se crea).
        folder_id: ID de carpeta en Google Drive donde crear el spreadsheet (opcional)
        spreadsheet_id: ID de spreadsheet existente (opcional si se usa spreadsheet_title)
        clear: Si limpiar la hoja antes de subir datos (default: True)
        value_input_option: "RAW" para valores literales o "USER_ENTERED" para interpretación (default: "USER_ENTERED")
        rename_sheet: Si renombrar la hoja tras escribir (default: True)
        rename_sheet_to: Nombre explícito para el renombrado (opcional)
        
    Returns:
        Diccionario con resultado de la operación:
        - status: Código de estado HTTP
        - message: Mensaje descriptivo
        - spreadsheet_id: ID del spreadsheet usado
        - sheet_name: Nombre final de la hoja (si se renombra, será el nuevo nombre)
        - url: URL del spreadsheet (si está disponible)
        
    Raises:
        RuntimeError: Si hay problemas de autenticación o configuración
        HttpError: Si hay errores en las llamadas a la API
    """
    # Validaciones de entrada
    if df is None or not isinstance(df, pd.DataFrame): 
        return {"status": "400 Bad Request", "message": "df must be a pandas.DataFrame"}
    
    if not spreadsheet_id and not spreadsheet_title: 
        return {"status": "400 Bad Request", "message": "Provide spreadsheet_id or spreadsheet_title"}
    
    # Construir servicios de Google APIs
    sheets, drive = _build_services()
    
    # Asegurar que existe el spreadsheet
    doc = _ensure_spreadsheet(sheets, drive, spreadsheet_title, spreadsheet_id, folder_id)
    
    # Ensure there is at least one sheet
    meta = _retry(lambda: sheets.spreadsheets().get(spreadsheetId=doc["id"], fields="sheets.properties.sheetId,sheets.properties.title").execute())
    if not meta.get("sheets"):
        _ensure_sheet_exists(sheets, doc["id"], "Sheet1")
        meta = _retry(lambda: sheets.spreadsheets().get(spreadsheetId=doc["id"], fields="sheets.properties.sheetId,sheets.properties.title").execute())
        if not meta.get("sheets"):
            raise RuntimeError("Failed to ensure at least one sheet in the spreadsheet")

    if sheet_name:
        sheet_id = _ensure_sheet_exists(sheets, doc["id"], sheet_name)
        current_sheet_name = sheet_name
    else:
        first_sheet_properties = meta["sheets"][0]["properties"]
        sheet_id = first_sheet_properties["sheetId"]
        current_sheet_name = first_sheet_properties["title"]

    # Limpiar hoja si se solicita
    if clear: 
        _retry(lambda: sheets.spreadsheets().values().clear(spreadsheetId=doc["id"], range=current_sheet_name).execute())
    
    # Convertir DataFrame a formato de valores
    values = _df_to_values(df)
    body = {"values": values}
    
    # Subir datos a la hoja
    _retry(lambda: sheets.spreadsheets().values().update(
        spreadsheetId=doc["id"], 
        range=f"{current_sheet_name}!A1", # Usar el nombre actual para la subida inicial
        valueInputOption=value_input_option, 
        body=body
    ).execute())
    
    # Rename sheet after upload (optional)
    new_sheet_name = current_sheet_name
    if rename_sheet:
        new_sheet_name = rename_sheet_to or datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        if current_sheet_name != new_sheet_name:
            rename_request = {"requests": [{"updateSheetProperties": {"properties": {"sheetId": sheet_id, "title": new_sheet_name}, "fields": "title"}}]}
            _retry(lambda: sheets.spreadsheets().batchUpdate(spreadsheetId=doc["id"], body=rename_request).execute())

    # Aplicar formato después de subir y renombrar (sin "table mode")
    format_requests = [
        # 1. Primera fila (encabezados) con color #fff2cc, negrita y texto centrado
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1, # Solo la primera fila
                    "startColumnIndex": 0,
                    "endColumnIndex": df.shape[1] # Hasta el número de columnas del DataFrame
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.949, "blue": 0.8},
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment"
            }
        },
        # 2. Congelar la primera fila y las dos primeras columnas
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenColumnCount": 2, "frozenRowCount": 1}
                },
                "fields": "gridProperties.frozenColumnCount,gridProperties.frozenRowCount"
            }
        },
        # 3. Añadir bordes a todas las celdas
        {
            "updateBorders": {
                "range": {"sheetId": sheet_id},
                "top": {"style": "SOLID", "width": 1, "color": {"red": 0.85, "green": 0.85, "blue": 0.85}},
                "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.85, "green": 0.85, "blue": 0.85}},
                "left": {"style": "SOLID", "width": 2},
                "right": {"style": "SOLID", "width": 2},
                "innerHorizontal": {"style": "SOLID", "width": 1, "color": {"red": 0.85, "green": 0.85, "blue": 0.85}},
                "innerVertical": {"style": "SOLID", "width": 1}
            }
        },
        # 4. Forzar CLIP para que el texto que no quepa no desborde ni haga wrap
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id},
                "cell": {"userEnteredFormat": {"wrapStrategy": "CLIP"}},
                "fields": "userEnteredFormat.wrapStrategy"
            }
        },
        # 5. Establecer ancho máximo uniforme de 200 px para todas las columnas excepto la primera
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": df.shape[1]
                },
                "properties": {"pixelSize": 200},
                "fields": "pixelSize"
            }
        },
        # 6. Autoajustar solo la primera columna según su contenido
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1
                }
            }
        },
        
    ]

    # Ejecutar las solicitudes de formato
    _retry(lambda: sheets.spreadsheets().batchUpdate(
        spreadsheetId=doc["id"],
        body={"requests": format_requests}
    ).execute())

    return {
        "status": "200 OK", 
        "message": "Sheet updated, renamed and formatted", # Actualizar mensaje
        "spreadsheet_id": doc["id"], 
        "sheet_name": new_sheet_name, # Devolver el nuevo nombre
        "url": doc.get("url", "")
    }

def read_google_sheet(
    spreadsheet_id: str,
    # Eliminar sheet_name de los parámetros
    value_render_option: str = "FORMATTED_VALUE"  # RAW, FORMATTED_VALUE, UNFORMATTED_VALUE
) -> List[Dict]: # Cambiar el tipo de retorno a List[Dict]
    """
    Lee datos de Google Sheets de la PRIMERA HOJA y los devuelve como una lista de diccionarios.

    Args:
        spreadsheet_id: ID del spreadsheet de Google.
        value_render_option: Cómo renderizar los valores.
                             "FORMATTED_VALUE" (defecto), "RAW", "UNFORMATTED_VALUE".

    Returns:
        Lista de diccionarios, donde cada diccionario representa una fila y
        las claves son los nombres de las columnas.
    """
    sheets, _ = _build_services()

    # Obtener metadatos del spreadsheet para encontrar el nombre de la primera hoja
    meta = _retry(lambda: sheets.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets.properties.title"
    ).execute())

    first_sheet_name = "Sheet1"
    if meta and "sheets" in meta and len(meta["sheets"]) > 0:
        first_sheet_name = meta["sheets"][0]["properties"]["title"]
    logger.debug("Detected first sheet name: %s", first_sheet_name)  # debug only

    # Rango de la hoja, asumiendo que los datos empiezan en A1
    range_name = f"{first_sheet_name}" # Lee toda la hoja

    result = _retry(lambda: sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueRenderOption=value_render_option
    ).execute())
    logger.debug("Sheets.values().get result: %s", result)  # debug only

    values = result.get('values', [])
    if not values:
        return []

    # La primera fila son los encabezados
    headers = values[0]
    data = []
    for row in values[1:]:
        row_dict = {}
        for i, header in enumerate(headers):
            row_dict[header] = row[i] if i < len(row) else ""
        data.append(row_dict)
    
    return data

#Uso de la función upsert_google_sheet
"""
import os
import pandas as pd
from modules.google_sheets import upsert_google_sheet

df = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])

res = upsert_google_sheet(
    df=df,
    spreadsheet_title="DataOrigin Demo",           # o usa spreadsheet_id="..."
    sheet_name="data",
    folder_id=os.getenv("GDRIVE_FOLDER_ID"),
    clear=True,
    value_input_option="USER_ENTERED"              # RAW o USER_ENTERED
)
print(res)
"""

#Uso de la función read_google_sheet
"""
import os
from modules.google_sheets import read_google_sheet

# Asegúrate de usar un spreadsheet_id válido y compartido con la Service Account
# spreadsheet_id = os.getenv("SPREADSHEET_ID", "TU_SPREADSHEET_ID_AQUI") # Reemplaza con tu ID real
spreadsheet_id = "YOUR_SPREADSHEET_ID" # Example spreadsheet id

# La función read_google_sheet ya no imprime directamente, solo devuelve los datos
read_data = read_google_sheet(
    spreadsheet_id=spreadsheet_id,
    value_render_option="FORMATTED_VALUE"
)

if read_data:
    print("Datos leídos (formato lista de diccionarios, cada diccionario es una fila):")
    for row_dict in read_data:
        print(row_dict)
else:
    print("No se encontraron datos o el spreadsheet está vacío.")
"""

