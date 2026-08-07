import os
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pathlib import Path

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.repositories.profile import profile_repo
from app.schemas.resume import (
    ResumeResponse, 
    ResumeAnalysisResponse, 
    AnalysisStatusResponse
)
from app.worker.tasks import analyze_resume_task

router = APIRouter()

# Base upload folder path definition
UPLOAD_DIR = Path("uploads")


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Upload a PDF resume. Increments version count and dispatches background analysis.
    """
    # 1. Validate file format
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents are supported.",
        )

    # 2. Determine target role
    if not target_role:
        # Check student profile preferred_role
        profile = profile_repo.get_by_user_id(db, user_id=current_user.id)
        if profile and profile.preferred_role:
            target_role = profile.preferred_role
        else:
            target_role = "Software Engineer"  # Default fallback

    # 3. Create upload directory
    user_upload_dir = UPLOAD_DIR / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    # 4. Version Calculation (De-activate previous active uploads)
    previous_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    version = len(previous_resumes) + 1
    
    for r in previous_resumes:
        r.is_active = False
        db.add(r)

    # 5. Save file to storage
    file_uuid = uuid.uuid4()
    stored_filename = f"resume_v{version}_{file_uuid.hex}.pdf"
    file_path = user_upload_dir / stored_filename
    
    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            # Read and write chunks
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)
                file_size += len(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to server: {str(e)}",
        )

    # Validate file size (max 5MB)
    if file_size > 5 * 1024 * 1024:
        # Remove partial file
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 5MB.",
        )

    # 6. Database record entries
    resume_record = Resume(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_size=file_size,
        mime_type="application/pdf",
        version=version,
        is_active=True,
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    # Initialize analysis block
    analysis_record = ResumeAnalysis(
        resume_id=resume_record.id,
        status="pending",
    )
    db.add(analysis_record)
    db.commit()

    # 7. Dispatch asynchronous background task
    # (Since celery is asynchronous, this returns immediately)
    analyze_resume_task.delay(str(resume_record.id), target_role)

    # Prepare response
    return resume_record


@router.get("/latest", response_model=ResumeResponse)
def get_latest_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve the latest active resume upload and its analysis report.
    """
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resumes uploaded yet.",
        )
    return resume


@router.get("/history", response_model=List[ResumeResponse])
def get_resume_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve the version history of all uploaded resumes.
    """
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.version.desc())
        .all()
    )
    return resumes


@router.get("/{resume_id}/status", response_model=AnalysisStatusResponse)
def get_analysis_status(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Check the real-time parsing status of a specific resume (used for polling).
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )

    analysis = resume.analysis
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not initialized.",
        )

    return {
        "resume_id": resume.id,
        "status": analysis.status,
        "ats_score": analysis.ats_score if analysis.status == "completed" else None,
        "error_message": analysis.error_message,
    }


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume_by_id(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve full analysis report of a specific resume upload by ID.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )
    return resume


@router.put("/{resume_id}/activate", response_model=ResumeResponse)
def activate_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Make a specific resume version the active one.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )
    # Deactivate all others
    db.query(Resume).filter(Resume.user_id == current_user.id).update({Resume.is_active: False})
    # Activate this one
    resume.is_active = True
    db.commit()
    db.refresh(resume)
    return resume
