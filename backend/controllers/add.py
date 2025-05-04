from fastapi import APIRouter, Depends

from models.user import User
from schemas.user import EditorSchema, ObserverSchema
from services.add import add_editor_service, add_observer_service
from services.auth import verify_user

router = APIRouter(prefix="/add")


@router.put("/editor", status_code=200)
def add_editor(editor: EditorSchema, user: User = Depends(verify_user)):
    return add_editor_service(editor, user)


@router.put("/observer", status_code=200)
def add_observer(observer: ObserverSchema, user: User = Depends(verify_user)):
    return add_observer_service(observer, user)
