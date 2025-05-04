from fastapi import HTTPException

from models import storage
from models.note import Note, NoteUserLink, UserRole
from models.user import User
from schemas.note import NoteSchema
from schemas.user import UserSchema


def create_note(note_data: NoteSchema, user: User):
    new_note = Note(title=note_data.title)
    new_note.details = note_data.details
    storage.new(new_note)
    storage.save()

    note_user_link = NoteUserLink(
        note_id=new_note.id,
        user_id=user.id,
        role=UserRole.OWNER
    )
    storage.new(note_user_link)
    storage.save()

    return {"detail": "Note created successfully."}


def create_user(user_data: UserSchema):
    email = user_data.email.lower().strip()
    username = user_data.username.strip()

    if storage.get(User, email=email):
        raise HTTPException(
            status_code=400, detail="Email already registered.")
    if storage.get(User, username=username):
        raise HTTPException(status_code=400, detail="Username already taken.")

    new_user = User(email=email, username=username)
    new_user.password = user_data.password

    storage.new(new_user)
    storage.save()

    return {"detail": "User registered successfully."}
