from fastapi import APIRouter, Depends

from models.user import User
from schemas.update import UpdateSchema
from services.auth import verify_user
from services.update import update_service

router = APIRouter()


@router.patch("/update", status_code=200)
def update_object(update: UpdateSchema, user: User = Depends(verify_user)):
    return update_service(update, user)
