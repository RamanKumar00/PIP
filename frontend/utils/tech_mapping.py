# Centralized mapping configuration for the Learning Platform
# Allows adding/updating/removing technologies simply by updating this list.

# Default search URL template when an exact match is not found
DEFAULT_SEARCH_URL_TEMPLATE = "https://www.geeksforgeeks.org/?s={query}"

# Each technology configuration has:
# - "display_name": The official display name
# - "url": The exact tutorial URL (can be from GeeksforGeeks or any other provider)
# - "aliases": List of alias names that should resolve to this technology
TECH_CONFIGS = [
    {
        "display_name": "Python",
        "url": "https://www.geeksforgeeks.org/python-programming-language/",
        "aliases": ["py", "python3", "python programming"]
    },
    {
        "display_name": "Java",
        "url": "https://www.geeksforgeeks.org/java/",
        "aliases": ["java programming", "jdk"]
    },
    {
        "display_name": "C++",
        "url": "https://www.geeksforgeeks.org/c-plus-plus/",
        "aliases": ["cpp", "c plus plus"]
    },
    {
        "display_name": "JavaScript",
        "url": "https://www.geeksforgeeks.org/javascript/",
        "aliases": ["js", "javascript programming", "es6"]
    },
    {
        "display_name": "React",
        "url": "https://www.geeksforgeeks.org/reactjs-tutorial-basic-concepts/",
        "aliases": ["reactjs", "react.js"]
    },
    {
        "display_name": "FastAPI",
        "url": "https://www.geeksforgeeks.org/fastapi/",
        "aliases": ["fast api"]
    },
    {
        "display_name": "Docker",
        "url": "https://www.geeksforgeeks.org/docker-tutorial/",
        "aliases": ["docker containers"]
    },
    {
        "display_name": "PostgreSQL",
        "url": "https://www.geeksforgeeks.org/postgresql-tutorial/",
        "aliases": ["postgres", "pgsql"]
    },
    {
        "display_name": "Machine Learning",
        "url": "https://www.geeksforgeeks.org/machine-learning/",
        "aliases": ["ml", "machinelearning"]
    },
    {
        "display_name": "Data Structures & Algorithms",
        "url": "https://www.geeksforgeeks.org/data-structures/",
        "aliases": ["dsa", "data structures", "algorithms", "ds", "algo"]
    },
    {
        "display_name": "System Design",
        "url": "https://www.geeksforgeeks.org/system-design-tutorial/",
        "aliases": ["systemdesign", "sd", "high level design", "hld", "lld"]
    },
    {
        "display_name": "Kubernetes",
        "url": "https://www.geeksforgeeks.org/kubernetes-tutorial/",
        "aliases": ["k8s", "k8", "kube"]
    },
    {
        "display_name": "AWS",
        "url": "https://www.geeksforgeeks.org/aws-tutorial/",
        "aliases": ["amazon web services", "amazon aws"]
    },
    {
        "display_name": "Redis",
        "url": "https://www.geeksforgeeks.org/redis-tutorial/",
        "aliases": ["redis cache"]
    },
    {
        "display_name": "TypeScript",
        "url": "https://www.geeksforgeeks.org/typescript/",
        "aliases": ["ts"]
    },
    {
        "display_name": "HTML",
        "url": "https://www.geeksforgeeks.org/html-tutorial/",
        "aliases": ["html5"]
    },
    {
        "display_name": "CSS",
        "url": "https://www.geeksforgeeks.org/css-tutorial/",
        "aliases": ["css3"]
    },
    {
        "display_name": "Node.js",
        "url": "https://www.geeksforgeeks.org/nodejs-tutorial/",
        "aliases": ["node", "nodejs"]
    },
    {
        "display_name": "MongoDB",
        "url": "https://www.geeksforgeeks.org/mongodb-tutorial/",
        "aliases": ["mongo"]
    },
    {
        "display_name": "Git",
        "url": "https://www.geeksforgeeks.org/git-tutorial/",
        "aliases": ["version control"]
    },
    {
        "display_name": "GitHub",
        "url": "https://www.geeksforgeeks.org/introduction-to-github/",
        "aliases": ["gh"]
    },
    {
        "display_name": "Django",
        "url": "https://www.geeksforgeeks.org/django-tutorial/",
        "aliases": ["python django"]
    },
    {
        "display_name": "Flask",
        "url": "https://www.geeksforgeeks.org/flask-tutorial-introduction/",
        "aliases": ["python flask"]
    },
    {
        "display_name": "Spring Boot",
        "url": "https://www.geeksforgeeks.org/spring-boot/",
        "aliases": ["springboot", "spring"]
    },
    {
        "display_name": "Go",
        "url": "https://www.geeksforgeeks.org/golang-tutorial-learn-go-programming-language/",
        "aliases": ["golang"]
    },
    {
        "display_name": "Rust",
        "url": "https://www.geeksforgeeks.org/rust-programming-language-tutorial/",
        "aliases": ["rustlang"]
    },
]

def get_resolution_map():
    """Returns a lookup dictionary mapping lowercase names/aliases to their respective URLs."""
    res_map = {}
    for item in TECH_CONFIGS:
        url = item["url"]
        display_name = item["display_name"]
        
        # Primary name
        res_map[display_name.lower().strip()] = url
        
        # Aliases
        for alias in item.get("aliases", []):
            res_map[alias.lower().strip()] = url
            
    return res_map

def get_autocomplete_suggestions():
    """Returns list of display names for autocomplete suggestions."""
    return [item["display_name"] for item in TECH_CONFIGS]
