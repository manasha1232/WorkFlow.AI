from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.crud import get_or_create_user, update_user_profile

router = APIRouter(prefix="/api/user", tags=["User"])


# -------------------------------
# Get user profile by email
# -------------------------------
@router.get("/profile")
def get_profile(email: str, db: Session = Depends(get_db)):
    user = get_or_create_user(db, email)
    return {
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
    }


# -------------------------------
# Update full name + username
# -------------------------------
@router.post("/update")
def update_profile(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    full_name = data.get("full_name")
    username = data.get("username")

    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    user = update_user_profile(db, email, full_name, username)

    return {
        "message": "Profile updated successfully",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username
        }
    }
