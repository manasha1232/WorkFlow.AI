# db/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    full_name = Column(String, nullable=True)
    username = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    processed_emails = relationship("ProcessedEmail", back_populates="user")



class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(String, index=True)

    raw_text = Column(Text)
    clean_text = Column(Text)
    summary = Column(Text)

    is_spam = Column(Boolean, default=False)
    spam_reason = Column(String)

    event_date = Column(String)
    google_event_id = Column(String, nullable=True)
    google_task_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="processed_emails")
