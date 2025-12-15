"""
Advanced Chat API endpoints with sophisticated orchestration
"""

from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatMessage, ChatResponse
from app.agents.advanced_master_agent import MasterAgent
from app.services.intelligent_agent_router import IntelligentAgentRouter, RoutingStrategy

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage, request: Request):
    """
    Advanced chat endpoint with sophisticated agent orchestration
    Routes messages through intelligent agent selection and state management
    """
    try:
        # Get orchestration systems from app state
        master_agent: MasterAgent = request.app.state.master_agent
        
        # Process message through Advanced Master Agent with orchestration
        response = await master_agent.process(
            message=chat_message.message,
            session_id=chat_message.session_id,
            phone=chat_message.phone
        )
        
        return response
        
    except Exception as e:
        print(f"Advanced chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/chat/route")
async def chat_with_routing(chat_message: ChatMessage, request: Request, routing_strategy: str = "hybrid"):
    """
    Chat endpoint with explicit routing strategy selection
    Allows testing different orchestration patterns
    """
    try:
        # Get systems from app state
        master_agent: MasterAgent = request.app.state.master_agent
        agent_router: IntelligentAgentRouter = request.app.state.agent_router
        
        # Map string to routing strategy enum
        strategy_mapping = {
            "performance": RoutingStrategy.PERFORMANCE_BASED,
            "load_balanced": RoutingStrategy.LOAD_BALANCED,
            "context_aware": RoutingStrategy.CONTEXT_AWARE,
            "hybrid": RoutingStrategy.HYBRID
        }
        
        strategy = strategy_mapping.get(routing_strategy, RoutingStrategy.HYBRID)
        
        # Process with specific routing strategy
        # For this demo, we'll route through master agent which uses orchestrator
        response = await master_agent.process(
            message=chat_message.message,
            session_id=chat_message.session_id,
            phone=chat_message.phone
        )
        
        # Add routing information to response
        if hasattr(response, 'metadata'):
            response.metadata["explicit_routing_strategy"] = routing_strategy
        
        return response
        
    except Exception as e:
        print(f"Routing-specific chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Routing chat failed: {str(e)}")


@router.get("/chat/health")
async def chat_health(request: Request):
    """Advanced health check for chat service with orchestration status"""
    try:
        # Get systems from app state
        master_agent: MasterAgent = request.app.state.master_agent
        agent_router: IntelligentAgentRouter = request.app.state.agent_router
        orchestrator = request.app.state.orchestrator
        state_manager = request.app.state.state_manager
        
        # Get analytics for health status
        routing_analytics = agent_router.get_routing_analytics()
        orchestration_metrics = orchestrator.get_orchestration_metrics()
        
        return {
            "status": "healthy",
            "service": "advanced_chat_api",
            "version": "2.0.0",
            "orchestration_systems": {
                "master_agent": "active",
                "agent_router": "active", 
                "orchestrator": "active",
                "state_manager": "active"
            },
            "agents": {
                "sales": "active",
                "verification": "active",
                "underwriting": "active"
            },
            "performance_summary": {
                "total_conversations": orchestration_metrics.get("total_conversations", 0),
                "successful_routings": routing_analytics["overall_analytics"]["successful_routings"],
                "average_routing_time": routing_analytics["overall_analytics"]["average_routing_time"],
                "active_conversations": orchestration_metrics.get("active_conversations", 0)
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "fallback": "basic_chat_available"
        }


@router.get("/chat/analytics")
async def get_chat_analytics(request: Request):
    """Get comprehensive chat analytics"""
    try:
        # Get systems from app state
        master_agent: MasterAgent = request.app.state.master_agent
        agent_router: IntelligentAgentRouter = request.app.state.agent_router
        
        analytics = {
            "master_agent_analytics": master_agent.get_orchestration_analytics(),
            "routing_analytics": agent_router.get_routing_analytics(),
            "system_status": "operational"
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            content={"error": f"Analytics retrieval failed: {str(e)}"}
        )


@router.post("/chat/conversation/pause")
async def pause_conversation(session_id: str, request: Request):
    """Pause an active conversation"""
    try:
        state_manager = request.app.state.state_manager
        
        success = await state_manager.pause_conversation(session_id, "user_request")
        
        if success:
            return {"status": "success", "message": f"Conversation {session_id} paused"}
        else:
            return {"status": "failed", "message": "Conversation not found or already paused"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pause failed: {str(e)}")


@router.post("/chat/conversation/resume")
async def resume_conversation(session_id: str, request: Request):
    """Resume a paused conversation"""
    try:
        state_manager = request.app.state.state_manager
        
        context = await state_manager.resume_conversation(session_id)
        
        if context:
            return {
                "status": "success", 
                "message": f"Conversation {session_id} resumed",
                "context": {
                    "stage": context.current_stage.value,
                    "message_count": len(getattr(context, 'conversation_history', []))
                }
            }
        else:
            return {"status": "failed", "message": "Conversation not found or expired"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume failed: {str(e)}")


@router.get("/chat/conversation/{session_id}/state")
async def get_conversation_state(session_id: str, request: Request):
    """Get current state of a conversation"""
    try:
        state_manager = request.app.state.state_manager
        
        state = state_manager.get_conversation_state(session_id)
        
        if state:
            return state
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State retrieval failed: {str(e)}")