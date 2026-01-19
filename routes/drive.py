from fastapi import APIRouter
from utils.drive_service import get_drive_service
from config.google_oauth import SCOPES

router = APIRouter(prefix="/api/drive")

@router.get("/list")
def list_drive_files(
    token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str
):
    service = get_drive_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )
    
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])
    return {"files": files}
