from typing import Any, Dict, List
import logging

# Use relative imports with defensive fallback for standalone execution
try:
    from .parser import extract_text_from_pdf
    from .cleaner import clean_text
    from .section_detector import detect_sections
    from .skill_extractor import extract_skills
    from .project_analyzer import analyze_projects
    from .grammar_checker import check_grammar_and_spelling
    from .role_matcher import match_role_skills
    from .ats_scoring_engine import ATSScoringEngine
    from .semantic_matcher import TFIDFSemanticMatcher
    from .recruiter_simulator import RecruiterSimulator
except ImportError:
    from parser import extract_text_from_pdf
    from cleaner import clean_text
    from section_detector import detect_sections
    from skill_extractor import extract_skills
    from project_analyzer import analyze_projects
    from grammar_checker import check_grammar_and_spelling
    from role_matcher import match_role_skills
    from ats_scoring_engine import ATSScoringEngine
    from semantic_matcher import TFIDFSemanticMatcher
    from recruiter_simulator import RecruiterSimulator

logger = logging.getLogger(__name__)


def generate_resume_report(pdf_bytes: bytes, target_role: str, target_requirements: str = "") -> Dict[str, Any]:
    """Execute the sequential pipeline analyzing resume PDF text using the redesigned engine.

    Args:
        pdf_bytes: PDF file contents.
        target_role: Preferred job title (e.g. Backend Developer).
        target_requirements: Text listing role specifications/requirements.

    Returns:
        Dict[str, Any]: Compiled analysis metrics dictionary.
    """
    try:
        # 1. Parse PDF
        raw_text = extract_text_from_pdf(pdf_bytes)
        if not raw_text.strip():
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

        # 7. Role Matching (keyword skills match)
        role_match = match_role_skills(skills, target_role)

        # 8. Compute Semantic Match Score
        if not target_requirements.strip():
            target_requirements = (
                f"Requires skills and proficiency in {target_role}. "
                "Key competencies include software engineering, architecture design, "
                "technical documentation, troubleshooting, systems design, testing, and Git version control."
            )

        semantic_matcher = TFIDFSemanticMatcher()
        semantic_res = semantic_matcher.match(cleaned_text, target_requirements)

        # 9. Run Modular ATS Scoring Engine
        scoring_data = {
            "sections": sections,
            "detected_skills": skills,
            "grammar_score": grammar_score,
            "grammar_issues": grammar_issues,
            "project_score": project_score,
            "project_analyses": project_analyses,
            "keyword_score": int((role_match["match_percentage"] / 100) * 20),
            "missing_skills": role_match["missing_skills"]
        }

        scoring_engine = ATSScoringEngine()
        diagnostics = scoring_engine.process(cleaned_text, scoring_data)

        # 10. Run Recruiter Simulation & Interview Prep
        sim_data = {
            "detected_skills": skills,
            "missing_skills": role_match["missing_skills"],
            "ats_score": diagnostics["ats_score"],
            "project_analyses": project_analyses
        }
        recruiter_sim = RecruiterSimulator()
        screening_report = recruiter_sim.simulate(cleaned_text, sim_data)

        # 11. Compile Unified suggestions
        compiled_suggestions = []
        for issue in grammar_issues:
            compiled_suggestions.append({
                "category": "grammar" if "grammar" in issue.get("issue_type", "grammar") else "spelling",
                "target": f"Found issue: '{issue.get('current')}'",
                "current": issue.get("current", ""),
                "suggested": issue.get("suggested", "N/A"),
                "rationale": issue.get("description", "Grammar correction.")
            })
        compiled_suggestions.extend(project_suggestions)
        compiled_suggestions.extend(diagnostics["suggestions"])

        # Deduplicate
        seen = set()
        unique_suggestions = []
        for s in compiled_suggestions:
            key = (s.get("current"), s.get("suggested"))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)

        # 12. Build coherent overall feedback
        ats_score = diagnostics["ats_score"]
        if ats_score >= 85:
            overall_feedback = (
                "Outstanding resume! It contains well-structured sections, strong action-oriented "
                "project bullet points with measurable metrics, and a solid technical skill set "
                "matching your target role."
            )
        elif ats_score >= 70:
            overall_feedback = (
                "Your resume is in good shape. It has clear section structures and covers your primary skills. "
                "To push into the top tier, focus on converting generic project descriptions to quantitative, "
                "action-oriented lines and fixing any minor spelling or spacing blunders."
            )
        else:
            overall_feedback = (
                "Your resume needs improvement. Several sections are either missing or lack descriptive details. "
                "Make sure you highlight technical projects, list your skills under dedicated headings, "
                "and include numeric metrics showing project impact."
            )

        # Append missing sections note if applicable
        detected_count = sum(
            1 for sec in ["education", "experience", "projects", "skills", "certifications"]
            if sections.get(sec) and len(sections[sec]) > 30
        )
        if detected_count < 5:
            missing_sec = [
                sec.capitalize()
                for sec in ["education", "experience", "projects", "skills", "certifications"]
                if not sections.get(sec) or len(sections.get(sec, "")) <= 30
            ]
            overall_feedback += (
                f" Note: Some important sections are missing or extremely thin ({', '.join(missing_sec)}). "
                "Adding these will boost your ATS readability."
            )

        # 13. Structure Analytics Data
        analytics_data = {
            "explanations": diagnostics["explanations"],
            "benchmark_comparison": {
                "gpa_met": True,
                "allowed_branch": True,
                "backlogs_checked": True
            }
        }

        return {
            "status": "completed",
            "ats_score": diagnostics["ats_score"],
            "detailed_breakdown": diagnostics["breakdown"],
            "strength_meter": diagnostics["strength_meter"],
            "overall_feedback": overall_feedback,
            "suggestions": unique_suggestions,
            "project_analyses": project_analyses,
            "detected_skills": skills,
            "missing_skills": role_match["missing_skills"],
            "missing_keywords": role_match["missing_skills"].copy(),
            "role_match": role_match,
            "parsed_text": cleaned_text,
            "recruiter_report": {
                "screening_decision": screening_report["screening_decision"],
                "strengths": screening_report["strengths"],
                "reservations": screening_report["reservations"]
            },
            "semantic_analysis": {
                "match_percentage": semantic_res["match_percentage"],
                "similarity_score": semantic_res["similarity_score"],
                "overlap_keywords": semantic_res["overlap_keywords"]
            },
            "interview_preparation": {
                "interview_readiness_score": screening_report["interview_readiness_score"],
                "interview_questions": screening_report["interview_questions"]
            },
            "analytics_data": analytics_data
        }

    except Exception as e:
        logger.exception("Pipeline failed during resume analysis")
        return {
            "status": "failed",
            "error_message": f"An unexpected error occurred during analysis: {str(e)}",
        }
