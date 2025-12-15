"""
Verification Agent - Validates KYC using dummy CRM API
"""

import re
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage
from app.services.dummy_services import DummyServices


class VerificationAgent(BaseAgent):
    """Agent responsible for customer verification and KYC"""
    
    def __init__(self):
        super().__init__("Verification Agent")
        self.dummy_services = DummyServices()
    
    async def process(self, message: str, context: ConversationContext) -> ChatResponse:
        """Process verification messages and validate customer"""
        
        # Handle edge case - user provides email or other info instead of phone
        if '@' in message and '.' in message:
            return self._generate_response(
                session_id=context.session_id,
                message="I see you've shared an email address. Right now I need your mobile number for verification.\n\n"
                       "Please share your 10-digit registered mobile number (e.g., 9876543210)",
                stage=ChatStage.VERIFICATION
            )
        
        # Check for common confused inputs
        if any(word in message.lower() for word in ['aadhaar', 'pan', 'card']):
            return self._generate_response(
                session_id=context.session_id,
                message="I'll need those documents later! Right now, I just need your mobile number to verify your identity.\n\n"
                       "Please share your 10-digit registered mobile number.",
                stage=ChatStage.VERIFICATION
            )
        
        # Extract phone number from message
        phone = self._extract_phone(message)
        
        if not phone:
            return self._generate_response(
                session_id=context.session_id,
                message="I need your registered mobile number to proceed. Please share your 10-digit mobile number "
                       "(the one you used for registration or the one linked to your PAN card).",
                stage=ChatStage.VERIFICATION
            )
        
        # Verify customer using dummy CRM
        verification_result = await self.dummy_services.verify_customer(phone)
        
        if verification_result.verified:
            context.customer_phone = phone
            context.customer_data = verification_result.customer_data
            context.verification_status = True
            
            customer_name = verification_result.customer_data.get('name', 'Customer')
            
            return self._generate_response(
                session_id=context.session_id,
                message=f"Excellent! I've verified your details, {customer_name}. ✅\n\n"
                       "Now let me check your credit profile and pre-approved offers. "
                       "This will help me get you the best possible interest rate and terms.\n\n"
                       "Please wait a moment while I fetch your personalized offer... 🔄",
                stage=ChatStage.UNDERWRITING,
                requires_input=False
            )
        else:
            return self._generate_response(
                session_id=context.session_id,
                message="I'm sorry, but I couldn't find your details in our system with this mobile number. "
                       "This could be because:\n\n"
                       "📱 The number isn't registered with us\n"
                       "📱 It might be a different number than your registered one\n"
                       "📱 There might be a typo\n\n"
                       "Could you please double-check and share your correct registered mobile number? "
                       "Or if you're a new customer, you'll need to complete our quick registration process first.",
                stage=ChatStage.VERIFICATION
            )
    
    def _extract_phone(self, message: str) -> str:
        """Extract phone number from message"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', message)
        
        # Look for 10-digit Indian mobile numbers
        if len(digits) == 10 and digits[0] in '6789':
            return digits
        elif len(digits) == 12 and digits.startswith('91'):
            return digits[2:]  # Remove +91 country code
        elif len(digits) == 13 and digits.startswith('+91'):
            return digits[3:]  # Remove +91 country code
        
        # Try to find 10-digit pattern in the message
        phone_pattern = r'(\d{10})'
        match = re.search(phone_pattern, message)
        if match:
            phone = match.group(1)
            if phone[0] in '6789':  # Valid Indian mobile prefix
                return phone
        
        return None