from fastapi import APIRouter
from pydantic import BaseModel

from routes.email_clean import extract_clean_text
from routes.email_summarize import summarize_text
from routes.email_spam_filter import analyze_spam

router = APIRouter(prefix="/api/email")

class EmailProcessRequest(BaseModel):
    text: str

@router.post("/process")
async def process_email(request: EmailProcessRequest):
    raw = request.text

    # CLEAN
    clean = extract_clean_text(raw)

    # SUMMARIZE
    summary = await summarize_text(clean)

    # SPAM CHECK
    spam = await analyze_spam(clean)

    # PRIORITY SCORE
    priority = compute_priority(clean, spam)

    return {
        "clean_text": clean,
        "summary": summary,
        "spam_analysis": spam,
        "priority_score": priority
    }

def compute_priority(text: str, spam_data: dict):

    text_lower = text.lower()

    if spam_data.get("is_spam"):
        return 10

    score = 50

    important_words = [
        "exam", "deadline", "schedule", "urgent",
        "meeting", "appointment", "result"
    ]

    promo_words = ["offer", "discount", "sale", "promotion"]

    for word in important_words:
        if word in text_lower:
            score += 30

    for word in promo_words:
        if word in text_lower:
            score -= 20

    return max(0, min(score, 100))
