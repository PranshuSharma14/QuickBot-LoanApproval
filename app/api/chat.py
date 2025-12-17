"""
Advanced Chat API endpoints with sophisticated orchestration
"""

from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatMessage, ChatResponse
from app.agents.advanced_master_agent import MasterAgent
from app.services.intelligent_agent_router import IntelligentAgentRouter, RoutingStrategy
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize advanced systems - will be replaced by app.state in endpoints


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage, request: Request):
    """
    Main chat endpoint that processes user messages through the Master Agent
    """
    try:
        # Get master agent from app state
        master_agent = request.app.state.master_agent
        
        # Process message through Master Agent
        response = await master_agent.process(
            message=chat_message.message,
            session_id=chat_message.session_id,
            phone=chat_message.phone
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error in chat endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )


@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "agents": {
            "master": "active",
            "sales": "active", 
            "verification": "active",
            "underwriting": "active"
        }
    }