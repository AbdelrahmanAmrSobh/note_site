from fastapi import APIRouter, Depends

from models.user import User
from schemas.user import EditorSchema, ObserverSchema
from services.auth import verify_user
from services.remove import remove_editor_service, remove_observer_service

router = APIRouter(prefix="/remove")


@router.put("/editor", status_code=200)
def remove_editor(editor: EditorSchema, user: User = Depends(verify_user)):
    return remove_editor_service(editor, user)


@router.put("/observer", status_code=200)
def remove_observer(observer: ObserverSchema, user: User = Depends(verify_user)):
    return remove_observer_service(observer, user)
