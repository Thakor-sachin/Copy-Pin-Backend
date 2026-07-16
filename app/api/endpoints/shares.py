import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.share import TextShareCreate, ShareResponse, ShareContentResponse
from app.services import share_service

router = APIRouter()

@router.post("/text", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
def share_text(payload: TextShareCreate, db: Session = Depends(get_db)):
    """
    Upload a text snippet and receive a 4-digit PIN.
    """
    if not payload.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Content cannot be empty"
        )
    return share_service.create_text_share(db, payload.content)

@router.post("/file", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
def share_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a file and receive a 4-digit PIN.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Filename is missing"
        )
    try:
        db_share = share_service.create_file_share(db, file)
        return db_share
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to save file: {str(e)}"
        )

@router.get("/{pin}", response_model=ShareContentResponse)
def get_share_metadata(pin: str, db: Session = Depends(get_db)):
    """
    Retrieve text content or file metadata for a given active PIN.
    """
    share = share_service.get_active_share(db, pin)
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Active PIN not found or expired"
        )
    return share

@router.get("/{pin}/download")
def download_file_payload(pin: str, db: Session = Depends(get_db)):
    """
    Download the file payload associated with a file PIN.
    """
    share = share_service.get_active_share(db, pin)
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="PIN not found or expired"
        )
        
    if share.share_type != "file":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This PIN points to a text share, not a file share"
        )
        
    if not share.file_path or not os.path.exists(share.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Associated file not found on disk"
        )
        
    return FileResponse(
        path=share.file_path,
        filename=share.file_name,
        media_type="application/octet-stream"
    )
