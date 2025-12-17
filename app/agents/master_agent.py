"""
Master Agent - Orchestrates the entire loan conversation flow with advanced orchestration
"""
import re
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.sales_agent import SalesAgent
from app.agents.verification_agent import VerificationAgent
from app.agents.underwriting_agent import UnderwritingAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage, LoanRequest, LoanPurpose
from app.database.database import get_db, ChatSession, SessionLocal
from app.services.agent_orchestrator import AgentOrchestrator, OrchestrationPattern
from app.services.conversation_state_manager import ConversationStateManager, StateTransition
from app.services.pdf_service import PDFService
from app.services.ai_service import ai_service

def _extract_number(text: str):
    """Extract number with support for k, lakh, crore suffixes"""
    text = text.lower().replace(',', '')
    
    # Pattern for number with optional decimal and suffix
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*(?:crore|crores|cr)', 10000000),  # crores
        (r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)', 100000),  # lakhs
        (r'(\d+(?:\.\d+)?)\s*k', 1000),  # thousands (k)
        (r'(\d+(?:\.\d+)?)', 1)  # plain number
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, text)
        if match:
            number = float(match.group(1))
            return int(number * multiplier)
    
    return None

class MasterAgent(BaseAgent):
    """Master agent that orchestrates the entire loan conversation"""
    
    def __init__(self):
        super().__init__("Master Agent")
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.pdf_service = PDFService()
        self.state_manager = ConversationStateManager()

        
        # Greeting messages
        self.greeting_messages = [
            "Welcome to QuickLoan! 🎉 I'm your personal loan assistant.",
            "Hello! I'm here to help you get the perfect personal loan in minutes!",
            "Hi there! Ready to get your instant personal loan approval?",
            "Welcome! I'm your AI loan expert, here to make borrowing simple and fast."
        ]
    
    async def process(self, message: str, session_id: str = None, phone: str = None) -> ChatResponse:
        """Main processing method that routes to appropriate agents"""
        
        # Initialize or load session
        context = await self._get_or_create_session(session_id, phone)
        
        # Handle edge cases and validate input
        message = message.strip()
        
        # Check for empty or very short messages
        if len(message) < 1:
            return self._generate_response(
                session_id=context.session_id,
                message="I didn't receive any message. Could you please type your response?",
                stage=context.current_stage,
                requires_input=True
            )
        
        # Check for very long messages (potential spam/abuse)
        if len(message) > 2000:
            return self._generate_response(
                session_id=context.session_id,
                message="Your message is too long. Please keep it under 2000 characters. Let me know what you need!",
                stage=context.current_stage,
                requires_input=True
            )
        
        # Handle common exit/quit commands
        exit_keywords = ['quit', 'exit', 'bye', 'goodbye', 'close', 'end chat', 'stop']
        if message.lower() in exit_keywords:
            return self._generate_response(
                session_id=context.session_id,
                message="Thank you for visiting QuickLoan! If you'd like to apply for a loan in the future, "
                       "just start a new conversation. Have a great day! 😊",
                stage=ChatStage.COMPLETED,
                requires_input=False,
                final=True
            )
        
        # Handle help requests
        help_keywords = ['help', 'what can you do', 'how does this work', 'guide', 'instructions']
        if any(keyword in message.lower() for keyword in help_keywords):
            return self._generate_response(
                session_id=context.session_id,
                message="I'm your QuickLoan AI Assistant! Here's how I can help:\n\n"
                       "💰 *Loan Application*: I'll guide you through the entire process\n"
                       "📝 *Requirements*: Just tell me loan amount, tenure, and purpose\n"
                       "✅ *Instant Approval*: Credit check and approval in minutes\n"
                       "📄 *Documents*: Minimal documentation needed\n"
                       "💳 *Disbursement*: Funds in 24-48 hours\n\n"
                       "I'll ask you questions step by step. Just answer naturally!\n\n"
                       "Ready to start? Tell me how much loan you need!",
                stage=context.current_stage,
                requires_input=True
            )
        
        # Handle abuse/inappropriate content
        abuse_keywords = ['fuck', 'shit', 'bastard', 'idiot', 'stupid', 'chutiya', 'madarchod']
        if any(keyword in message.lower() for keyword in abuse_keywords):
            return self._generate_response(
                session_id=context.session_id,
                message="I'm here to help you with your loan application. Please keep the conversation professional. "
                       "How can I assist you with your loan needs?",
                stage=context.current_stage,
                requires_input=True
            )
        
        # Add message to conversation history
        context.conversation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": "user",
            "message": message
        })
        
        # Check if we're awaiting purpose selection (mid-conversation purpose change)
        if hasattr(context, 'metadata') and context.metadata and \
           context.metadata.get('awaiting_purpose_selection'):
            # Extract purpose from the message
            purpose = self.sales_agent._extract_purpose(message)
            
            if purpose:
                # Update the purpose
                context.loan_request.purpose = purpose
                # Clear the flag
                context.metadata['awaiting_purpose_selection'] = False
                
                await self._save_session(context)
                
                purpose_display = purpose.value.replace('_', ' ').title()
                
                # Return to the previous stage
                if context.current_stage == ChatStage.VERIFICATION:
                    return self._generate_response(
                        session_id=context.session_id,
                        message=f"Perfect! ✅ I've updated your loan purpose to *{purpose_display}*.\n\n"
                               f"Let me summarize your updated loan details:\n\n"
                               f"💰 Amount: ₹{context.loan_request.amount:,}\n"
                               f"📅 Tenure: {context.loan_request.tenure} months\n"
                               f"🎯 Purpose: {purpose_display}\n\n"
                               "Now, please share your registered mobile number to continue:",
                        stage=ChatStage.VERIFICATION,
                        requires_input=True
                    )
                else:
                    # For other stages, show updated summary and continue
                    response = self._generate_response(
                        session_id=context.session_id,
                        message=f"Got it! ✅ Purpose updated to *{purpose_display}*.\n\n"
                               f"Updated loan details:\n"
                               f"💰 Amount: ₹{context.loan_request.amount:,}\n"
                               f"📅 Tenure: {context.loan_request.tenure} months\n"
                               f"🎯 Purpose: {purpose_display}\n\n"
                               "Let's continue!",
                        stage=context.current_stage,
                        requires_input=True
                    )
                    return response
            else:
                # Invalid purpose selection
                return self._generate_response(
                    session_id=context.session_id,
                    message="I didn't recognize that purpose. Please select a number (1-8) or type one of these:\n\n"
                           "Personal, Home Improvement, Education, Medical, Business, Wedding, Travel, Debt Consolidation",
                    stage=context.current_stage,
                    requires_input=True
                )
        
        # 🔄 Conversational flexibility: mid-flow corrections
        updates = await self._handle_mid_conversation_update(message, context)

        if updates:
            # Check if user wants to show purpose options
            if "loan_purpose" in updates and updates["loan_purpose"] == "SHOW_OPTIONS":
                # Set a flag in metadata to indicate we're waiting for purpose selection
                if not hasattr(context, 'metadata') or context.metadata is None:
                    context.metadata = {}
                context.metadata['awaiting_purpose_selection'] = True
                
                # Clear the loan_request purpose
                old_purpose = context.loan_request.purpose
                context.loan_request.purpose = None
                
                await self._save_session(context)
                
                # Show purpose options
                return self._generate_response(
                    session_id=context.session_id,
                    message="Sure! I understand you'd like to change the loan purpose. 😊\n\n"
                           "We offer personal loans for the following purposes:\n\n"
                           "1️⃣ Personal Use\n"
                           "2️⃣ Home Improvement\n"
                           "3️⃣ Education\n"
                           "4️⃣ Medical Emergency\n"
                           "5️⃣ Business/Startup\n"
                           "6️⃣ Wedding\n"
                           "7️⃣ Travel/Vacation\n"
                           "8️⃣ Debt Consolidation\n\n"
                           "Please select a number (1-8) or type the purpose name:",
                    stage=context.current_stage,
                    requires_input=True
                )
            
            # Build update message for valid purpose changes
            update_msg = "Got it 👍 I've updated your loan details:\n\n"
            if "loan_amount" in updates:
                update_msg += f"💰 Amount: ₹{context.loan_request.amount:,}\n"
            if "loan_tenure" in updates:
                update_msg += f"📅 Tenure: {context.loan_request.tenure} months\n"
            if "loan_purpose" in updates and updates["loan_purpose"] != "SHOW_OPTIONS":
                purpose_display = context.loan_request.purpose.value.replace('_', ' ').title()
                update_msg += f"🎯 Purpose: {purpose_display}\n"
            update_msg += "\n"
            
            # Persist updated context
            await self._save_session(context)

            # 🔁 Resume flow automatically from correct agent
            if context.current_stage == ChatStage.SALES:
                response = await self.sales_agent.process("", context)

            elif context.current_stage == ChatStage.VERIFICATION:
                response = await self.verification_agent.process("", context)

            elif context.current_stage == ChatStage.UNDERWRITING:
                response = await self.underwriting_agent.process("", context)

            else:
                response = self._generate_response(
                    session_id=context.session_id,
                    message="I've updated your details. Let's continue 👍",
                    stage=context.current_stage,
                    requires_input=True
                )

            # Prepend update acknowledgement
            response.message = update_msg + response.message

            # Save again after agent response
            await self._save_session(context)
            response.session_id = context.session_id
            return response


        # Route to appropriate agent based on current stage
        if context.current_stage == ChatStage.GREETING:
            response = await self._handle_greeting(message, context)
        elif context.current_stage == ChatStage.SALES:
            response = await self.sales_agent.process(message, context)
        elif context.current_stage == ChatStage.VERIFICATION:
            response = await self.verification_agent.process(message, context)
            
            # Auto-trigger underwriting after verification
            if response.stage == ChatStage.UNDERWRITING and not response.requires_input:
                context.current_stage = ChatStage.UNDERWRITING
                response = await self.underwriting_agent.process(message, context)
                
        elif context.current_stage == ChatStage.UNDERWRITING:
            response = await self.underwriting_agent.process(message, context)
        elif context.current_stage == ChatStage.SALARY_SLIP:
            response = await self._handle_salary_slip_stage(message, context)
        elif context.current_stage == ChatStage.DECISION:
            response = await self._handle_decision_stage(message, context)
        else:
            response = await self._handle_completed_stage(message, context)
        
        # 🔧 Normalize stage to ChatStage enum
        if isinstance(response.stage, str):
            try:
                context.current_stage = ChatStage(response.stage)
            except ValueError:
                # Fallback to GREETING if invalid stage
                context.current_stage = ChatStage.GREETING
        else:
            context.current_stage = response.stage

        
        # Add response to conversation history
        context.conversation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": "assistant",
            "message": response.message
        })
        
        # Save session
        await self._save_session(context)
        
        # Update response with session ID
        response.session_id = context.session_id
        
        return response
    
    async def _handle_greeting(self, message: str, context: ConversationContext) -> ChatResponse:
        """Handle initial greeting and introduction with AI intelligence"""
        
        import random
        
        # Try to get AI response if available
        ai_response = await ai_service.get_intelligent_response(
            user_message=message,
            context={
                "stage": "greeting",
                "loan_request": context.loan_request
            },
            stage="greeting"
        )
        
        # If AI gave a response, use it
        if ai_response:
            return self._generate_response(
                session_id=context.session_id,
                message=ai_response + "\n\n💰 How much loan amount do you need?",
                stage=ChatStage.SALES,
                requires_input=True
            )
        
        # Fallback to rule-based greeting
        greeting = random.choice(self.greeting_messages)
        
        response_message = (
            f"{greeting}\n\n"
            "I can help you get a personal loan of ₹10,000 to ₹50,00,000 with:\n"
            "✅ Instant approval in minutes\n"
            "✅ Competitive interest rates\n"
            "✅ Flexible repayment options\n"
            "✅ Minimal documentation\n\n"
            "Let's start! How much loan amount do you need?"
        )
        
        return self._generate_response(
            session_id=context.session_id,
            message=response_message,
            stage=ChatStage.SALES,
            requires_input=True
        )
        
        response_message = (
            f"{greeting}\n\n"
            "I can help you get a personal loan of ₹10,000 to ₹50,00,000 with:\n"
            "✅ Instant approval in minutes\n"
            "✅ Competitive interest rates\n"
            "✅ Flexible repayment options\n"
            "✅ Minimal documentation\n\n"
            "Let's start! How much loan amount do you need?"
        )
        
        return self._generate_response(
            session_id=context.session_id,
            message=response_message,
            stage=ChatStage.SALES,
            requires_input=True
        )
    
    async def _handle_salary_slip_stage(self, message: str, context: ConversationContext) -> ChatResponse:
        """Handle salary slip upload and verification"""
        
        # In real implementation, this would handle file upload
        # For demo, we'll simulate salary extraction
        from app.services.dummy_services import DummyServices
        dummy_services = DummyServices()
        
        # Simulate salary slip processing
        if any(word in message.lower() for word in ['upload', 'file', 'slip', 'salary', 'uploaded', 'attached']):
            # Get customer salary from database (for simulation)
            customer_phone = context.customer_phone
            salary = context.customer_data.get('salary', 50000)  # Default fallback
            
            # Process with underwriting agent
            return await self.underwriting_agent.process_salary_verification(context, salary)
        else:
            return self._generate_response(
                session_id=context.session_id,
                message="Please upload your latest salary slip to proceed with the loan approval. "
                       "I need to verify your current income to approve the higher loan amount.\n\n"
                       "Accepted formats: PDF, JPG, PNG\n"
                       "Make sure the salary amount is clearly visible in the document.",
                stage=ChatStage.SALARY_SLIP,
                file_upload=True
            )
    
    async def _handle_decision_stage(self, message: str, context: ConversationContext) -> ChatResponse:
        """Handle final decision and sanction letter generation"""
        
        if any(word in message.lower() for word in ['yes', 'email', 'send', 'generate', 'sanction']):
            # Generate sanction letter
            try:
                sanction_letter = await self._generate_sanction_letter(context)
                
                customer_name = context.customer_data.get('name', 'Customer')
                
                return self._generate_response(
                    session_id=context.session_id,
                    message=f"🎉 Perfect! Your sanction letter has been generated successfully!\n\n"
                           f"*Sanction Letter Details:*\n"
                           f"📄 Document: Loan Sanction Letter\n"
                           f"👤 Customer: {customer_name}\n"
                           f"💰 Amount: ₹{context.underwriting_result.loan_amount:,.0f}\n"
                           f"📅 Tenure: {context.underwriting_result.tenure} months\n"
                           f"💳 EMI: ₹{context.underwriting_result.emi:,.0f}\n\n"
                           f"The sanction letter has been saved and is ready for download.\n\n"
                           f"*Next Steps:*\n"
                           f"1. Download and review your sanction letter\n"
                           f"2. Our team will contact you within 24 hours\n"
                           f"3. Complete final documentation\n"
                           f"4. Get funds disbursed to your account\n\n"
                           f"Thank you for choosing QuickLoan! 🙏",
                    stage=ChatStage.COMPLETED,
                    requires_input=False,
                    final=True
                )
                
            except Exception as e:
                return self._generate_response(
                    session_id=context.session_id,
                    message=f"I apologize, but there was an issue generating your sanction letter. "
                           f"Don't worry - your loan is still approved! Our team will email you "
                           f"the sanction letter within 1 hour.\n\n"
                           f"Your loan reference number is: QL{context.session_id[:8].upper()}\n\n"
                           f"Thank you for choosing QuickLoan! 🙏",
                    stage=ChatStage.COMPLETED,
                    requires_input=False,
                    final=True
                )
        else:
            customer_name = context.customer_data.get('name', 'Customer')
            
            return self._generate_response(
                session_id=context.session_id,
                message=f"No problem, {customer_name}! Here's a summary of your approved loan:\n\n"
                       f"*Final Loan Details:*\n"
                       f"✅ *Approved Amount*: ₹{context.underwriting_result.loan_amount:,.0f}\n"
                       f"✅ *Tenure*: {context.underwriting_result.tenure} months\n"
                       f"✅ *EMI*: ₹{context.underwriting_result.emi:,.0f}\n"
                       f"✅ *Interest Rate*: {context.underwriting_result.interest_rate}% p.a.\n"
                       f"✅ *Loan Reference*: QL{context.session_id[:8].upper()}\n\n"
                       f"Our team will contact you within 24 hours to complete the documentation "
                       f"and disburse the funds to your account.\n\n"
                       f"Thank you for choosing QuickLoan! 🙏",
                stage=ChatStage.COMPLETED,
                requires_input=False,
                final=True
            )
    
    async def _handle_completed_stage(self, message: str, context: ConversationContext) -> ChatResponse:
        """Handle messages after loan process is completed"""
        
        return self._generate_response(
            session_id=context.session_id,
            message="Thank you for using QuickLoan! Your loan application has been completed. "
                   "If you need any assistance or have questions, please feel free to start a new conversation.\n\n"
                   "Have a great day! 😊",
            stage=ChatStage.COMPLETED,
            requires_input=False,
            final=True
        )
    
    async def _get_or_create_session(self, session_id: str = None, phone: str = None) -> ConversationContext:
        """Get existing session or create new one"""
        
        if session_id:
            # Try to load existing session
            db = SessionLocal()
            try:
                session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
                if session:
                    context_data = json.loads(session.context) if session.context else {}
                    context = ConversationContext(**context_data)

                    # 🔧 FIX: ensure current_stage is ChatStage enum
                    if isinstance(context.current_stage, str):
                        try:
                            context.current_stage = ChatStage(context.current_stage)
                        except ValueError:
                            context.current_stage = ChatStage.GREETING

                    context.session_id = session_id
                    return context

            except Exception as e:
                print(f"Error loading session: {e}")
            finally:
                db.close()
        
        # Create new session
        new_session_id = str(uuid.uuid4())
        context = ConversationContext(
            session_id=new_session_id,
            customer_phone=phone,
            current_stage=ChatStage.GREETING,
            conversation_history=[]
        )
        
        await self.state_manager.initialize_conversation(context.session_id)
        return context
    
    from app.models.schemas import LoanRequest

    async def _handle_mid_conversation_update(
        self,
        message: str,
        context: ConversationContext
    ):
        msg = message.lower()
        updates = {}

        # 🔒 If loan_request doesn't exist yet → this is INITIAL data entry
        # Let SalesAgent handle it normally
        if context.loan_request is None:
            return None
        
        # 🚫 Skip update detection if in VERIFICATION stage and message looks like phone number
        if context.current_stage == ChatStage.VERIFICATION:
            # Check if message contains a valid Indian phone number pattern
            digits_only = re.sub(r'\D', '', message)
            
            # Check for 10-digit phone starting with 6-9
            if len(digits_only) == 10 and digits_only[0] in '6789':
                return None  # This is a phone number, not an update
            
            # Check for phone patterns with country code
            if len(digits_only) == 12 and digits_only.startswith('91'):
                return None  # Phone with +91 prefix
            
            # Check if message contains a 10-digit sequence starting with 6-9 (handles "my number is 9876543214")
            phone_match = re.search(r'[6-9]\d{9}', message)
            if phone_match:
                return None  # Contains a phone number pattern

        # ---------------- TENURE CHANGE (only if already set) ----------------
        if context.loan_request.tenure:
            # Common typos for month/year
            tenure_keywords = ["month", "months", "minths", "monts", "mnths", "mth", "mths", 
                             "year", "years", "yrs", "yr", "yeras", "yrs"]
            tenure_change_keywords = ["change tenure", "change loan tenure", "update tenure", "modify tenure"]
            
            # Check if message contains tenure-related keywords or explicit change request
            has_tenure_keyword = any(kw in msg for kw in tenure_keywords)
            has_tenure_change = any(kw in msg for kw in tenure_change_keywords)
            
            if has_tenure_keyword or has_tenure_change:
                num = _extract_number(msg)
                if num:
                    # Detect if it's years (convert to months)
                    is_years = any(kw in msg for kw in ["year", "years", "yrs", "yr", "yeras"])
                    new_tenure = num * 12 if is_years else num
                    
                    # Only update if different
                    if new_tenure != context.loan_request.tenure:
                        updates["loan_tenure"] = new_tenure

        # ---------------- AMOUNT CHANGE (only if already set) ----------------
        if context.loan_request.amount:
            # Check for explicit amount change keywords OR amount-related words
            amount_keywords = ["loan", "amount", "₹", "rs", "rupees", "lakh", "lakhs", "crore", "crores", 
                              "thousand", "k", "l", "cr", "need", "want", "require"]
            
            # Also check if message contains amount indicators like "lakh/crore/k"
            has_amount_indicator = any(w in msg for w in amount_keywords)
            
            if has_amount_indicator:
                # Try to extract the new amount
                num = _extract_number(msg)
                if num and num >= 10000 and num != context.loan_request.amount:
                    updates["loan_amount"] = num

        # ---------------- PURPOSE CHANGE (only if already set) ----------------
        # First check if user wants to change purpose (even if keyword doesn't match)
        purpose_change_keywords = ["change purpose", "change loan purpose", "different purpose", "modify purpose", "update purpose"]
        purpose_inquiry_keywords = ["what are", "show me", "which", "available", "list", "options", "types of"]
        # Common typos of "purpose"
        purpose_typos = ["purpose", "purose", "purpse", "purposs", "porpose", "purpos", "perpus", "perpuse"]
        
        # Check if user is asking about available purposes or wants to change
        if context.loan_request.purpose:
            # Check for explicit purpose change keywords
            if any(kw in msg for kw in purpose_change_keywords):
                updates["loan_purpose"] = "SHOW_OPTIONS"  # Flag to show options
            # Check if asking about purposes
            elif any(kw in msg for kw in purpose_inquiry_keywords) and any(typo in msg for typo in purpose_typos):
                # User is asking "what are various loan purposes" or similar
                updates["loan_purpose"] = "SHOW_OPTIONS"
            # Check if they're trying to say "loan purpose <something>" with typo
            elif "loan" in msg and any(typo in msg for typo in purpose_typos):
                # Likely trying to change purpose, show options
                updates["loan_purpose"] = "SHOW_OPTIONS"
            # Only check for specific purpose keywords if we haven't already flagged for SHOW_OPTIONS
            else:
                purpose_map = {
                "wedding": LoanPurpose.WEDDING,
                "marriage": LoanPurpose.WEDDING,
                "shaadi": LoanPurpose.WEDDING,
                "education": LoanPurpose.EDUCATION,
                "study": LoanPurpose.EDUCATION,
                "edu": LoanPurpose.EDUCATION,
                "business": LoanPurpose.BUSINESS,
                "startup": LoanPurpose.BUSINESS,
                "medical": LoanPurpose.MEDICAL,
                "health": LoanPurpose.MEDICAL,
                "hospital": LoanPurpose.MEDICAL,
                "travel": LoanPurpose.TRAVEL,
                "vacation": LoanPurpose.TRAVEL,
                "trip": LoanPurpose.TRAVEL,
                "personal": LoanPurpose.PERSONAL,
                "home": LoanPurpose.HOME_IMPROVEMENT,
                "house": LoanPurpose.HOME_IMPROVEMENT,
                "renovation": LoanPurpose.HOME_IMPROVEMENT,
                "repair": LoanPurpose.HOME_IMPROVEMENT,
                "improvement": LoanPurpose.HOME_IMPROVEMENT,
                "debt": LoanPurpose.DEBT_CONSOLIDATION,
                "consolidation": LoanPurpose.DEBT_CONSOLIDATION,
                "loan closure": LoanPurpose.DEBT_CONSOLIDATION,
                "payoff": LoanPurpose.DEBT_CONSOLIDATION
                }
                for key, purpose_value in purpose_map.items():
                    if key in msg:
                        # Check if it's actually different from current purpose
                        if purpose_value != context.loan_request.purpose:
                            updates["loan_purpose"] = purpose_value
                            break

        # 🚫 Nothing actually changed → continue normal flow
        if not updates:
            return None

        # ---------------- INTELLIGENT STAGE ROLLBACK ----------------
        if context.current_stage == ChatStage.VERIFICATION:
            target_stage = ChatStage.SALES
        elif context.current_stage == ChatStage.UNDERWRITING:
            target_stage = ChatStage.VERIFICATION
        elif context.current_stage == ChatStage.DECISION:
            target_stage = ChatStage.UNDERWRITING
        else:
            target_stage = context.current_stage

        # ---------------- APPLY UPDATES SAFELY ----------------
        if "loan_amount" in updates:
            context.loan_request.amount = updates["loan_amount"]

        if "loan_tenure" in updates:
            context.loan_request.tenure = updates["loan_tenure"]

        if "loan_purpose" in updates:
            context.loan_request.purpose = updates["loan_purpose"]

        # ---------------- STATE MANAGER TRANSITION ----------------
        await self.state_manager.transition_stage(
            session_id=context.session_id,
            new_stage=target_stage,
            transition_type=StateTransition.BACKWARD
        )

        # Keep local context in sync
        context.current_stage = target_stage

        return updates


    async def _save_session(self, context: ConversationContext):
        """Save session to database"""
        
        db = SessionLocal()
        try:
            # Convert context to dict for JSON storage
            context_dict = context.dict()
            context_json = json.dumps(context_dict, default=str)
            
            # Update or create session
            session = db.query(ChatSession).filter(ChatSession.session_id == context.session_id).first()
            
            if session:
                session.customer_phone = context.customer_phone
                session.current_stage = context.current_stage.value
                session.context = context_json
                session.updated_at = datetime.now(timezone.utc)
            else:
                session = ChatSession(
                    session_id=context.session_id,
                    customer_phone=context.customer_phone,
                    current_stage=context.current_stage.value,
                    context=context_json
                )
                db.add(session)
            
            db.commit()
            
        except Exception as e:
            print(f"Error saving session: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _generate_sanction_letter(self, context: ConversationContext) -> str:
        """Generate PDF sanction letter"""
        
        try:
            letter_path = await self.pdf_service.generate_sanction_letter(
                customer_data=context.customer_data,
                loan_details=context.underwriting_result,
                session_id=context.session_id
            )
            return letter_path
        except Exception as e:
            print(f"Error generating sanction letter: {e}")
            raise e