"""
Base Agent class for all loan processing agents
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.models.schemas import ConversationContext, ChatResponse


class BaseAgent(ABC):
    """Base class for all agents in the loan processing system"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, message: str, context: ConversationContext) -> ChatResponse:
        """Process user message and return response"""
        pass
    
    def _generate_response(
        self, 
        session_id: str, 
        message: str, 
        stage: str, 
        requires_input: bool = True,
        options: Optional[list] = None,
        file_upload: bool = False,
        final: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Helper method to generate standardized responses"""
        return ChatResponse(
            session_id=session_id,
            message=message,
            stage=stage,
            requires_input=requires_input,
            options=options,
            file_upload=file_upload,
            final=final,
            metadata=metadata
        )