"""Aggregate all v1 API routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.career import router as career_router
from app.api.v1.imports import router as imports_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.users import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_v1_router.include_router(matches_router, prefix="/matches", tags=["Matches"])
api_v1_router.include_router(imports_router, prefix="/imports", tags=["Public data"])
api_v1_router.include_router(career_router, prefix="/career", tags=["Job seeker"])
