from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel
from uuid import UUID, uuid4

load_dotenv()

SECRET_KEY = os.environ["NOTE_SECRET_KEY"]

fernet = Fernet(SECRET_KEY)


def encrypt_data(data: str):
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(token: str):
    return fernet.decrypt(token.encode()).decode()


if TYPE_CHECKING:
    from models.user import User


def datetime_now_utc():
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    OBSERVER = "observer"


class NoteUserLink(SQLModel, table=True):
    note_id: UUID = Field(foreign_key="note.id",
                          nullable=False, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id",
                          nullable=False, primary_key=True)
    role: UserRole = Field(default=UserRole.OWNER, nullable=False)

    # Relationships
    note: "Note" = Relationship(back_populates="user_links")
    user: "User" = Relationship(back_populates="note_links")


class Note(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default_factory=uuid4, nullable=False, primary_key=True)
    title: str = Field(max_length=256, nullable=False)
    details_encrypted: str = Field(max_length=4096, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime_now_utc,
        sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(
        default_factory=datetime_now_utc,
        sa_column=Column(DateTime(timezone=True)))

    # Relationships
    user_links: List["NoteUserLink"] = Relationship(
        back_populates="note", sa_relationship_kwargs={"cascade": "all, delete"})

    @property
    def details(self):
        return decrypt_data(self.details_encrypted)

    @details.setter
    def details(self, value: str):
        self.details_encrypted = encrypt_data(value)

    @property
    def owner(self):
        return next((link.user for link in self.user_links if link.role == UserRole.OWNER), None)

    @property
    def editors(self):
        return [link.user for link in self.user_links if link.role == UserRole.EDITOR]

    @property
    def observers(self):
        return [link.user for link in self.user_links if link.role == UserRole.OBSERVER]

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "details": self.details
        }
