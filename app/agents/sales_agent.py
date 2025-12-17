"""
Sales Agent - Collects loan requirements and negotiates like a human sales executive
"""

import re
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage, LoanRequest, LoanPurpose
from app.utils.ai_helper import AIHelper


class SalesAgent(BaseAgent):
    """Agent responsible for collecting loan requirements and sales negotiation"""
    
    def __init__(self):
        super().__init__("Sales Agent")
        self.ai_helper = AIHelper()
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
        
        # Check if user is confirming a typo correction (yes/no response)
        message_lower = message.lower().strip()
        if not context.loan_request or not context.loan_request.amount:
            # Check if this is a confirmation to a previous amount with typo
            if message_lower in ['yes', 'yeah', 'yup', 'correct', 'right', 'ok', 'okay', 'confirm']:
                # Check if there's a pending amount in metadata
                if hasattr(context, 'metadata') and context.metadata and 'pending_amount' in context.metadata:
                    amount = context.metadata['pending_amount']
                    if not context.loan_request:
                        context.loan_request = LoanRequest(amount=amount)
                    else:
                        context.loan_request.amount = amount
                    
                    # Clear pending amount
                    del context.metadata['pending_amount']
                    
                    amount_in_words = self._amount_in_words(amount)
                    return self._generate_response(
                        session_id=context.session_id,
                        message=f"Great! ✅ {amount_in_words} (₹{amount:,.0f}) confirmed.\n\n"
                               f"Now, let me ask about the repayment period. "
                               f"What tenure would work best for you? "
                               f"We offer flexible options from 6 months to 7 years.\n\n"
                               f"Longer tenure = Lower monthly EMI\n"
                               f"Shorter tenure = Less total interest\n\n"
                               f"What would you prefer?",
                        stage=ChatStage.SALES
                    )
            
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
        """Collect loan amount from user with AI assistance"""
        
        # First check if message is a plain number (potential loan amount)
        # This prevents valid amounts from being flagged as gibberish
        amount = self._extract_amount(message)
        if not amount:
            # Try AI extraction as well
            amount = self.ai_helper.extract_loan_amount(message)
        
        # If we found a valid amount, skip intent analysis and process it directly
        if amount:
            # Check for typos before accepting the amount
            has_typo, corrected_text = self._detect_typo(message)
            
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
                # Check if there's a typo and ask for confirmation
                if has_typo:
                    amount_in_words = self._amount_in_words(amount)
                    
                    # Store pending amount in context metadata for confirmation
                    if not hasattr(context, 'metadata') or context.metadata is None:
                        context.metadata = {}
                    context.metadata['pending_amount'] = amount
                    
                    return self._generate_response(
                        session_id=context.session_id,
                        message=f"I noticed a small typo in your message 😊\n\n"
                               f"You typed: *{message}*\n"
                               f"Did you mean: *{corrected_text}*?\n\n"
                               f"I understand you need {amount_in_words} (₹{amount:,.0f}). Is that correct?\n\n"
                               f"Reply 'yes' to confirm or type the correct amount.",
                        stage=ChatStage.SALES
                    )
                
                # No typo, proceed normally
                if not context.loan_request:
                    context.loan_request = LoanRequest(amount=amount)
                else:
                    context.loan_request.amount = amount
                
                # Smart response acknowledging understanding
                amount_in_words = self._amount_in_words(amount)
                
                return self._generate_response(
                    session_id=context.session_id,
                    message=f"Perfect! I understand you need {amount_in_words} (₹{amount:,.0f}) 👍\n\n"
                           f"That's a great amount for your financial needs. "
                           f"Now, let me ask about the repayment period. "
                           f"What tenure would work best for you? "
                           f"We offer flexible options from 6 months to 7 years.\n\n"
                           f"Longer tenure = Lower monthly EMI\n"
                           f"Shorter tenure = Less total interest\n\n"
                           f"What would you prefer?",
                    stage=ChatStage.SALES
                )
        
        # No valid amount found, use AI to understand intent
        intent_analysis = self.ai_helper.understand_intent(message, 'sales')
        
        # Handle random/gibberish messages
        if intent_analysis.get('is_random') or intent_analysis['intent'] == 'random_gibberish':
            return self._generate_response(
                session_id=context.session_id,
                message="I didn't quite understand that! 😊 Let me help you - how much loan amount do you need?\n\n"
                       "You can say:\n"
                       "• '5 lakhs' or '5L'\n"
                       "• '50000' or '50k'\n"
                       "• 'I need 2 lakh rupees'\n\n"
                       "We offer loans from ₹10,000 to ₹50,00,000.",
                stage=ChatStage.SALES
            )
        
        # Handle questions
        if intent_analysis['intent'] == 'ask_question':
            ai_response = self.ai_helper.generate_contextual_response(
                message, intent_analysis, 'sales', {}
            )
            return self._generate_response(
                session_id=context.session_id,
                message=ai_response + "\n\nNow, how much loan amount do you need?",
                stage=ChatStage.SALES
            )
        
        # Handle greetings during amount collection
        if intent_analysis['intent'] == 'greeting':
            return self._generate_response(
                session_id=context.session_id,
                message="Hello again! 👋 Let's continue with your loan application. How much loan amount do you need?",
                stage=ChatStage.SALES
            )
        
        # If we reach here, no valid amount was found
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
    
    def _detect_typo(self, message: str) -> tuple[bool, str]:
        """
        Detect common typos in loan amount messages
        Returns (has_typo: bool, corrected_message: str)
        """
        typo_map = {
            'laksh': 'lakh',
            'laskh': 'lakh',
            'laks': 'lakh',
            'lakhs': 'lakhs',
            'lacs': 'lakh',
            'lacs': 'lakh',
            'crore': 'crore',
            'cror': 'crore',
            'crores': 'crores',
            'crors': 'crores'
        }
        
        message_lower = message.lower()
        corrected = message
        has_typo = False
        
        for typo, correct in typo_map.items():
            # Skip if it's already correct
            if typo == correct or typo == correct + 's':
                continue
                
            # Check for the typo in the message
            pattern = r'\b' + re.escape(typo) + r'\b'
            if re.search(pattern, message_lower, re.IGNORECASE):
                has_typo = True
                # Preserve case in correction
                corrected = re.sub(pattern, correct, corrected, flags=re.IGNORECASE)
        
        return has_typo, corrected
    
    def _amount_in_words(self, amount: int) -> str:
        """Convert amount to words (Indian format)"""
        if amount >= 10000000:  # 1 crore or more
            crores = amount / 10000000
            if crores == int(crores):
                return f"{int(crores)} crore" if crores == 1 else f"{int(crores)} crores"
            return f"{crores:.1f} crores"
        elif amount >= 100000:  # 1 lakh or more
            lakhs = amount / 100000
            if lakhs == int(lakhs):
                return f"{int(lakhs)} lakh" if lakhs == 1 else f"{int(lakhs)} lakhs"
            return f"{lakhs:.1f} lakhs"
        elif amount >= 1000:  # thousands
            return f"₹{amount:,}"
        else:
            return f"₹{amount}"
    
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
        message_stripped = message.strip()
        
        # Check for number selection (exact match or within message)
        for num, purpose in self.loan_purposes.items():
            # Check if the message is just the number
            if message_stripped == num:
                return purpose
            # Check if number appears in message with word boundaries
            if re.search(r'\b' + num + r'\b', message):
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