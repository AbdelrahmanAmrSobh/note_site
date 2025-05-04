from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID

from schemas.view import ObjectType


class UpdateSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    object_id: UUID
    object_type: ObjectType

    title: str | None = Field(default=None, max_length=256)
    details: str | None = Field(default=None, max_length=1096)

    email: EmailStr | None = Field(default=None, max_length=50)
    password: str | None = Field(default=None, max_length=32)
    username: str | None = Field(default=None, max_length=50)
