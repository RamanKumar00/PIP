from typing import Dict, List

# Core skills database for target industry roles
ROLE_SKILLS_DATABASE = {
    "Backend Developer": [
        "Python", "FastAPI", "PostgreSQL", "Docker", "Redis", 
        "GraphQL", "REST APIs", "Git", "CI/CD", "SQL"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "HTML", "CSS", 
        "Tailwind CSS", "Next.js", "Redux", "Git", "Bootstrap"
    ],
    "Full Stack Developer": [
        "Python", "JavaScript", "React", "FastAPI", "PostgreSQL", 
        "HTML", "CSS", "Docker", "Git", "REST APIs"
    ],
    "Data Scientist": [
        "Python", "SQL", "PostgreSQL", "Numpy", "Pandas", 
        "Scikit-Learn", "Machine Learning", "Data Analysis", "Git"
    ],
    "Data Analyst": [
        "SQL", "Python", "Power BI", "Data Analysis", "Pandas", "MySQL"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", 
        "Git", "Bash", "Nginx", "Docker Compose"
    ],
    "Product Manager": [
        "SQL", "Jira", "Agile", "Data Analysis", "GitHub"
    ],
}


def match_role_skills(detected_skills_dict: Dict[str, List[str]], target_role: str) -> Dict[str, any]:
    """Compare extracted skills against requirements for the target role.

    Args:
        detected_skills_dict: Extracted categorized skills dict.
        target_role: Preferred job role title (e.g. Backend Developer).

    Returns:
        Dict: Match percentage, matched skills, and missing skills.
    """
    # Normalize target role matching
    role = target_role
    if role not in ROLE_SKILLS_DATABASE:
        # Fallback to nearest match or default
        matched_roles = [r for r in ROLE_SKILLS_DATABASE if r.lower() in role.lower() or role.lower() in r.lower()]
        role = matched_roles[0] if matched_roles else "Software Engineer"

    # If role falls back to something outside DB, use Full Stack as default list
    required_skills = ROLE_SKILLS_DATABASE.get(role, ROLE_SKILLS_DATABASE["Full Stack Developer"])

    # Flatten all detected skills (lowercase for accurate comparison)
    flat_detected = []
    for skills_list in detected_skills_dict.values():
        flat_detected.extend([s.lower() for s in skills_list])

    matched = []
    missing = []

    for req_skill in required_skills:
        if req_skill.lower() in flat_detected:
            matched.append(req_skill)
        else:
            missing.append(req_skill)

    # Calculate match rate percentage
    total_req = len(required_skills)
    match_percentage = int((len(matched) / total_req) * 100) if total_req > 0 else 100

    return {
        "role_name": role,
        "match_percentage": match_percentage,
        "matched_skills": matched,
        "missing_skills": missing,
    }
