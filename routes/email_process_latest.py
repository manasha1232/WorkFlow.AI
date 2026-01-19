# routes/email_process_latest.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from utils.gmail_service import get_gmail_service
from config.google_oauth import SCOPES

# use the helper modules we created above
from routes.email_clean import extract_clean_text
from routes.email_summarize import summarize_text
from routes.email_spam_filter import analyze_spam

router = APIRouter(prefix="/api/email")

class TokensModel(BaseModel):
    token: str
    refresh_token: str
    client_id: str
    client_secret: str

@router.post("/process_latest")
def process_latest_email(tokens: TokensModel) -> Dict[str, Any]:
    """
    Fetch the latest email from inbox and run the full pipeline:
    clean -> summarize -> spam -> priority
    """
    # 1) connect to Gmail
    try:
        service = get_gmail_service(
            tokens.token,
            tokens.refresh_token,
            tokens.client_id,
            tokens.client_secret,
            SCOPES
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Gmail service: {e}")

    # 2) list latest messages (inbox)
    try:
        results = service.users().messages().list(userId="me", maxResults=1, q="in:inbox").execute()
        messages = results.get("messages", [])
        if not messages:
            return {"status": "no_messages", "message": "No messages in inbox"}
        latest = messages[0]
        message_id = latest.get("id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list messages: {e}")

    # 3) fetch full message (use 'full' or 'raw' depending on parser)
    try:
        raw_msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch message {message_id}: {e}")

    # 4) clean
    clean_text = extract_clean_text(raw_msg)

    # 5) summarize
    try:
        summary = summarize_text(clean_text)
    except Exception as e:
        summary = f"[summary_error] {e}"

    # 6) spam analysis
    try:
        spam_data = analyze_spam(clean_text)
    except Exception as e:
        spam_data = {"is_spam": False, "category": "error", "reason": str(e)}

    # 7) priority computation
    priority = compute_priority(clean_text, spam_data)

    return {
        "status": "processed",
        "message_id": message_id,
        "clean_text": clean_text,
        "summary": summary,
        "spam_analysis": spam_data,
        "priority_score": priority,
    }


def compute_priority(text: str, spam_data: dict) -> int:
    if spam_data.get("is_spam"):
        return 10  # low priority for spam

    score = 40  # base

    keywords_high = ["exam", "deadline", "urgent", "appointment", "meeting", "otp", "verification", "bank", "invoice"]
    for w in keywords_high:
        if w in (text or "").lower():
            score += 20

    keywords_low = ["offer", "sale", "promo", "discount", "unsubscribe"]
    for w in keywords_low:
        if w in (text or "").lower():
            score -= 15

    # clamp
    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return score
