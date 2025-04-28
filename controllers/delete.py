from fastapi import APIRouter, Depends

from models.user import User
from schemas.delete import DeleteSchema
from services.auth import verify_user
from services.delete import delete_service

router = APIRouter()


@router.delete("/delete", status_code=200)
def delete_object(delete: DeleteSchema, user: User = Depends(verify_user)):
    return delete_service(delete, user)
