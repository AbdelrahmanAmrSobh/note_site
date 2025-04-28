from pydantic import BaseModel, ConfigDict


class NoteSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    title: str
    details: str
