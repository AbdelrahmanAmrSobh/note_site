from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID


class UserSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., max_length=32)
    username: str = Field(..., max_length=50)


class EditorSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    note_id: UUID
    username: str = Field(..., max_length=50)


class ObserverSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    note_id: UUID
    username: str = Field(..., max_length=50)
