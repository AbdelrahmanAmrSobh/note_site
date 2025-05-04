from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from dotenv import load_dotenv
from sqlmodel import Column, DateTime, Field, SQLModel
from uuid import UUID, uuid4

load_dotenv()

SESSION_EXPIRE_DAYS = int(os.environ["SESSION_EXPIRE_DAYS"])


def calculate_session_expire_datetime():
    return datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRE_DAYS)


class UserSession(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key=("user.id"))
    expire_at: Optional[datetime] = Field(
        default_factory=calculate_session_expire_datetime,
        sa_column=Column(DateTime(timezone=True)))
