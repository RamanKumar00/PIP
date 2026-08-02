import os
import traceback
from pathlib import Path
from app.core.cel_app import celery_app
from app.core.database import SessionLocal
from app.models.resume import Resume, ResumeAnalysis
from app.services.resume.report_generator import generate_resume_report


@celery_app.task(name="app.worker.tasks.analyze_resume_task")
def analyze_resume_task(resume_id: str, target_role: str) -> bool:
    """Background task executing the resume intelligence pipeline.

    Args:
        resume_id: Unique UUID of the uploaded resume.
        target_role: Job title target for match calculations.

    Returns:
        bool: True if completed successfully, False otherwise.
    """
    db = SessionLocal()
    try:
        import uuid
        try:
            resume_uuid = uuid.UUID(str(resume_id))
        except (ValueError, TypeError):
            return False

        # Fetch the resume record
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        if not resume:
            return False

        # Retrieve or initialize the analysis record
        analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_uuid).first()
        if not analysis:
            analysis = ResumeAnalysis(resume_id=resume.id)
            db.add(analysis)
        
        # Update status to processing
        analysis.status = "processing"
        db.commit()

        # Locate the uploaded file path (stored in backend/uploads/{user_id}/)
        upload_dir = Path("uploads") / str(resume.user_id)
        file_path = upload_dir / resume.stored_filename

        if not file_path.exists():
            analysis.status = "failed"
            analysis.error_message = f"File not found on server storage: {resume.stored_filename}"
            db.commit()
            return False

        # Read PDF binary bytes
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        # Execute modular AI Pipeline
        report = generate_resume_report(pdf_bytes, target_role)

        if report.get("status") == "failed":
            analysis.status = "failed"
            analysis.error_message = report.get("error_message", "Unknown extraction error.")
        else:
            analysis.status = "completed"
            analysis.ats_score = report["ats_score"]
            analysis.grammar_score = report["detailed_breakdown"]["grammar_score"]
            analysis.formatting_score = report["detailed_breakdown"]["formatting_score"]
            analysis.keyword_score = report["detailed_breakdown"]["keyword_score"]
            analysis.project_score = report["detailed_breakdown"]["project_score"]
            analysis.experience_score = report["detailed_breakdown"]["experience_score"]
            analysis.role_match_score = report["role_match"]["match_percentage"]

            # Save nested structures in a single copy-assigned dictionary
            analysis.overall_feedback = report["overall_feedback"]
            
            db_breakdown = report["detailed_breakdown"].copy()
            db_breakdown["strength_meter"] = report["strength_meter"]
            db_breakdown["project_analyses"] = report["project_analyses"]
            db_breakdown["role_match"] = report["role_match"]
            
            analysis.detailed_breakdown = db_breakdown
            analysis.suggestions = report["suggestions"]
            analysis.missing_skills = report["missing_skills"]
            analysis.missing_keywords = report["missing_keywords"]
            analysis.detected_skills = report["detected_skills"]
            analysis.parsed_text = report["parsed_text"]

            # Set error message to None
            analysis.error_message = None

            # Also update user's profile with detected resume URL and merge skills if profile exists
            # (We will keep this flexible so that the profile stays synchronized)
            profile = resume.user.profile
            if profile:
                profile.resume_url = f"/uploads/{resume.user_id}/{resume.stored_filename}"

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        # Log tracebacks
        err_msg = f"Unexpected pipeline exception: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        
        # Save fail states to the database
        try:
            import uuid
            r_uuid = uuid.UUID(str(resume_id))
            analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == r_uuid).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = f"Pipeline execution failed: {str(e)}"
                db.commit()
        except Exception:
            pass
        return False
    finally:
        db.close()
