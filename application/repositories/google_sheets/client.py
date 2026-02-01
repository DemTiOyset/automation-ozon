from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def build_sheets_service(sa_json_path: str):
    """
    Создаёт клиент Google Sheets API от имени Service Account.
    """
    sa_path = Path(sa_json_path)

    if not sa_path.exists():
        raise FileNotFoundError(f"Service account json not found: {sa_path}")

    creds = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=SHEETS_SCOPES,
    )

    service = build(
        "sheets",
        "v4",
        credentials=creds,
        cache_discovery=False,
    )
    return service
