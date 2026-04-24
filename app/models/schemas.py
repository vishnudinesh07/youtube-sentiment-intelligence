from pydantic import BaseModel, Field


class AnalyseRequest(BaseModel):
    url: str
    limit: int = Field(default=100, ge=1, le=500)