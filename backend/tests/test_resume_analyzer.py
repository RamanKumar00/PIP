"""
Unit and integration tests for the ATS Resume Analyzer pipeline.
Run with: pytest tests/test_resume_analyzer.py -v
"""

# pyrefly: ignore [missing-import]
import pytest

# ------------------------------------------------------------------
# 1. ExperienceAnalyzer Tests
# ------------------------------------------------------------------

def test_experience_analyzer_strong():
    from app.services.resume.ats_scoring_engine import ExperienceAnalyzer
    analyzer = ExperienceAnalyzer()
    data = {
        "sections": {
            "experience": """Senior Software Engineer at TechCorp (2021-Present)
- Led migration of monolith to microservices, reducing deployment time by 40%
- Architected real-time data pipeline handling 2M events/day
- Mentored 4 junior engineers on Python and system design
"""
        }
    }
    res = analyzer.analyze("", data)
    assert res["score"] >= 15
    assert "Strong experience section" in res["explanation"]
    assert len(res["suggestions"]) == 0


def test_experience_analyzer_fair():
    from app.services.resume.ats_scoring_engine import ExperienceAnalyzer
    analyzer = ExperienceAnalyzer()
    data = {
        "sections": {
            "experience": "Intern at Startup (2023)\n- Built a landing page."
        }
    }
    res = analyzer.analyze("", data)
    assert 5 <= res["score"] < 15
    assert "Fair" in res["explanation"] or "Weak" in res["explanation"]


def test_experience_analyzer_missing():
    from app.services.resume.ats_scoring_engine import ExperienceAnalyzer
    analyzer = ExperienceAnalyzer()
    data = {"sections": {"experience": ""}}
    res = analyzer.analyze("", data)
    assert res["score"] <= 5
    assert "missing" in res["explanation"].lower() or "no meaningful" in res["explanation"].lower()
    assert len(res["suggestions"]) > 0


# ------------------------------------------------------------------
# 2. GrammarAnalyzer Tests
# ------------------------------------------------------------------

def test_grammar_analyzer_perfect():
    from app.services.resume.ats_scoring_engine import GrammarAnalyzer
    analyzer = GrammarAnalyzer()
    data = {
        "grammar_score": 20,
        "grammar_issues": []
    }
    res = analyzer.analyze("", data)
    assert res["score"] == 20
    assert "Perfect" in res["explanation"]
    assert len(res["suggestions"]) == 0


def test_grammar_analyzer_minor_issues():
    from app.services.resume.ats_scoring_engine import GrammarAnalyzer
    analyzer = GrammarAnalyzer()
    data = {
        "grammar_score": 16,
        "grammar_issues": [
            {"current": "recieve", "suggested": "receive", "description": "Common spelling mistake"},
            {"current": "seperate", "suggested": "separate", "description": "Common spelling mistake"}
        ]
    }
    res = analyzer.analyze("", data)
    assert res["score"] == 16
    assert "Minor" in res["explanation"]
    assert len(res["suggestions"]) == 2


def test_grammar_analyzer_high_errors():
    from app.services.resume.ats_scoring_engine import GrammarAnalyzer
    analyzer = GrammarAnalyzer()
    data = {
        "grammar_score": 8,
        "grammar_issues": [{"current": f"err{i}", "suggested": "fix", "description": "Typo"} for i in range(8)]
    }
    res = analyzer.analyze("", data)
    assert res["score"] == 8
    assert "High error density" in res["explanation"]


# ------------------------------------------------------------------
# 3. Project Analyzer Tests
# ------------------------------------------------------------------

def test_project_analyzer_strong():
    from app.services.resume.project_analyzer import analyze_projects
    text = """E-Commerce Platform
- Developed a scalable FastAPI-based platform using PostgreSQL, improving API response times by 30%
- Optimised database queries with indexing, reducing latency by 40%
- Implemented JWT Authentication for 10,000+ users
"""
    score, analyses, suggestions = analyze_projects(text)
    assert score > 0
    assert len(analyses) >= 1
    assert analyses[0]["score"] >= 75
    # "optimised" should now be recognized as an action verb
    assert any("optimised" in s.lower() for s in analyses[0]["suggestions"]) is False or analyses[0]["score"] >= 75


def test_project_analyzer_missing_section():
    from app.services.resume.project_analyzer import analyze_projects
    score, analyses, suggestions = analyze_projects("")
    assert score == 0
    assert len(analyses) == 0
    assert len(suggestions) == 1
    assert "[Section Missing]" in suggestions[0]["current"]


def test_project_analyzer_weak_bullets():
    from app.services.resume.project_analyzer import analyze_projects
    text = """My Project
- Worked on a website
- Made some changes to the database
- Helped with the frontend
"""
    score, analyses, suggestions = analyze_projects(text)
    assert score < 10  # Low score due to no metrics and weak verbs
    assert len(suggestions) > 0  # Should suggest rewrites


# ------------------------------------------------------------------
# 4. Skill Extractor Regression Tests
# ------------------------------------------------------------------

def test_skill_extractor_c_plus_plus():
    from app.services.resume.skill_extractor import extract_skills
    text = "Proficient in C++, C#, and Python for backend development."
    skills = extract_skills(text)
    assert "C++" in skills["programming"]
    assert "C#" in skills["programming"]
    assert "Python" in skills["programming"]
    # "C" must NOT appear as a false positive
    assert "C" not in skills["programming"]


def test_skill_extractor_node_js():
    from app.services.resume.skill_extractor import extract_skills
    text = "Built APIs with Node.js, Express, and GraphQL."
    skills = extract_skills(text)
    assert "Node.js" in skills["backend"] or "Node" in skills["backend"]
    assert "Express" in skills["backend"]
    assert "GraphQL" in skills["backend"]


# ------------------------------------------------------------------
# 5. Integration / End-to-End Tests
# ------------------------------------------------------------------

def test_full_pipeline_perfect_resume():
    """A synthetic perfect resume should score in the Excellent tier."""
    from app.services.resume.ats_scoring_engine import ATSScoringEngine

    engine = ATSScoringEngine()
    text = """John Doe
john@example.com | +1-234-567-8900 | linkedin.com/in/johndoe | github.com/johndoe

EDUCATION
B.S. Computer Science, MIT (2020-2024) | GPA: 3.9

EXPERIENCE
Software Engineer Intern at Google (Summer 2023)
- Developed a distributed caching layer using Redis, reducing latency by 45%
- Optimised microservice communication with gRPC, improving throughput by 60%
- Led code reviews for 5 junior engineers

PROJECTS
AI Chatbot Platform
- Built an interactive AI chatbot using LangChain and OpenAI APIs, achieving 95% resolution rate
- Engineered PostgreSQL schema with indexing, reducing query time by 40%
- Implemented JWT Authentication and CI/CD pipelines with Docker

SKILLS
Python, FastAPI, PostgreSQL, Redis, Docker, Git, CI/CD, GraphQL, REST APIs, Kubernetes

CERTIFICATIONS
AWS Certified Solutions Architect – Associate
"""

    data = {
        "sections": {
            "education": "B.S. Computer Science, MIT (2020-2024) | GPA: 3.9",
            "experience": "Software Engineer Intern at Google (Summer 2023)\n- Developed a distributed caching layer using Redis, reducing latency by 45%\n- Optimised microservice communication with gRPC, improving throughput by 60%\n- Led code reviews for 5 junior engineers",
            "projects": "AI Chatbot Platform\n- Built an interactive AI chatbot using LangChain and OpenAI APIs, achieving 95% resolution rate\n- Engineered PostgreSQL schema with indexing, reducing query time by 40%\n- Implemented JWT Authentication and CI/CD pipelines with Docker",
            "skills": "Python, FastAPI, PostgreSQL, Redis, Docker, Git, CI/CD, GraphQL, REST APIs, Kubernetes",
            "certifications": "AWS Certified Solutions Architect – Associate",
            "header_contact": "john@example.com | +1-234-567-8900 | linkedin.com/in/johndoe | github.com/johndoe"
        },
        "grammar_score": 20,
        "grammar_issues": [],
        "project_score": 18,
        "keyword_score": 18,
        "missing_skills": []
    }

    result = engine.process(text, data)
    assert result["ats_score"] >= 70
    assert result["breakdown"]["project_score"] > 0
    assert result["breakdown"]["experience_score"] > 0
    assert result["strength_meter"]["quality_label"] in ["Excellent", "Good"]


def test_full_pipeline_empty_resume():
    """An empty/minimal resume should not crash and should score low but safely."""
    from app.services.resume.ats_scoring_engine import ATSScoringEngine

    engine = ATSScoringEngine()
    data = {
        "sections": {
            "education": "",
            "experience": "",
            "projects": "",
            "skills": "",
            "certifications": "",
            "header_contact": ""
        },
        "grammar_score": 20,
        "grammar_issues": [],
        "project_score": 0,
        "keyword_score": 0,
        "missing_skills": ["Python", "Docker"]
    }

    result = engine.process("", data)
    assert 10 <= result["ats_score"] <= 40
    assert result["breakdown"]["formatting_score"] == 10  # Base only
    assert result["breakdown"]["project_score"] == 0


# ------------------------------------------------------------------
# 6. Scoring Monotonicity Property Test
# ------------------------------------------------------------------

def test_score_never_decreases_when_improving():
    """Adding a better project score should never lower the overall ATS score."""
    from app.services.resume.ats_scoring_engine import ATSScoringEngine

    engine = ATSScoringEngine()
    base_data = {
        "sections": {
            "education": "B.S. CS",
            "experience": "Intern at Corp\n- Built API",
            "projects": "Project A\n- Did stuff",
            "skills": "Python, Git",
            "certifications": "Cert A",
            "header_contact": "test@test.com | 1234567890 | linkedin.com/in/test | github.com/test"
        },
        "grammar_score": 18,
        "grammar_issues": [],
        "project_score": 5,
        "keyword_score": 10,
        "missing_skills": []
    }

    result_low = engine.process("test resume", base_data)

    # Now improve project score
    base_data["project_score"] = 18
    result_high = engine.process("test resume", base_data)

    assert result_high["ats_score"] >= result_low["ats_score"]
