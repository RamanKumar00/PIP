import re
from typing import Dict, List

SKILL_DICTIONARY = {
    "programming": [
        "Python", "Java", "C++", "C#", "JavaScript", "TypeScript",
        "Golang", "Rust", "Ruby", "PHP", "HTML", "CSS", "Kotlin",
        "Swift", "Scala", "Bash", "Perl", "SQL", "C", "Go"
    ],
    "backend": [
        "FastAPI", "Flask", "Django", "Node.js", "Node", "Express",
        "Spring Boot", "Spring", "Ruby on Rails", "Rails", "ASP.NET",
        "Laravel", "GraphQL", "REST APIs", "REST API", "gRPC", "Celery"
    ],
    "frontend": [
        "React", "Streamlit", "Angular", "Vue.js", "Vue", "Next.js",
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


def _make_skill_pattern(skill: str) -> str:
    """Build a regex pattern that handles special chars like +, #, . correctly."""
    escaped = re.escape(skill.lower())
    # Special case: skill "C" must NOT match the 'c' inside C++ or C#
    if skill.lower() == "c":
        return r"(?<![a-z0-9])c(?![a-z0-9+#])"
    return r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])"


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Scan resume text and extract skills categorized by domain."""
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

    text_lower = text.lower()

    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            pattern = re.compile(_make_skill_pattern(skill))
            if pattern.search(text_lower):
                clean_name = skill
                extracted[category].append(clean_name)

    # De-duplicate lists
    for k in extracted:
        extracted[k] = list(sorted(set(extracted[k])))

    return extracted
