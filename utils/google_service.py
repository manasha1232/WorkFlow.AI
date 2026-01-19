# utils/google_service.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Tuple

def build_credentials(token: str, refresh_token: str, client_id: str, client_secret: str, scopes: list) -> Credentials:
    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )
    return creds

def get_calendar_service(token: str, refresh_token: str, client_id: str, client_secret: str, scopes: list):
    creds = build_credentials(token, refresh_token, client_id, client_secret, scopes)
    service = build("calendar", "v3", credentials=creds)
    return service

def get_tasks_service(token: str, refresh_token: str, client_id: str, client_secret: str, scopes: list):
    creds = build_credentials(token, refresh_token, client_id, client_secret, scopes)
    service = build("tasks", "v1", credentials=creds)
    return service
