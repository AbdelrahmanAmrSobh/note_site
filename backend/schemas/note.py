from pydantic import BaseModel, ConfigDict, Field


class NoteSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    title: str = Field(..., max_length=256)
    details: str = Field(..., max_length=1096)
