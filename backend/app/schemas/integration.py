from pydantic import BaseModel


class ExportRequest(BaseModel):
    data: dict
    filename: str
