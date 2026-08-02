from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, profile, resume, company, roadmap, health

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
