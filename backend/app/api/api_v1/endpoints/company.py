import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight
from app.models.resume import Resume
from app.repositories.profile import profile_repo
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyRoleCreate,
    CompanyRoleResponse,
    EligibilityCheckResponse
)
from app.services.eligibility.engine import evaluate_eligibility

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new company. (Admin Only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required.",
        )
        
    db_company = db.query(Company).filter(Company.name == company_in.name).first()
    if db_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A company with this name already exists.",
        )

    company = Company(**company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.post("/{company_id}/roles", response_model=CompanyRoleResponse, status_code=status.HTTP_201_CREATED)
def create_role_for_company(
    company_id: uuid.UUID,
    role_in: CompanyRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Add a job placement role, setting up eligibility rules and skill weights. (Admin Only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required.",
        )

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target company not found.",
        )

    # 1. Create Role
    role = CompanyRole(
        company_id=company_id,
        title=role_in.title,
        ctc=role_in.ctc,
        description=role_in.description,
        application_link=role_in.application_link,
        difficulty=role_in.difficulty,
        selection_rounds=role_in.selection_rounds,
        hiring_pattern=role_in.hiring_pattern,
        expected_oa_pattern=role_in.expected_oa_pattern,
        technical_interview_topics=role_in.technical_interview_topics,
        hr_interview_topics=role_in.hr_interview_topics,
        interview_experience=role_in.interview_experience,
        preparation_resources=role_in.preparation_resources,
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    # 2. Add Eligibility Rule
    if role_in.eligibility_rule:
        rule = EligibilityRule(
            role_id=role.id,
            **role_in.eligibility_rule.dict()
        )
        db.add(rule)

    # 3. Add Skill Weights
    if role_in.skill_weights:
        for sw_in in role_in.skill_weights:
            sw = CompanySkillWeight(
                role_id=role.id,
                **sw_in.dict()
            )
            db.add(sw)

    db.commit()
    db.refresh(role)
    return role


@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve all active placement companies and their associated roles.
    """
    companies = (
        db.query(Company)
        .filter(Company.is_active == True)
        .order_by(Company.name.asc())
        .all()
    )
    return companies


@router.get("/roles/{role_id}/check", response_model=EligibilityCheckResponse)
def check_role_eligibility(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Evaluate the student's profile & resume parameters against target role criteria.
    """
    # 1. Fetch Company Role
    role = db.query(CompanyRole).filter(CompanyRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company job placement role not found.",
        )

    # 2. Fetch Student Profile
    profile = profile_repo.get_by_user_id(db, user_id=current_user.id)

    # 3. Fetch Student Active Resume
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_active == True)
        .first()
    )

    # 4. Execute matching engine calculation
    evaluation = evaluate_eligibility(
        profile=profile,
        active_resume=resume,
        rule=role.eligibility_rule,
        skill_weights=role.skill_weights,
        db=db,
    )
    return evaluation
