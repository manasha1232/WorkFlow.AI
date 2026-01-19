# utils/gmail_service.py

import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Enable HTTP (ONLY for local dev)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def get_gmail_service(
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    scopes: list
):
    """
    Returns an authenticated Gmail API service using token + refresh token.

    This function handles:
    - Creating Credentials object manually
    - Refreshing expired tokens using Google OAuth endpoints
    - Returning a working Gmail API service client
    """

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=scopes
    )

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print("❌ Token refresh failed:", e)
            raise

    # Create Gmail API service
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print("❌ Failed to build Gmail Service:", e)
        raise
