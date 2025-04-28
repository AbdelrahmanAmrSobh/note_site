from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

from schemas.view import ObjectType


class UpdateSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    object_id: UUID
    object_type: ObjectType

    title: str | None = None
    details: str | None = None

    email: EmailStr | None = None
    password: str | None = None
    phone: str | None = None
    username: str | None = None
