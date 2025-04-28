from fastapi import HTTPException

from models import storage
from models.user import User
from schemas.delete import DeleteSchema


def delete_service(delete: DeleteSchema, user: User):
    request_dict = delete.model_dump(mode="python", exclude_none=True)

    object_type = request_dict.pop("object_type", None)
    object_id = request_dict.pop("object_id", None)

    if not object_type or not object_id:
        raise HTTPException(
            status_code=400,
            detail="object_type and object_id must be provided"
        )

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
