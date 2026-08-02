from typing import Any, Dict, List, Optional
from app.models.profile import Profile
from app.models.resume import Resume
from app.models.company import EligibilityRule, CompanySkillWeight


def evaluate_eligibility(
    profile: Optional[Profile],
    active_resume: Optional[Resume],
    rule: Optional[EligibilityRule],
    skill_weights: List[CompanySkillWeight],
    db: Optional[Any] = None,
) -> Dict[str, Any]:
    """Evaluate student profile and resume compatibility against target role eligibility rules.

    Returns:
        Dict: is_eligible, overall_score, breakdown, reasons, missing_skills, estimated_effort.
    """
    reasons = []
    missing_skills = []
    estimated_weeks = 0.0

    # Fallbacks if rules aren't defined
    if not rule:
        return {
            "is_eligible": True,
            "overall_score": 100,
            "breakdown": {
                "cgpa_score": 100,
                "branch_score": 100,
                "backlog_score": 100,
                "skills_score": 100,
                "resume_score": 100,
            },
            "reasons": [],
            "missing_skills": [],
            "estimated_effort": "0 weeks",
        }

    # --- 1. CGPA Scoring (20% weight) ---
    cgpa_score = 100
    if not profile or profile.cgpa is None:
        cgpa_score = 0
        reasons.append("Academic profile details (CGPA) are missing.")
    elif rule.min_cgpa > 0:
        if float(profile.cgpa) >= rule.min_cgpa:
            cgpa_score = 100
        else:
            cgpa_score = int((float(profile.cgpa) / rule.min_cgpa) * 100)
            reasons.append(
                f"CGPA is too low: {float(profile.cgpa):.2f} (Required: ≥ {rule.min_cgpa:.2f})"
            )

    # --- 2. Branch Check (15% weight) ---
    branch_score = 100
    if rule.allowed_branches and len(rule.allowed_branches) > 0:
        if not profile or not profile.branch:
            branch_score = 0
            reasons.append("Branch selection is missing from academic profile.")
        else:
            allowed_branches_lower = [b.lower() for b in rule.allowed_branches]
            if profile.branch.lower() in allowed_branches_lower:
                branch_score = 100
            else:
                branch_score = 0
                reasons.append(
                    f"Branch '{profile.branch}' is not eligible. Allowed branches: {', '.join(rule.allowed_branches)}"
                )

    # --- 3. Backlogs Check (15% weight) ---
    backlog_score = 100
    if profile:
        backlogs = profile.backlogs or 0
        if backlogs <= rule.max_active_backlogs:
            backlog_score = 100
        else:
            backlog_score = 0
            reasons.append(
                f"Active backlogs exceed limit: {backlogs} (Allowed: ≤ {rule.max_active_backlogs})"
            )
    else:
        backlog_score = 0
        reasons.append("Academic profile backlogs count is missing.")

    # --- 4. Resume Score Check (20% weight) ---
    resume_score = 100
    ats_rating = 0
    if not active_resume or not active_resume.analysis:
        resume_score = 0
        reasons.append("No active resume upload or resume analysis has not completed.")
    elif rule.min_resume_match_score > 0:
        ats_rating = active_resume.analysis.ats_score
        if ats_rating >= rule.min_resume_match_score:
            resume_score = 100
        else:
            resume_score = int((ats_rating / rule.min_resume_match_score) * 100)
            reasons.append(
                f"Resume ATS rating is low: {ats_rating}% (Required: ≥ {rule.min_resume_match_score}%)"
            )

    # --- 5. Skill Weights Match Check (30% weight) ---
    skill_score = 100
    student_skills = set()
    
    # 1. Fetch skills from UserSkillProgress database (closed-loop mastered skills)
    has_db_skills = False
    if db and profile:
        from app.models.roadmap import UserSkillProgress
        progress_records = db.query(UserSkillProgress).filter(
            UserSkillProgress.user_id == profile.user_id,
            (UserSkillProgress.confidence_score >= 80) | (UserSkillProgress.mastery_level == "Mastered")
        ).all()
        if progress_records:
            has_db_skills = True
            for rec in progress_records:
                student_skills.add(rec.skill_name.strip().lower())

    # 2. Fallback to active resume parsed skills if no db progress records exist yet
    if not has_db_skills and active_resume and active_resume.analysis and active_resume.analysis.detected_skills:
        for skill_list in active_resume.analysis.detected_skills.values():
            if skill_list:
                for s in skill_list:
                    student_skills.add(s.strip().lower())

    if skill_weights and len(skill_weights) > 0:
        total_weight = sum(sw.importance for sw in skill_weights)
        matched_weight = 0
        
        for sw in skill_weights:
            skill_lower = sw.skill_name.lower()
            if skill_lower in student_skills:
                matched_weight += sw.importance
            else:
                # Add to missing skills list
                missing_skills.append({
                    "skill_name": sw.skill_name,
                    "importance": sw.importance,
                    "required_level": sw.required_level
                })
                
                # Check if it's a critical missing skill
                if sw.importance >= 4:
                    reasons.append(
                        f"Missing critical skill: {sw.skill_name} (Required Importance: {'High' if sw.importance == 4 else 'Critical'})"
                    )
                
                # Calculate effort contribution:
                # Importance 5 = 2 weeks, 4 = 1.5 weeks, 3 = 1 week, 2/1 = 0.5 weeks
                if sw.importance == 5:
                    estimated_weeks += 2.0
                elif sw.importance == 4:
                    estimated_weeks += 1.5
                elif sw.importance == 3:
                    estimated_weeks += 1.0
                else:
                    estimated_weeks += 0.5
                    
        skill_score = int((matched_weight / total_weight) * 100) if total_weight > 0 else 100
    else:
        skill_score = 100

    # --- 6. Aggregate Overall Weighted Score ---
    overall_score = int(
        0.20 * cgpa_score
        + 0.15 * branch_score
        + 0.15 * backlog_score
        + 0.30 * skill_score
        + 0.20 * resume_score
    )

    # --- 7. Resolve Final Eligibility Status ---
    # User is eligible ONLY IF they meet ALL mandatory criteria (no warning reasons)
    is_eligible = len(reasons) == 0

    # --- 8. Resolve Estimated Effort Text ---
    if is_eligible:
        estimated_effort = "0 weeks"
    else:
        # Check if there is an academic criteria failure that cannot be solved by self-study
        has_academic_gap = False
        if profile and profile.cgpa is not None and rule.min_cgpa > 0:
            if float(profile.cgpa) < rule.min_cgpa:
                has_academic_gap = True
        if rule.allowed_branches and profile and profile.branch:
            if profile.branch.lower() not in [b.lower() for b in rule.allowed_branches]:
                has_academic_gap = True
                
        if has_academic_gap:
            estimated_effort = "Academic Gap (Requires off-campus/exception approval)"
        elif estimated_weeks == 0.0:
            estimated_effort = "1 week (Minor resume optimizations)"
        else:
            # Round off to range
            low_range = int(estimated_weeks)
            high_range = int(estimated_weeks + 1)
            if low_range == high_range or low_range == 0:
                estimated_effort = f"{high_range} week" + ("s" if high_range > 1 else "")
            else:
                estimated_effort = f"{low_range}-{high_range} weeks"

    return {
        "is_eligible": is_eligible,
        "overall_score": overall_score,
        "breakdown": {
            "cgpa_score": cgpa_score,
            "branch_score": branch_score,
            "backlog_score": backlog_score,
            "skills_score": skill_score,
            "resume_score": resume_score,
        },
        "reasons": reasons,
        "missing_skills": missing_skills,
        "estimated_effort": estimated_effort,
    }
