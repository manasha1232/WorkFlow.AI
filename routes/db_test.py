from fastapi import APIRouter
from db.database import get_db

router = APIRouter(prefix="/api/db")

@router.get("/ping")
async def ping_db():
    db = get_db()
    result = await db.test_ping.insert_one({"ping": True})
    count = await db.test_ping.count_documents({})
    return {
        "status": "ok",
        "inserted_id": str(result.inserted_id),
        "docs_in_collection": count
    }