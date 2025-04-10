# project/app/schemas/website_parse.py
from pydantic import BaseModel
from typing import Optional

class WebsiteParseRequest(BaseModel):
    url: str
    max_depth: int = 2
    format: str = "graphml"

class WebsiteParseResponse(BaseModel):
    task_id: str

class ParseStatusResponse(BaseModel):
    status: str
    progress: int
    result: Optional[str] = None
    error: Optional[str] = None