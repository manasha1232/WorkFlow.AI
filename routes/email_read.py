from fastapi import APIRouter
from utils.gmail_service import get_gmail_service
from config.google_oauth import SCOPES
import base64
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api/email")


def extract_body(payload):
    """
    Extract readable email body text from Gmail API payload.
    """
    parts = payload.get("parts", [])

    for part in parts:
        if part["mimeType"] == "text/plain":
            data = part["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        if part["mimeType"] == "text/html":
            data = part["body"].get("data")
            if data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                return BeautifulSoup(html, "html.parser").text

        # Nested parts
        if "parts" in part:
            nested = extract_body(part)
            if nested:
                return nested

    return "(No readable content)"


@router.get("/read")
def read_email(message_id: str, token: str, refresh_token: str, client_id: str, client_secret: str):

    service = get_gmail_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )

    email = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = email.get("payload", {})
    body_text = extract_body(payload)

    return {
        "id": message_id,
        "snippet": email.get("snippet"),
        "body": body_text
    }
