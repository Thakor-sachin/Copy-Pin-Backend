from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    pin = Column(String(10), unique=True, index=True, nullable=False)
    share_type = Column(String(10), nullable=False)  # "text" or "file"
    
    # Text-specific content
    content = Column(Text, nullable=True)
    
    # File-specific metadata
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def is_expired(self) -> bool:
        # Check if the share is expired relative to current UTC time
        now = datetime.utcnow()
        return now > self.expires_at
