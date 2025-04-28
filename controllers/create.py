from fastapi import APIRouter, Depends

from models.user import User
from schemas.note import NoteSchema
from schemas.user import UserSchema
from services.auth import verify_user
from services.create import create_note, create_user

router = APIRouter(prefix="/create")


@router.post("/user", status_code=201)
def user(user: UserSchema):
    return create_user(user)


@router.post("/note", status_code=201)
def note(note: NoteSchema, user: User = Depends(verify_user)):
    return create_note(note, user)
