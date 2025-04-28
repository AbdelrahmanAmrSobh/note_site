from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    email: EmailStr
    password: str
    username: str


class EditorSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    note_id: UUID
    username: str


class ObserverSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    note_id: UUID
    username: str
