from typing import List, Optional, TYPE_CHECKING

from bcrypt import checkpw, gensalt, hashpw
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID, uuid4

from models.note import UserRole

if TYPE_CHECKING:
    from models.note import NoteUserLink


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default_factory=uuid4, nullable=False, primary_key=True)
    email: str = Field(index=True, max_length=50, nullable=False, unique=True)
    username: str = Field(index=True, max_length=50,
                          nullable=False, unique=True)
    pw: str = Field(max_length=128, nullable=False)

    # Relationships
    note_links: List["NoteUserLink"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"})

    @property
    def password(self):
        print(f"Attempt to read password field on user {self.id}")
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_password: str):
        hashed = hashpw(plain_password.encode('utf-8'), gensalt())
        self.pw = hashed.decode('utf-8')

    def checkpw(self, plain_password: str):
        return checkpw(plain_password.encode('utf-8'), self.pw.encode('utf-8'))

    def __eq__(self, user):
        if not isinstance(user, User):
            return False
        return user.id == self.id

    @property
    def notes(self):
        return [note_link.note for note_link in self.note_links]

    def to_dict(self):
        owner_notes = []
        observer_notes = []
        editor_notes = []

        for note_link in self.note_links:
            if note_link.role == UserRole.OWNER:
                owner_notes.append(note_link.note.to_dict())
            elif note_link.role == UserRole.OBSERVER:
                observer_notes.append(note_link.note.to_dict())
            elif note_link.role == UserRole.EDITOR:
                editor_notes.append(note_link.note.to_dict())

        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "notes": {
                "editor": editor_notes,
                "observer": observer_notes,
                "owner": owner_notes,
            }
        }
