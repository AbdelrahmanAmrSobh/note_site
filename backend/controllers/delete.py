from fastapi import APIRouter, Depends
from uuid import UUID

from models.user import User
from schemas.view import ObjectType
from services.auth import verify_user
from services.delete import delete_service

router = APIRouter()


@router.delete("/delete/{object_type}/{object_id}", status_code=200)
def delete_object(object_type: ObjectType, object_id: UUID, user: User = Depends(verify_user)):
    return delete_service(object_type, object_id, user)
