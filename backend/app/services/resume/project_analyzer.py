import re
from typing import Dict, List, Tuple

# Lists of strong action verbs typically used in resumes
ACTION_VERBS = [
    "developed", "designed", "implemented", "optimized", "created", "built",
    "launched", "managed", "engineered", "integrated", "deployed", "reduced",
    "improved", "enhanced", "accelerated", "scaled", "orchestrated", "refactored",
    "authored", "automated", "executed", "formulated", "pioneered", "restructured"
]

# Simple mapping of common weak phrases to strong action-oriented, metrics-driven recommendations
SUGGESTION_MAPPING = [
    (
        r"(worked on|developed|built)\s+(an?|my)?\s*(e-?commerce|online shop|shopping)\s*(website|app|platform)?",
        "Developed a scalable FastAPI-based E-commerce platform using JWT Authentication, PostgreSQL, and REST APIs, improving API response times by 30%."
    ),
    (
        r"(built|developed|created)\s+(an?|my)?\s*(placement|college|campus|job)\s*(portal|website|system)?",
        "Engineered PlaceMentor AI, an automated recruitment readiness engine using spaCy, Celery background workers, and PostgreSQL, increasing profile match accuracy by 45%."
    ),
    (
        r"(made|created|designed)\s+(the|a)?\s*(database|db|schemas|tables)",
        "Designed and optimized a normalized PostgreSQL database schema with indexing and foreign keys constraints, reducing query retrieval latency by 40%."
    ),
    (
        r"(worked on|implemented|added)\s+(login|signup|auth|security)",
        "Implemented secure JWT Authentication and token refresh workflows using Passlib (Bcrypt) and FastAPI dependencies, enhancing session security and compliance."
    ),
    (
        r"(built|developed)\s+(an?|my)?\s*(chat-?bot|ai chat|messenger)",
        "Developed an interactive AI chatbot leveraging LangChain, Sentence Transformers, and OpenAI compatible APIs, achieving a 95% user inquiry resolution rate."
    ),
]


def analyze_projects(projects_text: str) -> Tuple[int, List[Dict[str, str]], List[Dict[str, str]]]:
    """Analyze the projects section text and output project scores and AI suggestions.

    Args:
        projects_text: Text block of the projects section.

    Returns:
        Tuple: (project_score, detailed_project_analyses, suggestion_list)
    """
    project_score = 0
    detailed_analyses = []
    suggestions = []

    if not projects_text:
        return 0, [], [
            {
                "category": "project",
                "target": "Projects Section",
                "current": "[Section Missing]",
                "suggested": "Add a dedicated 'Projects' section highlighting 2-3 technical projects.",
                "rationale": "Projects demonstrate hands-on application of programming skills to campus recruiters."
            }
        ]

    # Split into lines
    lines = [l.strip() for l in projects_text.split("\n") if l.strip()]
    
    # Identify project blocks (typically a header line followed by bullet points)
    # A simple parser groups text by line content
    current_project = "General Projects"
    project_bullets = {current_project: []}

    for line in lines:
        # If line looks like a title (short, no bullet indicator, no verbs)
        is_bullet = line.startswith(("-", "*", "•", "o", "1.", "2.", "3.", "4."))
        clean_line = re.sub(r"^[\-\*\•od\.]+\s*", "", line).strip()
        
        if not is_bullet and len(clean_line) < 40 and not any(v in clean_line.lower() for v in ACTION_VERBS[:5]):
            current_project = clean_name = clean_line
            project_bullets[current_project] = []
        else:
            project_bullets[current_project].append(clean_line)

    # Clean empty groups
    project_bullets = {k: v for k, v in project_bullets.items() if v}
    if not project_bullets:
        # Fallback to lines if no structured projects found
        project_bullets = {"Project 1": lines}

    total_bullets = 0
    bullets_with_metrics = 0
    bullets_with_verbs = 0

    for proj_title, bullets in project_bullets.items():
        proj_score = 50  # Base score for project definition
        proj_suggestions = []

        for bullet in bullets:
            total_bullets += 1
            bullet_lower = bullet.lower()

            # 1. Check for metrics (numbers, %, metrics keywords)
            has_metric = bool(re.search(r"\b\d+(\.\d+)?%?\b", bullet)) or any(
                m in bullet_lower for m in ["percent", "percentage", "lpa", "hours", "ms", "latency", "accuracy", "speedup", "seconds"]
            )
            if has_metric:
                bullets_with_metrics += 1
                proj_score += 15

            # 2. Check for action verbs
            has_verb = any(bullet_lower.startswith(v) or re.match(r"^\w+\s+" + v, bullet_lower) for v in ACTION_VERBS)
            if has_verb:
                bullets_with_verbs += 1
                proj_score += 10

            # 3. Check for specific weak phrases to generate suggestions
            for regex, replacement in SUGGESTION_MAPPING:
                if re.search(regex, bullet_lower):
                    suggestions.append(
                        {
                            "category": "project",
                            "target": proj_title,
                            "current": bullet,
                            "suggested": replacement,
                            "rationale": "Recruiters look for strong action verbs and quantitative metrics demonstrating impact."
                        }
                    )
                    proj_suggestions.append(f"Upgrade bullet point: '{bullet}' to reflect action and metrics.")

        # Cap project-specific score at 100
        proj_score = min(proj_score, 100)
        detailed_analyses.append(
            {
                "title": proj_title,
                "score": proj_score,
                "suggestions": proj_suggestions if proj_suggestions else ["✓ Project is well-described with good formatting."]
            }
        )

    # Calculate overall project section score (out of 20 points for ATS)
    # Average of project scores scaled to 20
    if detailed_analyses:
        avg_score = sum(p["score"] for p in detailed_analyses) / len(detailed_analyses)
        project_score = int((avg_score / 100) * 20)
    else:
        project_score = 0

    return project_score, detailed_analyses, suggestions
