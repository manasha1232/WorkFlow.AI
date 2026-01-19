from fastapi import APIRouter
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(prefix="/api/email")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def summarize_text(text: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Summarize this in 2–3 lines:\n{text}"}]
    )
    return response.choices[0].message.content


@router.post("/summarize")
async def summarize_email(data: dict):
    text = data.get("text", "")
    summary = await summarize_text(text)
    return {"summary": summary}
