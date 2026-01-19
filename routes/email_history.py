from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import ProcessedEmail, User

router = APIRouter(prefix="/api/email/history")


# ---------------------------------------------------------
# Helper: Convert DB object -> Clean JSON for frontend
# ---------------------------------------------------------
def serialize_email(email: ProcessedEmail):
    return {
        "id": email.id,
        "message_id": email.message_id,
        "raw_text": email.raw_text,
        "clean_text": email.clean_text,
        "summary": email.summary,
        "spam": {
            "is_spam": email.is_spam,
            "reason": email.spam_reason
        },
        "event": {
            "date": email.event_date,
            "google_event_id": email.google_event_id
        },
        "task": {
            "google_task_id": email.google_task_id
        },
        "created_at": str(email.created_at)
    }


# ---------------------------------------------------------
# 1️⃣ GET FULL HISTORY FOR A USER
# ---------------------------------------------------------
@router.get("/")
def get_history(user_email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    emails = db.query(ProcessedEmail)\
        .filter(ProcessedEmail.user_id == user.id)\
        .order_by(ProcessedEmail.created_at.desc())\
        .all()

    return [serialize_email(e) for e in emails]


# ---------------------------------------------------------
# 2️⃣ GET SINGLE EMAIL BY ID
# ---------------------------------------------------------
@router.get("/{email_id}")
def get_email(email_id: int, user_email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    email = db.query(ProcessedEmail).filter(
        ProcessedEmail.id == email_id,
        ProcessedEmail.user_id == user.id
    ).first()

    if not email:
        raise HTTPException(404, "Email not found or does not belong to user")

    return serialize_email(email)


# ---------------------------------------------------------
# 3️⃣ DELETE ONE EMAIL
# ---------------------------------------------------------
@router.delete("/{email_id}")
def delete_email(email_id: int, user_email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    email = db.query(ProcessedEmail).filter(
        ProcessedEmail.id == email_id,
        ProcessedEmail.user_id == user.id
    ).first()

    if not email:
        raise HTTPException(404, "Email not found")

    db.delete(email)
    db.commit()

    return {"message": "Deleted successfully"}


# ---------------------------------------------------------
# 4️⃣ DELETE ALL FOR USER
# ---------------------------------------------------------
@router.delete("/all")
def delete_all(user_email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    db.query(ProcessedEmail).filter(
        ProcessedEmail.user_id == user.id
    ).delete()

    db.commit()
    return {"message": "All email history cleared"}


# ---------------------------------------------------------
# 5️⃣ CLEANUP OLD EMAILS (KEEP SYSTEM LIGHT)
# ---------------------------------------------------------
@router.delete("/cleanup/old")
def cleanup_old(user_email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")

    old_items = db.query(ProcessedEmail).filter(
        ProcessedEmail.user_id == user.id
    ).order_by(ProcessedEmail.created_at.asc()).limit(100).all()

    for item in old_items:
        db.delete(item)

    db.commit()
    return {"deleted": len(old_items)}
