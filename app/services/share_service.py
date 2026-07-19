import os
import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.share import Share
from fastapi import UploadFile

def generate_unique_pin(db: Session) -> str:
    """
    Generates a unique 4-digit PIN code.
    Checks the database to ensure no active shares share this PIN.
    """
    for _ in range(100):  # avoid infinite loops in case of extreme fill rate
        # 4 digits code
        pin = "".join(random.choices(string.digits, k=4))
        
        # Check if active share with this PIN already exists
        now = datetime.now(timezone.utc)
        exists = db.query(Share).filter(Share.pin == pin, Share.expires_at > now).first()
        if not exists:
            return pin
            
    # Fallback to 5 digits if 4 digits are completely exhausted (unlikely for development)
    return "".join(random.choices(string.digits, k=5))

def create_text_share(db: Session, content: str) -> Share:
    """
    Stores a text share and returns the created Share entity with its PIN.
    """
    pin = generate_unique_pin(db)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=24)  # Default 24 hours expiry
    
    db_share = Share(
        pin=pin,
        share_type="text",
        content=content,
        created_at=now,
        expires_at=expires_at
    )
    
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share

def create_file_share(db: Session, file: UploadFile) -> Share:
    """
    Saves an uploaded file locally and registers it in the DB.
    """
    pin = generate_unique_pin(db)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=24)
    
    # Secure disk storage path
    # Avoid path traversal exploits by extracting only the basename and removing unsafe chars
    base_name = os.path.basename(file.filename) if file.filename else "file_upload"
    safe_filename = "".join(c for c in base_name if c.isalnum() or c in "._- ") or "file_upload"
    disk_filename = f"{pin}_{safe_filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, disk_filename)
    
    # Ensure upload folder exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Read file and write to disk with size check
    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE:
                    raise ValueError(f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB")
                buffer.write(chunk)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    db_share = Share(
        pin=pin,
        share_type="file",
        file_name=safe_filename,
        file_path=file_path,
        file_size=file_size,
        created_at=now,
        expires_at=expires_at
    )
    
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share

def get_active_share(db: Session, pin: str) -> Share:
    """
    Retrieves an active share by its PIN. 
    If a share is found but is expired, deletes it and returns None.
    """
    share = db.query(Share).filter(Share.pin == pin).first()
    if not share:
        return None
        
    if share.is_expired():
        # Clean up expired share
        delete_share(db, share)
        return None
        
    return share

def delete_share(db: Session, share: Share):
    """
    Deletes share record from DB and deletes local files if applicable.
    """
    if share.share_type == "file" and share.file_path:
        try:
            if os.path.exists(share.file_path):
                os.remove(share.file_path)
        except Exception as e:
            print(f"Error deleting file {share.file_path}: {e}")
            
    db.delete(share)
    db.commit()

def cleanup_expired_shares_job(db: Session) -> int:
    """
    Finds and deletes all expired shares.
    """
    now = datetime.now(timezone.utc)
    expired_shares = db.query(Share).filter(Share.expires_at <= now).all()
    count = len(expired_shares)
    
    for share in expired_shares:
        delete_share(db, share)
        
    return count
