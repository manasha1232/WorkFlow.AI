# routes/email_actions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import dateparser
from datetime import timedelta
import os

from utils.google_service import get_calendar_service, get_tasks_service

# Scopes required for calendar & tasks
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks"
]

router = APIRouter(prefix="/api/email", tags=["email-actions"])

class CreateActionsRequest(BaseModel):
    text: str                     # cleaned or summarized email text (string)
    token: str
    refresh_token: str
    client_id: str
    client_secret: str
    calendar_id: Optional[str] = "primary"   # optional, default primary
    task_list_id: Optional[str] = None       # optional: if None will use default tasklist (first)
    timezone: Optional[str] = "Asia/Kolkata" # default timezone

def _parse_datetime_from_text(text: str, timezone: str):
    """
    Try to parse a date/time from text using dateparser.
    Returns aware datetime object or None.
    """
    if not text or not isinstance(text, str):
        return None

    settings = {
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",   # prefer future (for events)
        "TIMEZONE": timezone
    }

    dt = dateparser.parse(text, settings=settings)
    return dt

def _rfc3339(dt):
    # Google Calendar wants RFC3339 format (with timezone)
    # dateparser gives timezone-aware dt usually; isoformat preserves offset
    return dt.isoformat()

@router.post("/create_actions")
def create_actions(req: CreateActionsRequest):
    # 1) Parse datetime
    dt = _parse_datetime_from_text(req.text, req.timezone)
    if dt is None:
        raise HTTPException(status_code=400, detail="No date/time detected in text")

    # 2) Create Calendar event (1 hour default duration)
    cal_svc = get_calendar_service(req.token, req.refresh_token, req.client_id, req.client_secret, SCOPES)
    start_rfc = _rfc3339(dt)
    end_rfc = _rfc3339(dt + timedelta(hours=1))

    event_body = {
        "summary": "Auto: " + (req.text[:80] + "..." if len(req.text) > 80 else req.text),
        "description": req.text,
        "start": {"dateTime": start_rfc},
        "end": {"dateTime": end_rfc},
    }

    try:
        created_event = cal_svc.events().insert(calendarId=req.calendar_id, body=event_body).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar create failed: {e}")

    # 3) Create Task (in Tasks API)
    tasks_svc = get_tasks_service(req.token, req.refresh_token, req.client_id, req.client_secret, SCOPES)

    # determine tasklist: use provided or fetch default
    task_list_id = req.task_list_id
    try:
        if not task_list_id:
            lists = tasks_svc.tasklists().list(maxResults=10).execute()
            items = lists.get("items", [])
            task_list_id = items[0]["id"] if items else "@default"
    except Exception as e:
        # fallback to default
        task_list_id = "@default"

    # Tasks API expects due as RFC3339 in full datetime with timezone truncated to date or RFC3339 date-time?
    # Use due as dateTime if supported; task API uses 'due' (RFC3339) - it's okay to pass datetime string
    task_body = {
        "title": "Auto Task: " + (req.text[:60] + "..." if len(req.text) > 60 else req.text),
        "notes": req.text,
        "due": start_rfc
    }

    try:
        created_task = tasks_svc.tasks().insert(tasklist=task_list_id, body=task_body).execute()
    except Exception as e:
        # If task creation fails, still return event id but indicate task error
        return {
            "calendar_event": created_event,
            "task_error": str(e),
            "message": "Calendar created but tasks failed"
        }

    return {
        "calendar_event": {
            "id": created_event.get("id"),
            "htmlLink": created_event.get("htmlLink"),
            "start": created_event.get("start"),
            "end": created_event.get("end"),
            "summary": created_event.get("summary")
        },
        "task": {
            "id": created_task.get("id"),
            "title": created_task.get("title"),
            "due": created_task.get("due")
        }
    }
