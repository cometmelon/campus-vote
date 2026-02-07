"""FastAPI main application"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth_router, elections_router, voting_router, clubs_router, dashboard_router
from seed import seed_demo_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Seeding demo data...")
    seed_demo_data()
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="CampusVote API",
    description="Campus Election Dashboard System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(auth_router)
app.include_router(elections_router)
app.include_router(voting_router)
app.include_router(clubs_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {"message": "CampusVote API", "docs": "/docs"}
