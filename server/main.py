"""
POC 1: AI Adoption Metrics Dashboard
FastAPI Server - Main Application

3-Tier Architecture:
- Tier 1: React Frontend (client/)
- Tier 2: FastAPI Backend (server/)
- Tier 3: MySQL Database
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add server directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api import dashboard, users, metrics, organizations, github_sync
from app.database.connection import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    init_database()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Server shutting down")

app = FastAPI(
    title="AI Adoption Metrics API",
    description="Backend API for AI Adoption Dashboard - POC 1",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "https://poc-1-ai-adoption-dashboard-client.vercel.app",
        "https://poc-1-ai-adoption-dashboa-git-master-umangbhardwaj855s-projects.vercel.app", 
        "https://poc-1-ai-adoption-dashboard-client-on3l95swb.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(github_sync.router, prefix="/api/github", tags=["GitHub Sync"])

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "AI Adoption Metrics API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI Adoption Metrics Dashboard API",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
