from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.repositories.user import user_repo
from app.schemas.user import UserCreate

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Streamlit might be run from various ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.time()
        
        logger.info(
            f"Incoming request {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        
        response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"Completed request {request.method} {request.url.path} with status {response.status_code} in {duration:.2f}ms",
            extra={"request_id": request_id}
        )
        
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(TracingMiddleware)


@app.on_event("startup")
def startup_event():
    import os
    if os.getenv("TESTING") == "True":
        print("Skipping database table creation and seeding in testing mode.")
        return

    # Create tables on startup if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Seed the initial admin user and company criteria data
    db = SessionLocal()
    try:
        # 1. Seed Admin User
        admin = user_repo.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not admin:
            admin_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
            )
            created_admin = user_repo.create(db, obj_in=admin_in)
            created_admin.role = "admin"
            created_admin.is_verified = True
            db.add(created_admin)
            db.commit()
            db.refresh(created_admin)
            print("Successfully seeded first superuser admin user.")

        # 2. Seed Placement Companies
        from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight
        if db.query(Company).count() == 0:
            print("Seeding initial company data into placementor tables...")
            
            # --- Google SDE ---
            google = Company(
                name="Google",
                website_url="https://google.com",
                careers_url="https://careers.google.com",
                industry="Technology",
                hq_location="Mountain View, CA",
                hiring_frequency="Yearly",
                internship_ppo_available=True,
                remote_onsite="Onsite"
            )
            db.add(google)
            db.commit()
            db.refresh(google)
            
            google_role = CompanyRole(
                company_id=google.id,
                title="Software Engineer (SDE)",
                ctc=35.0,
                description="Core software engineering role focusing on algorithmic development, systems engineering, and scale.",
                application_link="https://careers.google.com",
                difficulty="Hard",
                selection_rounds=4,
                hiring_pattern="Online Coding Assessment (2 questions, 60m) followed by 3 Technical Rounds (DSA, System Architecture) and 1 Behavioral Round (Googlyness).",
                expected_oa_pattern="2 medium/hard DSA questions focusing on graphs, trees, or complex dynamic programming.",
                technical_interview_topics=["Data Structures", "Algorithms", "System Design", "Operating Systems", "Networking"],
                hr_interview_topics=["Googlyness", "Behavioral", "Teamwork", "Culture Fit"],
                interview_experience="A senior candidate reported: 'Heavy focus on graph traversals (BFS/DFS) and dynamic programming state transitions. The Googlyness round was highly situational and based on leadership principles.'",
                preparation_resources=["Google Tech Dev Guide", "LeetCode Top Interview 150", "Grokking the System Design Interview"]
            )
            db.add(google_role)
            db.commit()
            db.refresh(google_role)
            
            google_rule = EligibilityRule(
                role_id=google_role.id,
                min_cgpa=8.5,
                allowed_branches=["CSE", "IT", "ECE"],
                max_active_backlogs=0,
                min_resume_match_score=75
            )
            db.add(google_rule)
            
            google_skills = [
                ("Python", 5, "Expert"),
                ("Java", 5, "Expert"),
                ("C++", 5, "Expert"),
                ("Docker", 4, "Intermediate"),
                ("Git", 4, "Intermediate")
            ]
            for name, weight, lvl in google_skills:
                db.add(CompanySkillWeight(role_id=google_role.id, skill_name=name, importance=weight, required_level=lvl))

            # --- Amazon SDE ---
            amazon = Company(
                name="Amazon",
                website_url="https://amazon.jobs",
                careers_url="https://amazon.jobs",
                industry="Cloud & E-Commerce",
                hq_location="Seattle, WA",
                hiring_frequency="Yearly",
                internship_ppo_available=True,
                remote_onsite="Onsite"
            )
            db.add(amazon)
            db.commit()
            db.refresh(amazon)
            
            amazon_role = CompanyRole(
                company_id=amazon.id,
                title="Systems Development Engineer (SDE)",
                ctc=28.5,
                description="Build scalable customer-facing application backends, cloud database infrastructure, and robust API frameworks.",
                application_link="https://amazon.jobs",
                difficulty="Hard",
                selection_rounds=4,
                hiring_pattern="Online Assessment (Coding + Work Style Assessment) followed by 3 Technical rounds (Systems, DBMS, DSA) and 1 Managerial Round (Leadership Principles).",
                expected_oa_pattern="1 debugging round, 2 medium DSA questions, and a situational work style assessment.",
                technical_interview_topics=["Data Structures", "DBMS", "Operating Systems", "REST APIs", "AWS Cloud Concepts"],
                hr_interview_topics=["Amazon Leadership Principles", "Conflict Resolution", "Ownership", "Customer Obsession"],
                interview_experience="Intern candidate report: 'They spend 50% of the interview checking your leadership principles compatibility. Make sure you map your projects to ownership and deep dives.'",
                preparation_resources=["Amazon Leadership Principles Checklist", "Educative.io System Design", "LeetCode SQL Study Plan"]
            )
            db.add(amazon_role)
            db.commit()
            db.refresh(amazon_role)
            
            amazon_rule = EligibilityRule(
                role_id=amazon_role.id,
                min_cgpa=8.0,
                allowed_branches=["CSE", "IT", "ECE", "EEE"],
                max_active_backlogs=0,
                min_resume_match_score=70
            )
            db.add(amazon_rule)
            
            amazon_skills = [
                ("FastAPI", 4, "Intermediate"),
                ("PostgreSQL", 5, "Intermediate"),
                ("Redis", 4, "Intermediate"),
                ("AWS", 5, "Intermediate"),
                ("Docker", 4, "Intermediate")
            ]
            for name, weight, lvl in amazon_skills:
                db.add(CompanySkillWeight(role_id=amazon_role.id, skill_name=name, importance=weight, required_level=lvl))

            # --- Microsoft SDE ---
            microsoft = Company(
                name="Microsoft",
                website_url="https://microsoft.com",
                careers_url="https://careers.microsoft.com",
                industry="Technology",
                hq_location="Redmond, WA",
                hiring_frequency="Bi-yearly",
                internship_ppo_available=True,
                remote_onsite="Hybrid"
            )
            db.add(microsoft)
            db.commit()
            db.refresh(microsoft)
            
            microsoft_role = CompanyRole(
                company_id=microsoft.id,
                title="Software Engineer Intern",
                ctc=18.0,
                description="Develop features for core cloud products (Azure, Office 365) and contribute to open-source developer tooling.",
                application_link="https://careers.microsoft.com",
                difficulty="Medium",
                selection_rounds=3,
                hiring_pattern="Online Assessment (3 Codility Questions, 90 mins) followed by 2 technical interviews (DSA + OOP design) and 1 HR fitment interview.",
                expected_oa_pattern="3 algorithmic coding questions (easy-medium difficulty) on Codility.",
                technical_interview_topics=["Algorithms", "Object-Oriented Design", "Bit Manipulation", "Relational Databases"],
                hr_interview_topics=["Growth Mindset", "Inclusion", "Leadership Traits", "Collaboration"],
                interview_experience="A candidate reported: 'OOP principles and design patterns (like Singleton or Factory) are tested heavily during the second technical round.'",
                preparation_resources=["Microsoft Codility Prep List", "Head First Design Patterns", "LeetCode OOP Exercises"]
            )
            db.add(microsoft_role)
            db.commit()
            db.refresh(microsoft_role)
            
            microsoft_rule = EligibilityRule(
                role_id=microsoft_role.id,
                min_cgpa=8.0,
                allowed_branches=["CSE", "IT", "ECE"],
                max_active_backlogs=0,
                min_resume_match_score=65
            )
            db.add(microsoft_rule)
            
            microsoft_skills = [
                ("C++", 5, "Intermediate"),
                ("TypeScript", 4, "Intermediate"),
                ("React", 4, "Intermediate"),
                ("Git", 4, "Intermediate")
            ]
            for name, weight, lvl in microsoft_skills:
                db.add(CompanySkillWeight(role_id=microsoft_role.id, skill_name=name, importance=weight, required_level=lvl))

            db.commit()
            print("Initial company criteria data successfully seeded.")

            # 3. Seed Curated Learning Resources
            from app.models.roadmap import LearningResource
            if db.query(LearningResource).count() == 0:
                print("Seeding curated learning resources...")
                resources = [
                    LearningResource(
                        skill_name="Python",
                        title="Python for Beginners - Full Crash Course",
                        url="https://www.youtube.com/watch?v=rfscVS0vtbw",
                        description="Learn the absolute basics of Python syntax, data structures (lists, dicts), control flows, functions, and object-oriented principles.",
                        estimated_hours=6,
                        difficulty="Beginner",
                        category="Programming",
                        tags=["python", "basics", "dsa"],
                        source="YouTube",
                        popularity=5
                    ),
                    LearningResource(
                        skill_name="Docker",
                        title="Docker Containerization Basics and Volume Mounts",
                        url="https://docs.docker.com/get-started/",
                        description="Master docker containers, image layers caching, volumes persistence, networks, and docker-compose orchestration workflows.",
                        estimated_hours=8,
                        difficulty="Intermediate",
                        category="Tools",
                        tags=["docker", "containers", "devops"],
                        source="Official Docs",
                        popularity=4
                    ),
                    LearningResource(
                        skill_name="FastAPI",
                        title="FastAPI Web Framework Complete Tutorial",
                        url="https://fastapi.tiangolo.com/tutorial/",
                        description="Build high-concurrency asynchronous API endpoints using Pydantic, dependency injection, and automatic swagger documentation.",
                        estimated_hours=12,
                        difficulty="Intermediate",
                        category="Backend",
                        tags=["fastapi", "python", "backend", "api"],
                        source="Official Docs",
                        popularity=4
                    ),
                    LearningResource(
                        skill_name="PostgreSQL",
                        title="Relational Schema Design & Query Optimizations",
                        url="https://www.postgresql.org/docs/",
                        description="Master SQL fundamentals, complex JOIN tables, foreign keys, database normalization forms, indexes, and execution plans optimizations.",
                        estimated_hours=15,
                        difficulty="Intermediate",
                        category="Database",
                        tags=["sql", "postgres", "db", "indexing"],
                        source="Official Docs",
                        popularity=5
                    ),
                    LearningResource(
                        skill_name="AWS",
                        title="Amazon Web Services Practitioner Essentials",
                        url="https://aws.amazon.com/training/essentials/",
                        description="Learn primary cloud building blocks including EC2 instances, S3 storage buckets, RDS databases, IAM security groups, and VPC networking.",
                        estimated_hours=10,
                        difficulty="Intermediate",
                        category="Cloud",
                        tags=["aws", "cloud", "deployment"],
                        source="AWS Training",
                        popularity=4
                    )
                ]
                for r in resources:
                    db.add(r)
                db.commit()

            # 4. Seed Practice Quiz Questions
            from app.models.roadmap import QuestionBank
            if db.query(QuestionBank).count() == 0:
                print("Seeding quiz question bank...")
                questions = [
                    QuestionBank(
                        skill_name="Docker",
                        topic="Basics",
                        difficulty="Medium",
                        question_text="Which of the following commands builds a new Docker image from a local Dockerfile?",
                        options=[
                            "docker compile -f Dockerfile .",
                            "docker run -d image_name",
                            "docker build -t image_name .",
                            "docker create container_name ."
                        ],
                        correct_option="docker build -t image_name .",
                        explanation="The 'docker build' command compiles a Dockerfile in the specified directory (represented by '.') into a reusable docker image.",
                        tags=["core", "commands"]
                    ),
                    QuestionBank(
                        skill_name="Docker",
                        topic="Volumes",
                        difficulty="Hard",
                        question_text="Why do we use Docker Volume mounts in containerized environments?",
                        options=[
                            "To make compilation speeds faster.",
                            "To persist databases/files data out-of-band even if the container crashes or restarts.",
                            "To encrypt network requests between containers.",
                            "To compile Python code to binaries."
                        ],
                        correct_option="To persist databases/files data out-of-band even if the container crashes or restarts.",
                        explanation="Volume mounts bypass the container's union file system, writing data directly to the host machine storage to guarantee durability.",
                        tags=["volumes", "persistence"]
                    ),
                    QuestionBank(
                        skill_name="FastAPI",
                        topic="Async",
                        difficulty="Medium",
                        question_text="Which Python keyword enables high-concurrency asynchronous endpoint routing in FastAPI?",
                        options=[
                            "await def",
                            "async def",
                            "defer function",
                            "concurrency loop"
                        ],
                        correct_option="async def",
                        explanation="Declaring endpoints with 'async def' allows FastAPI to yield processing loops while waiting for slow database IO queries, increasing concurrency.",
                        tags=["async", "routing"]
                    ),
                    QuestionBank(
                        skill_name="FastAPI",
                        topic="Validation",
                        difficulty="Medium",
                        question_text="What parsing library does FastAPI utilize internally to enforce schema validations and generate Swagger docs?",
                        options=[
                            "Marshmallow",
                            "Django forms",
                            "Pydantic",
                            "JSON Schema Compiler"
                        ],
                        correct_option="Pydantic",
                        explanation="FastAPI natively leverages Pydantic models to automatically validate incoming JSON structures and compile OpenAPI specs.",
                        tags=["pydantic", "validation"]
                    ),
                    # Predefined subjective interview questions
                    QuestionBank(
                        id=uuid.UUID("d0c00000-0000-0000-0000-000000000001"),
                        skill_name="Docker",
                        topic="Interview",
                        difficulty="Medium",
                        question_text="Explain what a Dockerfile is and how layer caching speeds up application deployment container builds.",
                        options=[],
                        correct_option="",
                        explanation="A Dockerfile is a text document containing all instructions a user could call on the command line to assemble an image. Layer caching helps avoid building unchanged steps, speeding up consecutive builds.",
                        tags=["interview", "dockerfile"]
                    ),
                    QuestionBank(
                        id=uuid.UUID("fa0a0000-0000-0000-0000-000000000001"),
                        skill_name="FastAPI",
                        topic="Interview",
                        difficulty="Medium",
                        question_text="Explain the differences between synchronous (def) and asynchronous (async def) endpoint routing in FastAPI.",
                        options=[],
                        correct_option="",
                        explanation="Synchronous endpoints run in an external threadpool to prevent blocking the main event loop, while asynchronous endpoints run directly on the event loop and must yield control using await on non-blocking IO operations.",
                        tags=["interview", "async"]
                    ),
                    QuestionBank(
                        id=uuid.UUID("ca000000-0000-0000-0000-000000000001"),
                        skill_name="Python",
                        topic="Interview",
                        difficulty="Medium",
                        question_text="Explain how memory management works in Python, focusing on reference counting and garbage collection.",
                        options=[],
                        correct_option="",
                        explanation="Python handles memory using automatic reference counting to reclaim objects when their reference count drops to zero, and a cyclic garbage collector to detect and break reference cycles.",
                        tags=["interview", "memory"]
                    )
                ]
                for q in questions:
                    db.add(q)
                db.commit()
                print("Roadmap questions and resources successfully seeded.")

    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to PlaceMentor AI API Service."}


# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
