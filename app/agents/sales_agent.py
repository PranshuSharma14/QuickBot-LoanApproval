"""
Sales Agent - Collects loan requirements and negotiates like a human sales executive
"""

import re
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage, LoanRequest, LoanPurpose


class SalesAgent(BaseAgent):
    """Agent responsible for collecting loan requirements and sales negotiation"""
    
    def __init__(self):
        super().__init__("Sales Agent")
        self.loan_purposes = {
            "1": LoanPurpose.PERSONAL,
            "2": LoanPurpose.HOME_IMPROVEMENT,
            "3": LoanPurpose.EDUCATION,
            "4": LoanPurpose.MEDICAL,
            "5": LoanPurpose.BUSINESS,
            "6": LoanPurpose.WEDDING,
            "7": LoanPurpose.TRAVEL,
            "8": LoanPurpose.DEBT_CONSOLIDATION
        }
    
    async def process(self, message: str, context: ConversationContext) -> ChatResponse:
        """Process sales-related messages and collect loan requirements"""
        
        # If we don't have loan amount yet
        if not context.loan_request or not context.loan_request.amount:
            return await self._collect_loan_amount(message, context)
        
        # If we don't have tenure yet
        if not context.loan_request.tenure:
            return await self._collect_tenure(message, context)
        
        # If we don't have purpose yet
        if not context.loan_request.purpose:
            return await self._collect_purpose(message, context)
        
        # All loan details collected, move to verification
        return self._generate_response(
            session_id=context.session_id,
            message="Perfect! Let me summarize your loan requirement:\n\n"
                   f"💰 Loan Amount: ₹{context.loan_request.amount:,.0f}\n"
                   f"📅 Tenure: {context.loan_request.tenure} months\n"
                   f"🎯 Purpose: {context.loan_request.purpose.value.replace('_', ' ').title()}\n\n"
                   "Now, let me quickly verify your details to proceed with the application. "
                   "Could you please share your registered mobile number?",
            stage=ChatStage.VERIFICATION,
            requires_input=True
        )
    
    async def _collect_loan_amount(self, message: str, context: ConversationContext) -> ChatResponse:
        """Collect loan amount from user"""
        
        # Handle edge cases - user asks questions instead of providing amount
        clarification_keywords = ['what', 'how much', 'minimum', 'maximum', 'range', 'limit', 'can i get']
        if any(keyword in message.lower() for keyword in clarification_keywords) and len(message.split()) < 15:
            return self._generate_response(
                session_id=context.session_id,
                message="Great question! Here are our loan amount options:\n\n"
                       "💰 **Minimum**: ₹10,000\n"
                       "💰 **Maximum**: ₹50,00,000\n\n"
                       "The exact amount you qualify for depends on your credit score and income.\n\n"
                       "How much do you need? Just tell me the amount!",
                stage=ChatStage.SALES
            )
        
        # Try to extract amount from message
        amount = self._extract_amount(message)
        
        if amount:
            if amount < 10000:
                return self._generate_response(
                    session_id=context.session_id,
                    message="I understand you need a smaller amount, but our minimum loan amount is ₹10,000. "
                           "This gives you better terms and lower processing fees. Would you like to consider ₹10,000 instead?",
                    stage=ChatStage.SALES
                )
            elif amount > 5000000:
                return self._generate_response(
                    session_id=context.session_id,
                    message="That's a substantial amount! Our maximum personal loan limit is ₹50,00,000. "
                           "Would ₹50,00,000 work for your requirements? We can offer very competitive rates for this amount.",
                    stage=ChatStage.SALES
                )
            else:
                # Valid amount, store it
                if not context.loan_request:
                    context.loan_request = LoanRequest(amount=amount)
                else:
                    context.loan_request.amount = amount
                
                return self._generate_response(
                    session_id=context.session_id,
                    message=f"Excellent! ₹{amount:,.0f} is a great choice. "
                           f"Now, what repayment tenure would work best for you? "
                           f"We offer flexible options from 6 months to 7 years (84 months). "
                           f"Longer tenure means lower EMI. What would you prefer?",
                    stage=ChatStage.SALES
                )
        else:
            return self._generate_response(
                session_id=context.session_id,
                message="I'd love to help you with the perfect loan amount! Could you tell me how much you need? "
                       "We offer personal loans from ₹10,000 to ₹50,00,000. What amount would work for you?",
                stage=ChatStage.SALES
            )
    
    async def _collect_tenure(self, message: str, context: ConversationContext) -> ChatResponse:
        """Collect loan tenure from user"""
        
        tenure = self._extract_tenure(message)
        
        if tenure:
            if tenure < 6:
                return self._generate_response(
                    session_id=context.session_id,
                    message="I understand you want to repay quickly! However, our minimum tenure is 6 months "
                           "for better processing and lower costs. 6 months would give you an EMI of approximately "
                           f"₹{(context.loan_request.amount * 1.12 / 6):,.0f}. Would that work?",
                    stage=ChatStage.SALES
                )
            elif tenure > 84:
                return self._generate_response(
                    session_id=context.session_id,
                    message="Our maximum tenure is 84 months (7 years) which gives you the lowest possible EMI of "
                           f"approximately ₹{(context.loan_request.amount * 1.85 / 84):,.0f}. Would 84 months work for you?",
                    stage=ChatStage.SALES
                )
            else:
                # Valid tenure, store it
                context.loan_request.tenure = tenure
                estimated_emi = (context.loan_request.amount * 1.35) / tenure  # Rough estimate
                
                return self._generate_response(
                    session_id=context.session_id,
                    message=f"Perfect! {tenure} months is an excellent choice. Your EMI will be approximately "
                           f"₹{estimated_emi:,.0f} (exact amount will be confirmed after approval).\n\n"
                           "Now, what's the purpose of this loan? This helps us offer you the best rates:\n\n"
                           "1️⃣ Personal expenses\n"
                           "2️⃣ Home improvement\n"
                           "3️⃣ Education\n"
                           "4️⃣ Medical expenses\n"
                           "5️⃣ Business needs\n"
                           "6️⃣ Wedding\n"
                           "7️⃣ Travel\n"
                           "8️⃣ Debt consolidation\n\n"
                           "Please choose a number or tell me the purpose:",
                    stage=ChatStage.SALES,
                    options=["Personal", "Home improvement", "Education", "Medical", "Business", "Wedding", "Travel", "Debt consolidation"]
                )
        else:
            return self._generate_response(
                session_id=context.session_id,
                message="What repayment period would be comfortable for you? I can offer:\n\n"
                       "🔹 Short term (6-12 months): Higher EMI, less interest\n"
                       "🔹 Medium term (12-36 months): Balanced EMI\n"
                       "🔹 Long term (36-84 months): Lower EMI, more flexibility\n\n"
                       "Just tell me the number of months that suits you best!",
                stage=ChatStage.SALES
            )
    
    async def _collect_purpose(self, message: str, context: ConversationContext) -> ChatResponse:
        """Collect loan purpose from user"""
        
        purpose = self._extract_purpose(message)
        
        if purpose:
            context.loan_request.purpose = purpose
            
            purpose_benefits = {
                LoanPurpose.PERSONAL: "Great choice! Personal loans offer maximum flexibility.",
                LoanPurpose.HOME_IMPROVEMENT: "Excellent! Home improvement loans often qualify for special rates.",
                LoanPurpose.EDUCATION: "Education is the best investment! You may get preferential rates.",
                LoanPurpose.MEDICAL: "Health is wealth! Medical loans get priority processing.",
                LoanPurpose.BUSINESS: "Business growth loans come with flexible repayment options.",
                LoanPurpose.WEDDING: "Congratulations! Wedding loans have special festive offers.",
                LoanPurpose.TRAVEL: "Travel loans help you create memories! Quick approval process.",
                LoanPurpose.DEBT_CONSOLIDATION: "Smart move! Debt consolidation can save you money."
            }
            
            return self._generate_response(
                session_id=context.session_id,
                message=f"{purpose_benefits[purpose]}\n\n"
                       "Let me summarize your loan requirement:\n\n"
                       f"💰 Amount: ₹{context.loan_request.amount:,.0f}\n"
                       f"📅 Tenure: {context.loan_request.tenure} months\n"
                       f"🎯 Purpose: {purpose.value.replace('_', ' ').title()}\n\n"
                       "Perfect! Now let me verify your details to get you the best rates. "
                       "Could you please share your registered mobile number?",
                stage=ChatStage.VERIFICATION
            )
        else:
            return self._generate_response(
                session_id=context.session_id,
                message="Could you please select one of the loan purposes? This helps us:\n"
                       "✅ Offer you better interest rates\n"
                       "✅ Speed up the approval process\n"
                       "✅ Provide customized terms\n\n"
                       "1️⃣ Personal expenses  2️⃣ Home improvement  3️⃣ Education  4️⃣ Medical\n"
                       "5️⃣ Business  6️⃣ Wedding  7️⃣ Travel  8️⃣ Debt consolidation\n\n"
                       "Just type the number or purpose:",
                stage=ChatStage.SALES,
                options=["Personal", "Home improvement", "Education", "Medical", "Business", "Wedding", "Travel", "Debt consolidation"]
            )
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract loan amount from message"""
        # Remove common words and extract numbers
        message = message.lower().replace(',', '')
        
        # Look for patterns like "5 lakh", "2.5 lakh", "50000", "50k"
        patterns = [
            r'(\d+\.?\d*)\s*lakh',
            r'(\d+\.?\d*)\s*crore',
            r'(\d+\.?\d*)\s*k\b',
            r'₹\s*(\d+\.?\d*)',
            r'(\d{4,})'  # Any number with 4+ digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                amount = float(match.group(1))
                if 'lakh' in message:
                    amount *= 100000
                elif 'crore' in message:
                    amount *= 10000000
                elif 'k' in message and amount < 1000:
                    amount *= 1000
                return amount
        
        return None
    
    def _extract_tenure(self, message: str) -> Optional[int]:
        """Extract tenure from message"""
        # Look for numbers followed by months/years
        patterns = [
            r'(\d+)\s*month',
            r'(\d+)\s*year',
            r'(\d+)\s*yr',
            r'(\d+)\s*mon',
            r'(\d+)(?:\s+months?)?(?:\s+years?)?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                tenure = int(match.group(1))
                if 'year' in message or 'yr' in message:
                    tenure *= 12
                return tenure
        
        return None
    
    def _extract_purpose(self, message: str) -> Optional[LoanPurpose]:
        """Extract loan purpose from message"""
        message_lower = message.lower()
        
        # Check for number selection
        for num, purpose in self.loan_purposes.items():
            if num in message or str(int(num)) in message:
                return purpose
        
        # Check for keyword matching
        purpose_keywords = {
            LoanPurpose.PERSONAL: ['personal', 'general', 'miscellaneous'],
            LoanPurpose.HOME_IMPROVEMENT: ['home', 'house', 'renovation', 'repair', 'improvement'],
            LoanPurpose.EDUCATION: ['education', 'study', 'course', 'college', 'school'],
            LoanPurpose.MEDICAL: ['medical', 'health', 'hospital', 'treatment', 'medicine'],
            LoanPurpose.BUSINESS: ['business', 'startup', 'investment', 'work', 'office'],
            LoanPurpose.WEDDING: ['wedding', 'marriage', 'shaadi', 'ceremony'],
            LoanPurpose.TRAVEL: ['travel', 'vacation', 'trip', 'tour', 'holiday'],
            LoanPurpose.DEBT_CONSOLIDATION: ['debt', 'consolidation', 'loan closure', 'payoff']
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return purpose
        
        return None