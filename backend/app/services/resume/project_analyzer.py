import re
from typing import Dict, List, Tuple

ACTION_VERBS = [
    "developed", "designed", "implemented", "optimized", "optimised", "created", "built",
    "launched", "managed", "engineered", "integrated", "deployed", "reduced",
    "improved", "enhanced", "accelerated", "scaled", "orchestrated", "refactored",
    "authored", "automated", "executed", "formulated", "pioneered", "restructured"
]

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


def _is_likely_title(line: str) -> bool:
    """Heuristic to detect if a line is a project title rather than a bullet."""
    stripped = line.lstrip("- *•▸►▶▷#>")
    if len(stripped) > 60:
        return False
    lower = stripped.lower()
    starts_with_verb = any(lower.startswith(v) for v in ACTION_VERBS)
    has_metric = bool(re.search(r"\b\d+\b", stripped))
    if starts_with_verb and has_metric:
        return False
    if stripped.isupper():
        return True
    words = stripped.split()
    if len(words) <= 4 and not starts_with_verb:
        return True
    return False


def analyze_projects(projects_text: str) -> Tuple[int, List[Dict[str, str]], List[Dict[str, str]]]:
    """Analyze the projects section text and output project scores and AI suggestions."""
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

    lines = [l.strip() for l in projects_text.split("\n") if l.strip()]

    current_project = "General Projects"
    project_bullets = {current_project: []}

    for line in lines:
        is_bullet = line.startswith(("-", "*", "•", "o", "1.", "2.", "3.", "4."))
        clean_line = re.sub(r"^[\-\*\•od\.]+\s*", "", line).strip()

        if not is_bullet and _is_likely_title(clean_line):
            current_project = clean_line
            project_bullets[current_project] = []
        else:
            project_bullets[current_project].append(clean_line)

    project_bullets = {k: v for k, v in project_bullets.items() if v}
    if not project_bullets:
        project_bullets = {"Project 1": lines}

    total_bullets = 0
    bullets_with_metrics = 0
    bullets_with_verbs = 0

    for proj_title, bullets in project_bullets.items():
        proj_score = 30
        proj_suggestions = []

        for bullet in bullets:
            total_bullets += 1
            bullet_lower = bullet.lower()

            has_metric = bool(re.search(r"\b\d+(\.\d+)?%?\b", bullet)) or any(
                m in bullet_lower for m in ["percent", "percentage", "lpa", "hours", "ms", "latency", "accuracy", "speedup", "seconds", "throughput", "reduced", "improved", "increased"]
            )
            if has_metric:
                bullets_with_metrics += 1
                proj_score += 15

            has_verb = any(bullet_lower.startswith(v) or re.match(r"^\w+\s+" + v, bullet_lower) for v in ACTION_VERBS)
            if has_verb:
                bullets_with_verbs += 1
                proj_score += 10

            matched_specific = False
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
                    matched_specific = True
                    break

            if not matched_specific and (not has_verb or not has_metric):
                missing_parts = []
                if not has_verb:
                    missing_parts.append("strong action verbs")
                if not has_metric:
                    missing_parts.append("measurable metrics/results")
                
                suggestions.append(
                    {
                        "category": "project",
                        "target": proj_title,
                        "current": bullet,
                        "suggested": "Structure this bullet to start with a strong action verb (e.g. 'Optimized', 'Designed') and quantify the impact with a number or percentage.",
                        "rationale": f"Bullet point lacks {' and '.join(missing_parts)}."
                    }
                )
                proj_suggestions.append(f"Upgrade bullet point: '{bullet}' to reflect action and metrics.")

        proj_score = min(proj_score, 100)
        detailed_analyses.append(
            {
                "title": proj_title,
                "score": proj_score,
                "suggestions": proj_suggestions if proj_suggestions else ["✓ Project is well-described with good formatting."]
            }
        )

    if detailed_analyses:
        avg_score = sum(p["score"] for p in detailed_analyses) / len(detailed_analyses)
        project_score = int((avg_score / 100) * 20)
    else:
        project_score = 0

    return project_score, detailed_analyses, suggestions
