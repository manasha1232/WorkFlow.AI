from fastapi import APIRouter
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/api/email")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def analyze_spam(text: str) -> dict:
    """
    Forces AI to return perfect JSON.
    """

    prompt = f"""
You must return ONLY valid JSON. No explanation, no extra words.

Analyze the email text below and output JSON in this structure:

{{
  "is_spam": true/false,
  "category": "spam" | "important" | "social",
  "reason": "short explanation"
}}

Email text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract AI raw output
    result = response.choices[0].message.content.strip()

    # SAFETY FIX → If JSON is wrapped inside ``` ```
    if result.startswith("```"):
        result = result.strip("`").strip()
        if result.startswith("json"):
            result = result[4:].strip()

    # FINAL SAFE PARSE
    try:
        return json.loads(result)
    except:
        # fallback in case AI misbehaves
        return {
            "is_spam": False,
            "category": "unknown",
            "reason": "AI returned invalid JSON"
        }


@router.post("/check_spam")
async def check_spam_api(data: dict):
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}

    result = await analyze_spam(text)
    return {"analysis": result}
