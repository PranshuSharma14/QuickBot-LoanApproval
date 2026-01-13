"""
Advanced Main FastAPI application for Agentic AI Loan Sales Assistant
An Indian NBFC loan processing system with sophisticated multi-agent orchestration
QuickLoan Bank Portal - HDFC-style banking experience
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
import asyncio
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.database.database import init_db
from app.database.postgres_models import init_postgres_db
from app.api import chat, dummy_apis
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.ocr import router as ocr_router
from app.models.schemas import ChatMessage, ChatResponse
from app.agents.master_agent import MasterAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and master agent on startup"""
    # Initialize SQLite database (for legacy/existing AI flow)
    init_db()
    
    # Initialize PostgreSQL database (for user auth & dashboard)
    try:
        init_postgres_db()
        logger.info("✅ PostgreSQL database initialized")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL initialization failed: {e}. Using SQLite fallback for demo.")
    
    # Initialize master agent
    app.state.master_agent = MasterAgent()
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup(app.state.master_agent))
    
    logger.info("🚀 NBFC Agentic AI Loan Sales Assistant is ready!")
    print("🚀 NBFC Agentic AI Loan Sales Assistant is ready!")
    
    yield
    
    # Cancel cleanup task on shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    logger.info("👋 Shutting down...")
    print("👋 Shutting down...")


async def periodic_cleanup(master_agent):
    """Periodically clean up old conversations"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            logger.info("Running periodic cleanup...")
            await master_agent.state_manager.cleanup_old_conversations(max_age_hours=48)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}", exc_info=True)


# Initialize FastAPI app with advanced configuration
app = FastAPI(
    title="Advanced Agentic AI Loan Sales Assistant",
    description="AI-powered loan processing system with sophisticated multi-agent orchestration for Indian NBFC",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:5173", "http://127.0.0.1:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(ocr_router, tags=["OCR"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(dummy_apis.router, prefix="/api", tags=["External APIs"])


@app.get("/api/download-sanction-letter/{session_id}")
async def download_sanction_letter(session_id: str):
    """Download sanction letter PDF for a session"""
    import glob
    
    # Find PDF file for this session
    pattern = f"generated/sanction_letter_{session_id[:8]}*.pdf"
    files = glob.glob(pattern)
    
    if not files:
        raise HTTPException(status_code=404, detail="Sanction letter not found")
    
    # Get the most recent file if multiple exist
    latest_file = max(files, key=os.path.getctime)
    
    return FileResponse(
        path=latest_file,
        media_type="application/pdf",
        filename=f"QuickLoan_Sanction_Letter.pdf"
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "NBFC Agentic AI Loan Sales Assistant is running",
        "status": "active",
        "version": "1.0.0",
        "workflow": [
            "1. Greeting",
            "2. Sales & Requirements",
            "3. KYC Verification",
            "4. Credit Underwriting",
            "5. Approval/Rejection",
            "6. Sanction Letter"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )