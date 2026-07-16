from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TextShareCreate(BaseModel):
    content: str = Field(..., description="Text content to be shared")

class ShareResponse(BaseModel):
    pin: str = Field(..., min_length=4, max_length=10)
    share_type: str
    expires_at: datetime
    file_name: Optional[str] = None
    file_size: Optional[int] = None

    class Config:
        from_attributes = True

class ShareContentResponse(BaseModel):
    pin: str = Field(..., min_length=4, max_length=10)
    share_type: str
    content: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: datetime

    class Config:
        from_attributes = True
