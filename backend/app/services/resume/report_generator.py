from typing import Any, Dict, List

from app.services.resume.parser import extract_text_from_pdf
from app.services.resume.cleaner import clean_text
from app.services.resume.section_detector import detect_sections
from app.services.resume.skill_extractor import extract_skills
from app.services.resume.project_analyzer import analyze_projects
from app.services.resume.grammar_checker import check_grammar_and_spelling
from app.services.resume.role_matcher import match_role_skills
from app.services.resume.ats_calculator import calculate_ats_score


def generate_resume_report(pdf_bytes: bytes, target_role: str) -> Dict[str, Any]:
    """Execute the sequential pipeline analyzing resume PDF text.

    Args:
        pdf_bytes: PDF file contents.
        target_role: Preferred job title (e.g. Backend Developer).

    Returns:
        Dict[str, Any]: Compiled analysis metrics dictionary.
    """
    # 1. Parse PDF
    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        # Scanned PDF or blank
        return {
            "status": "failed",
            "error_message": "Could not extract text from the PDF file. Please ensure it is a digital PDF, not a scanned image.",
        }

    # 2. Clean Text
    cleaned_text = clean_text(raw_text)

    # 3. Detect Sections
    sections = detect_sections(cleaned_text)

    # 4. Extract Skills
    skills = extract_skills(cleaned_text)

    # 5. Project Quality Analysis
    project_score, project_analyses, project_suggestions = analyze_projects(
        sections.get("projects", "")
    )

    # 6. Grammar & Spelling Checks
    grammar_score, grammar_issues = check_grammar_and_spelling(cleaned_text)

    # 7. Role Matching
    role_match = match_role_skills(skills, target_role)

    # 8. ATS Score Calculations
    overall_ats, breakdown, strength_meter, overall_feedback = calculate_ats_score(
        sections,
        skills,
        grammar_score,
        project_score,
        role_match["match_percentage"],
    )

    # 9. Consolidate suggestions list matching SuggestionItem schema
    compiled_suggestions = []
    
    # Append spelling/grammar suggestions
    for issue in grammar_issues:
        compiled_suggestions.append(
            {
                "category": "grammar" if "grammar" in issue["issue_type"] else "spelling",
                "target": f"Found issue: '{issue['current']}'",
                "current": issue["current"],
                "suggested": issue["suggested"],
                "rationale": issue["description"],
            }
        )
    # Append project suggestions
    compiled_suggestions.extend(project_suggestions)

    # Combine missing keywords (missing target skills + missing project metrics suggestions)
    missing_keywords = role_match["missing_skills"].copy()

    return {
        "status": "completed",
        "ats_score": overall_ats,
        "detailed_breakdown": breakdown,
        "strength_meter": strength_meter,
        "overall_feedback": overall_feedback,
        "suggestions": compiled_suggestions,
        "project_analyses": project_analyses,
        "detected_skills": skills,
        "missing_skills": role_match["missing_skills"],
        "missing_keywords": missing_keywords,
        "role_match": role_match,
        "parsed_text": cleaned_text,
    }
