from fastapi import HTTPException
from uuid import UUID

from models import storage
from models.user import User
from schemas.view import ObjectType


def delete_service(object_type: ObjectType, object_id: UUID, user: User):
    target_object = storage.get(object_type, id=object_id)

    if not target_object:
        raise HTTPException(
            status_code=404,
            detail=f"{object_type} with id {object_id} not found"
        )

    if (hasattr(target_object, "owner") and target_object.owner == user) or target_object == user:

        storage.delete(target_object)
        storage.save()

        return {"detail": f"{object_type.value.capitalize()} deleted successfully"}

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to delete this object"
    )
