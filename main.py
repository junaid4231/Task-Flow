from fastapi import FastAPI
from app.core.database import engine 
from app.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="TaskFlow API - Professional Task Management System"
)
app.include_router(api_router,prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TaskFlow API",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

