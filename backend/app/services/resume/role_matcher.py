from typing import Dict, List

# Expanded core skills database for target industry roles
ROLE_SKILLS_DATABASE = {
    "Backend Developer": [
        "Python", "FastAPI", "PostgreSQL", "Docker", "Redis",
        "GraphQL", "REST APIs", "Git", "CI/CD", "SQL", "Node.js", "MongoDB", "Kafka", "RabbitMQ"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "HTML", "CSS",
        "Tailwind CSS", "Next.js", "Redux", "Git", "Bootstrap", "Vue.js", "Webpack", "Sass"
    ],
    "Full Stack Developer": [
        "Python", "JavaScript", "React", "FastAPI", "PostgreSQL",
        "HTML", "CSS", "Docker", "Git", "REST APIs", "Node.js", "MongoDB", "TypeScript"
    ],
    "Data Scientist": [
        "Python", "SQL", "PostgreSQL", "Numpy", "Pandas",
        "Scikit-Learn", "Machine Learning", "Data Analysis", "Git", "TensorFlow", "PyTorch", "Matplotlib"
    ],
    "Data Analyst": [
        "SQL", "Python", "Power BI", "Data Analysis", "Pandas", "MySQL", "Excel", "Tableau", "Statistics"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform",
        "Git", "Bash", "Nginx", "Docker Compose", "Jenkins", "Ansible", "Prometheus", "Linux"
    ],
    "Product Manager": [
        "SQL", "Jira", "Agile", "Data Analysis", "GitHub", "Figma", "Notion", "Roadmapping"
    ],
    "Machine Learning Engineer": [
        "Python", "TensorFlow", "PyTorch", "Scikit-Learn", "Docker",
        "Kubernetes", "MLflow", "SQL", "Git", "FastAPI", "AWS", "Pandas", "Numpy"
    ],
    "Mobile Developer": [
        "Swift", "Kotlin", "React Native", "Flutter", "Java", "Git", "Firebase", "iOS", "Android"
    ],
    "Software Engineer": [
        "Python", "Java", "C++", "Git", "SQL", "Docker", "REST APIs", "Data Structures", "Algorithms"
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
    role = target_role.strip()

    # Exact match first
    if role not in ROLE_SKILLS_DATABASE:
        # Try case-insensitive exact match
        for db_role in ROLE_SKILLS_DATABASE:
            if db_role.lower() == role.lower():
                role = db_role
                break
        else:
            # Try substring match
            matched_roles = [
                r for r in ROLE_SKILLS_DATABASE
                if r.lower() in role.lower() or role.lower() in r.lower()
            ]
            if matched_roles:
                role = matched_roles[0]
            else:
                role = "Software Engineer"  # Safe generic fallback

    required_skills = ROLE_SKILLS_DATABASE.get(role, ROLE_SKILLS_DATABASE["Software Engineer"])

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

    total_req = len(required_skills)
    match_percentage = int((len(matched) / total_req) * 100) if total_req > 0 else 100

    return {
        "role_name": role,
        "match_percentage": match_percentage,
        "matched_skills": matched,
        "missing_skills": missing,
    }
