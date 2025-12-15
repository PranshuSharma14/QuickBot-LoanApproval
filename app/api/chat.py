"""
Advanced Chat API endpoints with sophisticated orchestration
"""

from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatMessage, ChatResponse
from app.agents.advanced_master_agent import MasterAgent
from app.services.intelligent_agent_router import IntelligentAgentRouter, RoutingStrategy

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
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
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