from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, email
from app.db.session import create_tables_if_not_exist
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Initialize database tables without dropping existing data
    logger.info("Initializing database tables...")
    create_tables_if_not_exist()
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    raise

settings = get_settings()

app = FastAPI(
    title="Authentication API",
    description="API for user signup and login",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True, # Allows cookies to be sent with requests
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    email.router,
    prefix=f"{settings.API_V1_STR}/email",
    tags=["email"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Authentication API",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
