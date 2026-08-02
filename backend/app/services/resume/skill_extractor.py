import re
from typing import Dict, List

# Define the master skill categories and keywords
SKILL_DICTIONARY = {
    "programming": [
        "Python", "Java", "C\\+\\+", "C\\#", "JavaScript", "TypeScript", 
        "Golang", "Rust", "Ruby", "PHP", "HTML", "CSS", "Kotlin", 
        "Swift", "Scala", "Bash", "Perl", "SQL"
    ],
    "backend": [
        "FastAPI", "Flask", "Django", "Node\\.js", "Node", "Express", 
        "Spring Boot", "Spring", "Ruby on Rails", "Rails", "ASP\\.NET", 
        "Laravel", "GraphQL", "REST APIs", "REST API", "gRPC", "Celery"
    ],
    "frontend": [
        "React", "Streamlit", "Angular", "Vue\\.js", "Vue", "Next\\.js", 
        "Tailwind CSS", "Tailwind", "jQuery", "Bootstrap", "Sass", "Redux", "React Native"
    ],
    "database": [
        "PostgreSQL", "SQLite", "MySQL", "Redis", "MongoDB", "Cassandra", 
        "DynamoDB", "MariaDB", "Oracle", "SQL Server", "Elasticsearch", "Firebase"
    ],
    "tools": [
        "Docker", "Git", "GitHub", "GitLab", "CI/CD", "Jenkins", 
        "Kubernetes", "Docker Compose", "Terraform", "Ansible", 
        "Prometheus", "Grafana", "Jira", "Nginx", "Apache"
    ],
    "cloud": [
        "AWS", "Amazon Web Services", "GCP", "Google Cloud", 
        "Azure", "Heroku", "Render", "Vercel", "Netlify", "DigitalOcean"
    ],
}


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Scan resume text and extract skills categorized by domain.

    Args:
        text: Cleaned resume text.

    Returns:
        Dict[str, List[str]]: Dictionary with lists of matched skill strings.
    """
    extracted = {
        "programming": [],
        "backend": [],
        "frontend": [],
        "database": [],
        "tools": [],
        "cloud": [],
    }

    if not text:
        return extracted

    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()

    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            # Escape and create word boundary pattern
            pattern = re.compile(r"\b" + skill.lower() + r"\b")
            if pattern.search(text_lower):
                # Save display name rather than lowercase
                # Format clean names (remove regex escapes)
                clean_name = skill.replace("\\", "")
                extracted[category].append(clean_name)

    # Special Case-Sensitive Matches for "C" and "Go"
    # Ensure they are matched as independent capital letters or words, avoiding matches on "c" in cgpa.
    if re.search(r"\bC\b", text) and "C" not in extracted["programming"]:
        extracted["programming"].append("C")
    if re.search(r"\bGo\b", text) and "Golang" not in extracted["programming"] and "Go" not in extracted["programming"]:
        extracted["programming"].append("Go")

    # De-duplicate lists
    for k in extracted:
        extracted[k] = list(sorted(set(extracted[k])))

    return extracted
