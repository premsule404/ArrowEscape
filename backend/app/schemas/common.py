from pydantic import BaseModel
from typing import Optional, Any

class ErrorDetail(BaseModel):
    code: str
    message: str

class APIResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
