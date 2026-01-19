from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar_service(token, refresh_token, client_id, client_secret, scopes):
    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )

    service = build("calendar", "v3", credentials=creds)
    return service
