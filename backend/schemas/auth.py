from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AuthSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., max_length=32)
