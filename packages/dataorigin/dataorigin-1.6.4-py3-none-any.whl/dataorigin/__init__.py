from . import google_sheets

__all__ = ["google_sheets"]
try:
    from importlib.metadata import PackageNotFoundError, version
except Exception:  # noqa: BLE001
    version = None
    PackageNotFoundError = Exception

try:
    __version__ = version("dataorigin") if version else "0.0.0"
except PackageNotFoundError:
    __version__ = "0.0.0"
