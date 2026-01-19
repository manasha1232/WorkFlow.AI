from fastapi import APIRouter
from utils.calendar_service import get_calendar_service
from config.google_oauth import SCOPES
import datetime

router = APIRouter(prefix="/api/calendar")

@router.get("/events")
def get_calendar_events(
    token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str
):
    service = get_calendar_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )

    now = datetime.datetime.utcnow().isoformat() + "Z"  # UTC time
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return {"events": events}
