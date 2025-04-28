from pydantic import BaseModel, ConfigDict, EmailStr


class AuthSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    email: EmailStr
    password: str
