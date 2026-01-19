# utils/google_clients.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# -----------------------------------------
# Build OAuth Credentials
# -----------------------------------------
def build_credentials(token, refresh_token, client_id, client_secret):
    """
    Builds OAuth2 credentials using access_token + refresh_token.
    """
    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/tasks"
        ],
    )
    return creds


# -----------------------------------------
# Gmail API Client
# -----------------------------------------
def get_gmail_service(token, refresh_token, client_id, client_secret):
    creds = build_credentials(token, refresh_token, client_id, client_secret)
    return build("gmail", "v1", credentials=creds)


# -----------------------------------------
# Google Calendar API Client
# -----------------------------------------
def get_calendar_service(token, refresh_token, client_id, client_secret):
    creds = build_credentials(token, refresh_token, client_id, client_secret)
    return build("calendar", "v3", credentials=creds)


# -----------------------------------------
# Google Tasks API Client
# -----------------------------------------
def get_tasks_service(token, refresh_token, client_id, client_secret):
    creds = build_credentials(token, refresh_token, client_id, client_secret)
    return build("tasks", "v1", credentials=creds)
