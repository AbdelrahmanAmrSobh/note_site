from fastapi import APIRouter, Depends
from uuid import UUID

from models.user import User
from schemas.view import ObjectType
from services.auth import verify_user
from services.view import view_service

router = APIRouter(prefix="/view")


@router.get("/{object_type}/{object_id}", status_code=200)
def view_object(object_type: ObjectType, object_id: UUID, user: User = Depends(verify_user)):
    return view_service(object_type, object_id, user)
