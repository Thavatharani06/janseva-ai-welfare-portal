import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.services.seed_service import seed_initial_welfare_data
from app.api.v1 import auth, schemes, rag, voice, eligibility, applications, dashboard, admin, digilocker, lpg, profile, electricity

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization & auto-seeding
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_initial_welfare_data(session)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Ensure downloads directory exists
os.makedirs("downloads/forms", exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(schemes.router, prefix=settings.API_V1_STR)
app.include_router(rag.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(eligibility.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(digilocker.router, prefix=settings.API_V1_STR)
app.include_router(lpg.router, prefix=settings.API_V1_STR)
app.include_router(profile.router, prefix=settings.API_V1_STR)
app.include_router(electricity.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "JanSeva AI - Multilingual Legal Welfare API Server is running",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
