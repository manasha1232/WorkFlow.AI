# routes/email_process_full.py
import base64, re, asyncio
from sqlalchemy.orm import Session
from db.models import ProcessedEmail
from utils.google_clients import get_gmail_service
from routes.email_clean import extract_clean_text
from routes.email_summarize import summarize_text
from routes.email_spam_filter import analyze_spam
from utils.google_actions import create_calendar_event, create_google_task

def run_async(fn, *args):
    if asyncio.iscoroutinefunction(fn):
        return asyncio.run(fn(*args))
    return fn(*args)


def extract_plaintext(msg):
    payload = msg.get("payload", {})
    parts = payload.get("parts", [])

    for p in parts:
        if p.get("mimeType") == "text/plain":
            data = p["body"].get("data")
            if data:
                try:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                except:
                    pass

    data = payload.get("body", {}).get("data")
    if data:
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        except:
            pass

    return msg.get("snippet", "")


def extract_event_date(text: str):
    patterns = [
        r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
        r"\b(\d{1,2}\s+\w+\s+\d{4})\b",
        r"on\s+(\d{1,2}\s+\w+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def process_single_email(msg_id, token, refresh_token, client_id, client_secret, user_id, db: Session):

    gmail = get_gmail_service(token, refresh_token, client_id, client_secret)
    raw_msg = gmail.users().messages().get(userId="me", id=msg_id, format="full").execute()

    raw_text = extract_plaintext(raw_msg)
    clean_text = extract_clean_text(raw_text)

    summary = run_async(summarize_text, clean_text)
    spam = run_async(analyze_spam, clean_text)

    is_spam = spam.get("is_spam", False)
    spam_reason = spam.get("reason")
    event_date = extract_event_date(clean_text)

    google_event_id = None
    google_task_id = None

    if event_date and not is_spam:
        google_event_id = create_calendar_event(token, refresh_token, client_id, client_secret, event_date, summary)

    elif not is_spam and any(w in summary.lower() for w in ["submit", "review", "finish", "send"]):
        google_task_id = create_google_task(token, refresh_token, client_id, client_secret, summary)

    # save to db
    exists = db.query(ProcessedEmail).filter_by(
        user_id=user_id, message_id=msg_id
    ).first()

    if not exists:
        entry = ProcessedEmail(
            user_id=user_id,
            message_id=msg_id,
            raw_text=raw_text,
            clean_text=clean_text,
            summary=summary,
            is_spam=is_spam,
            spam_reason=spam_reason,
            event_date=event_date,
            google_event_id=google_event_id,
            google_task_id=google_task_id
        )
        db.add(entry)
        db.commit()

    return {
        "message_id": msg_id,
        "summary": summary,
        "spam_analysis": spam,
        "event_date": event_date
    }
