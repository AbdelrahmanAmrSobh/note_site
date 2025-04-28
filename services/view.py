from fastapi import HTTPException
from uuid import UUID

from models import storage
from models.user import User
from schemas.view import ObjectType


def view_service(object_type: ObjectType, object_id: UUID, user: User):
    target_object = storage.get(object_type, id=object_id)
    if not target_object:
        raise HTTPException(
            status_code=404,
            detail=f"{object_type.value.capitalize()} with ID {object_id} not found"
        )

    link = storage.get("link", note_id=object_id, user_id=user.id)

    if target_object == user or link:
        return target_object.to_dict()
    raise HTTPException(
        status_code=403,
        detail="You do not have permission to view this object"
    )
