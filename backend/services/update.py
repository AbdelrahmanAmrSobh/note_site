from fastapi import HTTPException

from models import storage
from models.note import datetime_now_utc, UserRole
from models.user import User
from schemas.update import UpdateSchema


def update_service(update: UpdateSchema, user: User):
    request_dict = update.model_dump(mode="python", exclude_none=True)

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

    link = storage.get("link", note_id=object_id, user_id=user.id)

    if target_object == user or (link and link.role != UserRole.OBSERVER):
        for key, value in request_dict.items():
            if not hasattr(target_object, key) and key != "password":
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{key}' does not exist on {object_type}"
                )
            if key == "email" and storage.get("user", email=value):
                raise HTTPException(
                    status_code=400,
                    detail="Email is already used by another user."
                )
            if key == "username" and storage.get("user", username=value):
                raise HTTPException(
                    status_code=400,
                    detail="Username is already used by another user."
                )

        for key, value in request_dict.items():
            setattr(target_object, key, value)

        if hasattr(target_object, "updated_at"):
            target_object.updated_at = datetime_now_utc()

        storage.new(target_object)
        storage.save()

        return {"detail": "Object updated successfully"}

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to modify this object"
    )
