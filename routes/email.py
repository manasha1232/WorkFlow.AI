from fastapi import APIRouter
from utils.gmail_service import get_gmail_service
from config.google_oauth import SCOPES


router = APIRouter(prefix="/api/email")

@router.get("/list")
def list_emails(
    token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str
):
    service = get_gmail_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )

    results = service.users().messages().list(
        userId="me", maxResults=10
    ).execute()

    messages = results.get("messages", [])
    return {"messages": messages}
