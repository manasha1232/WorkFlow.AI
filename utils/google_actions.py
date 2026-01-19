# utils/google_actions.py

from utils.google_clients import get_calendar_service, get_tasks_service

def create_calendar_event(token, refresh, cid, secret, date, summary):
    service = get_calendar_service(token, refresh, cid, secret)

    event = {
        "summary": summary[:100],
        "start": {"date": date},
        "end": {"date": date},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return created.get("id")


def create_google_task(token, refresh, cid, secret, summary):
    service = get_tasks_service(token, refresh, cid, secret)

    task_body = {
        "title": summary[:80]
    }

    created = service.tasks().insert(tasklist="@default", body=task_body).execute()
    return created.get("id")
