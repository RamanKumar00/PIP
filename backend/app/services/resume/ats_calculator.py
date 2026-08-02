from typing import Dict, List, Tuple


def calculate_ats_score(
    sections_dict: Dict[str, str],
    skills_dict: Dict[str, List[str]],
    grammar_score: int,
    project_score: int,
    role_match_pct: int,
) -> Tuple[int, Dict[str, int], Dict[str, any], str]:
    """Calculate overall ATS score, category breakdown, strength metrics, and feedback.

    Returns:
        Tuple: (overall_ats_score, breakdown_dict, strength_meter_dict, overall_feedback)
    """
    # 1. Formatting Score (out of 20)
    # Check completeness of core sections
    formatting_score = 10
    detected_count = 0
    for sec_name in ["education", "experience", "projects", "skills", "certifications"]:
        if sections_dict.get(sec_name) and len(sections_dict[sec_name]) > 30:
            formatting_score += 2
            detected_count += 1
            
    # 2. Keywords & Skills Score (out of 20)
    # Scale based on role match and sheer volume of skills
    total_skills = sum(len(lst) for lst in skills_dict.values())
    keyword_score = 10
    if total_skills >= 12:
        keyword_score += 10
    elif total_skills >= 6:
        keyword_score += 5
    else:
        keyword_score += 2

    # Boost keyword score slightly based on target role match rate
    keyword_score = int(keyword_score * 0.7 + (role_match_pct / 100) * 6)
    keyword_score = min(max(keyword_score, 5), 20)

    # 3. Experience Score (out of 10)
    experience_score = 0
    exp_text = sections_dict.get("experience", "")
    if exp_text and len(exp_text) > 50:
        experience_score = 10
    elif exp_text:
        experience_score = 5

    # 4. Achievements & Certifications Score (out of 10)
    achievements_score = 0
    cert_text = sections_dict.get("certifications", "")
    if cert_text and len(cert_text) > 30:
        achievements_score = 10
    elif cert_text:
        achievements_score = 5

    # Calculate overall ATS Score (Sum of formatting, grammar, keywords, projects, exp, achievements)
    overall_ats = formatting_score + grammar_score + keyword_score + project_score + experience_score + achievements_score
    overall_ats = min(max(overall_ats, 10), 100)

    # 5. Compile Strength Meter
    readability = int((formatting_score / 20) * 100)
    professionalism = int((grammar_score / 20) * 100)
    technical_strength = int(((keyword_score + project_score) / 40) * 100)
    ats_compatibility = overall_ats

    # Quality label & star ratings
    if overall_ats >= 85:
        quality_label = "Excellent"
        stars = 5
    elif overall_ats >= 70:
        quality_label = "Good"
        stars = 4
    elif overall_ats >= 50:
        quality_label = "Fair"
        stars = 3
    else:
        quality_label = "Needs Improvement"
        stars = 2

    strength_meter = {
        "quality_label": quality_label,
        "stars": stars,
        "readability": readability,
        "professionalism": professionalism,
        "technical_strength": technical_strength,
        "ats_compatibility": ats_compatibility,
    }

    # 6. Detailed Score Breakdown mapping to schema
    breakdown = {
        "formatting_score": formatting_score,
        "grammar_score": grammar_score,
        "keyword_score": keyword_score,
        "project_score": project_score,
        "experience_score": experience_score,
        "achievements_score": achievements_score,
    }

    # 7. Generate text feedback summary
    feedback_segments = []
    if overall_ats >= 85:
        feedback_segments.append(
            "Outstanding resume! It contains well-structured sections, strong action-oriented project bullet points with measurable metrics, and a solid technical skill set matching your target role."
        )
    elif overall_ats >= 70:
        feedback_segments.append(
            "Your resume is in good shape. It has clear section structures and covers your primary skills. To push into the top tier, focus on converting generic project descriptions to quantitative, action-oriented lines and fixing any minor spelling or spacing blunders."
        )
    else:
        feedback_segments.append(
            "Your resume needs improvement. Several sections are either missing or lack descriptive details. Make sure you highlight technical projects, list your skills under dedicated headings, and include numeric metrics showing project impact."
        )

    if detected_count < 5:
        missing_sec = []
        for name in ["education", "experience", "projects", "skills", "certifications"]:
            if not sections_dict.get(name):
                missing_sec.append(name.capitalize())
        feedback_segments.append(
            f"Note: Some important sections are missing or extremely thin ({', '.join(missing_sec)}). Adding these will boost your ATS readability."
        )

    overall_feedback = " ".join(feedback_segments)

    return overall_ats, breakdown, strength_meter, overall_feedback
