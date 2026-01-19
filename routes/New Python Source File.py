from fastapi import APIRouter
from pydantic import BaseModel
from utils.gmail_service import get_gmail_service
from config.google_oauth import SCOPES

from routes.email_clean import extract_clean_text
from routes.email_summarize import summarize_text
from routes.email_spam_filter import analyze_spam

router = APIRouter(prefix="/api/email")


class ProcessFullRequest(BaseModel):
    token: str
    refresh_token: str
    client_id: str
    client_secret: str
    max_results: int = 10   # <-- user controls how many emails to fetch


@router.post("/process_full")
async def process_full(req: ProcessFullRequest):

    # Gmail service
    service = get_gmail_service(
        req.token,
        req.refresh_token,
        req.client_id,
        req.client_secret,
        SCOPES
    )

    # Fetch latest N emails
    results = service.users().messages().list(
        userId="me",
        maxResults=req.max_results,
        q="in:inbox"
    ).execute()

    messages = results.get("messages", [])
    processed = []

    for msg in messages:
        raw = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        # Clean
        clean_text = extract_clean_text(
            raw.get("snippet", "")  
        )

        # Summarize
        summary = await summarize_text(clean_text)

        # Spam detection
        spam = await analyze_spam(clean_text)

        # Priority scoring
        priority = compute_priority(clean_text, spam)

        processed.append({
            "message_id": msg["id"],
            "raw_text": raw.get("snippet", ""),
            "clean_text": clean_text,
            "summary": summary,
            "spam_analysis": spam,
            "priority_score": priority,
            "status": "processed"
        })

    return {"count": len(processed), "emails": processed}


def compute_priority(text: str, spam_data: dict):

    if spam_data.get("is_spam"):
        return 10

    score = 50
    text = text.lower()

    important = ["exam", "deadline", "meeting", "urgent", "result"]
    promo = ["offer", "discount", "sale", "promotion"]

    for w in important:
        if w in text:
            score += 30

    for w in promo:
        if w in text:
            score -= 20

    return max(0, min(score, 100))
