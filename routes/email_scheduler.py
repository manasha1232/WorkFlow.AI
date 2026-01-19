# routes/email_scheduler.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import time

from db.database import get_db
from db.crud import get_or_create_user, is_message_processed
from utils.google_clients import get_gmail_service
from routes.email_process_full import process_single_email
from db.models import User

router = APIRouter(prefix="/api/email/scheduler")
scheduler = BackgroundScheduler()
scheduler.start()

LAST_PROCESSED = {}

class SchedulerRequest(BaseModel):
    token: str
    refresh_token: str
    client_id: str
    client_secret: str
    user_email: str
    max_results: int = 10
    interval_minutes: int = 5


def safe_call(fn):
    for _ in range(3):
        try:
            return fn()
        except Exception as e:
            print("Retrying Gmail:", e)
            time.sleep(1)
    return None


@router.post("/auto")
def auto_scheduler(req: SchedulerRequest, db: Session = Depends(get_db)):

    user = get_or_create_user(db, req.user_email)
    user_id = user.id

    def job_logic():
        print(f"\n📬 Scheduler run for user {user_id}")

        service = get_gmail_service(req.token, req.refresh_token, req.client_id, req.client_secret)

        response = safe_call(lambda: service.users().messages().list(
            userId="me",
            q="in:inbox is:unread",
            maxResults=req.max_results
        ).execute())

        if not response:
            print("❌ Gmail request failed.")
            return

        messages = response.get("messages", [])

        for msg in messages:
            mid = msg["id"]

            if is_message_processed(db, user_id, mid):
                print(f"↩ already processed: {mid}")
                continue

            result = process_single_email(
                mid, req.token, req.refresh_token,
                req.client_id, req.client_secret, user_id, db
            )

            print("✔ Processed:", mid)

    scheduler.add_job(
        job_logic,
        trigger="interval",
        minutes=req.interval_minutes,
        id=f"user_{user_id}",
        replace_existing=True
    )

    return {"message": "Scheduler started", "user_id": user_id}


@router.post("/stop")
def stop_scheduler(user_email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    jid = f"user_{user.id}"
    job = scheduler.get_job(jid)

    if job:
        job.remove()
        return {"message": "Scheduler stopped"}

    return {"message": "Scheduler not running"}
