# DataOrigin Package

This package provides core utilities for the DataOrigin project, focusing on leveraging AI-driven data insights for sales prospecting and lead generation in the B2B event space.

## Installation

To install the `dataorigin` package, you can use pip:

```bash
pip install dataorigin
```

## Usage

Example usage for `google_sheets.py` (assuming you have configured credentials using environment variables):

- `GOOGLE_SERVICE_ACCOUNT_JSON`: full Service Account JSON as a string (recommended for containers)
- `GOOGLE_APPLICATION_CREDENTIALS`: absolute path to Service Account JSON
- `GOOGLE_OAUTH_CLIENT_SECRET_FILE`: path to OAuth client secret file (interactive, local dev)
- `GOOGLE_OAUTH_TOKEN_FILE`: where to persist OAuth token (default: `token.json`)
- `GOOGLE_OAUTH_PORT`: OAuth local server port (default: `0`)

```python
import os
import pandas as pd
from dataorigin.google_sheets import upsert_google_sheet, read_google_sheet

# Example: Write data to a spreadsheet
df = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])

res = upsert_google_sheet(
    df=df,
    spreadsheet_id="YOUR_SPREADSHEET_ID",           # or use spreadsheet_title="..."
    sheet_name="data",                              # optional: target sheet (created if missing)
    folder_id=os.getenv("GDRIVE_FOLDER_ID"),         # optional
    clear=True,
    value_input_option="USER_ENTERED",              # "RAW" or "USER_ENTERED"
    rename_sheet=False
)

# Example: Read data from a spreadsheet (reads the first sheet by default)
data = read_google_sheet(spreadsheet_id="YOUR_SPREADSHEET_ID")
print(data)
```

## License

This project is licensed under the GNU General Public License v3.0 - see the `LICENSE` file for details.
