from sqlalchemy.orm import Session
from db.models import User, ProcessedEmail


# ----------------------------
# CREATE OR RETURN USER
# ----------------------------
def get_or_create_user(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ----------------------------
# UPDATE USER PROFILE
# ----------------------------
def update_user_profile(db: Session, user_id: int, full_name: str, username: str):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    user.full_name = full_name
    user.username = username

    db.commit()
    db.refresh(user)
    return user


# ----------------------------
# CHECK IF MESSAGE PROCESSED
# ----------------------------
def is_message_processed(db: Session, user_id: int, message_id: str) -> bool:
    return db.query(ProcessedEmail).filter_by(
        user_id=user_id,
        message_id=message_id
    ).first() is not None
