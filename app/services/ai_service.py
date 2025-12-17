"""
AI Service for intelligent conversation handling using OpenAI
"""
import logging
from typing import Optional, Dict, Any
from app.utils.config import config

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered intelligent responses"""
    
    def __init__(self):
        self.openai_available = False
        self.client = None
        
        if config.is_openai_enabled():
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                self.openai_available = True
                logger.info("✅ OpenAI service initialized successfully")
            except ImportError:
                logger.warning("⚠️ OpenAI package not installed. Install with: pip install openai")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
        else:
            logger.info("ℹ️ OpenAI not configured. Using rule-based responses.")
    
    async def get_intelligent_response(
        self, 
        user_message: str, 
        context: Dict[str, Any],
        stage: str
    ) -> Optional[str]:
        """
        Get an intelligent AI response based on context
        
        Args:
            user_message: The user's message
            context: Conversation context
            stage: Current conversation stage
            
        Returns:
            AI-generated response or None if AI not available
        """
        if not self.openai_available:
            return None
        
        try:
            # Build context-aware prompt
            system_prompt = self._build_system_prompt(stage, context)
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=config.OPENAI_MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"AI response generated for stage: {stage}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return None
    
    def _build_system_prompt(self, stage: str, context: Dict[str, Any]) -> str:
        """Build context-aware system prompt"""
        
        base_prompt = """You are a helpful and professional loan assistant for QuickLoan, an Indian NBFC (Non-Banking Financial Company). 
You help customers apply for personal loans ranging from ₹10,000 to ₹50,00,000.

Your personality:
- Warm, friendly, and professional
- Clear and concise in communication
- Patient and understanding
- Helpful in guiding customers through the loan process
- Use appropriate Indian context (₹ symbol, Indian terms)

Important guidelines:
- Keep responses SHORT (2-3 sentences max)
- Be conversational and natural
- Guide users toward completing their loan application
- If user asks unrelated questions, politely redirect to loan process
- Use emojis sparingly and appropriately"""
        
        stage_guidance = {
            "greeting": """
Current Stage: GREETING
Your task: Welcome the user and ask about their loan amount requirement.
If they say something random, acknowledge it briefly and guide them to start the loan process.""",
            
            "sales": """
Current Stage: SALES (Collecting Loan Requirements)
Your task: Collect loan amount, tenure, and purpose.
If they ask questions, answer briefly and guide back to requirements.""",
            
            "verification": """
Current Stage: VERIFICATION (Identity Check)
Your task: Request and verify customer's mobile number.
Keep focus on verification process.""",
            
            "underwriting": """
Current Stage: UNDERWRITING (Credit Assessment)
Your task: Inform about credit evaluation and loan decision.
Be reassuring and professional."""
        }
        
        stage_prompt = stage_guidance.get(stage, "")
        
        # Add context information
        context_info = ""
        if context.get("loan_request"):
            loan_req = context["loan_request"]
            context_info = f"\nCurrent loan request: Amount=₹{loan_req.get('amount', 'Not set')}, Tenure={loan_req.get('tenure', 'Not set')} months"
        
        return f"{base_prompt}\n\n{stage_prompt}{context_info}\n\nRespond naturally to the user's message."
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.openai_available


# Global AI service instance
ai_service = AIService()
