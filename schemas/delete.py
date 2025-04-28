from enum import Enum
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ObjectType(str, Enum):
    NOTE = "note"
    USER = "user"


class DeleteSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    object_id: UUID
    object_type: ObjectType
