from fastapi import APIRouter
from utils.tasks_service import get_tasks_service
from config.google_oauth import SCOPES

router = APIRouter(prefix="/api/tasks")

@router.post("/create")
def create_task(
    token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    title: str,
    notes: str = "",
    due: str = None   # format: "2025-12-01T09:00:00.000Z"
):
    service = get_tasks_service(
        token, refresh_token, client_id, client_secret, SCOPES
    )

    task_body = {
        "title": title,
        "notes": notes
    }

    if due:
        task_body["due"] = due

    result = service.tasks().insert(
        tasklist='@default',
        body=task_body
    ).execute()

    return {"task_created": result}
