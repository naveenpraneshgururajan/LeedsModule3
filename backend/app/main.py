"""
FastAPI Main Application

Configuration Manager API - No Pydantic models, using plain dictionaries.
"""

import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.parser import YAMLParser
from core.ml_detector import MLDetector
from core.change_tracker import ChangeTracker
from core.uplift_assistant import UpliftAssistant

# Import route modules
from app.api.routes import environments, uplift, changes, reports

# Initialize FastAPI app
app = FastAPI(
    title="Configuration Manager API",
    description="Intelligent configuration management with ML-based anomaly detection",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components (shared across requests)
print("\n" + "=" * 60)
print("🚀 Starting Configuration Manager API")
print("=" * 60)

parser = YAMLParser(settings.YAML_FILES_PATH)
ml_detector = MLDetector(settings.MODELS_PATH)
change_tracker = ChangeTracker(settings.GIT_REPO_PATH)
uplift_assistant = UpliftAssistant()

print(f"\n📂 YAML Files Path: {settings.YAML_FILES_PATH}")
print(f"🔧 Git Repo Path: {settings.GIT_REPO_PATH}")
print(f"🤖 Models Path: {settings.MODELS_PATH}")
print(f"🌐 Frontend URL: {settings.FRONTEND_URL}")
print("\n" + "=" * 60)

# Store in app state for access in routes
app.state.parser = parser
app.state.ml_detector = ml_detector
app.state.change_tracker = change_tracker
app.state.uplift_assistant = uplift_assistant


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Configuration Manager API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "environments": "/api/environments",
            "uplift": "/api/uplift",
            "changes": "/api/changes",
            "reports": "/api/reports",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "parser": parser.yaml_dir.exists(),
            "ml_detector": ml_detector.is_ready(),
            "change_tracker": change_tracker.is_available()
        },
        "settings": {
            "yaml_path": settings.YAML_FILES_PATH,
            "models_loaded": ml_detector.is_ready()
        }
    }


# Include routers
app.include_router(
    environments.router,
    prefix="/api/environments",
    tags=["environments"]
)

app.include_router(
    uplift.router,
    prefix="/api/uplift",
    tags=["uplift"]
)

app.include_router(
    changes.router,
    prefix="/api/changes",
    tags=["changes"]
)

app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["reports"]
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
