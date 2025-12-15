"""
Master Agent - Orchestrates the entire loan conversation flow with advanced orchestration
"""

import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.sales_agent import SalesAgent
from app.agents.verification_agent import VerificationAgent
from app.agents.underwriting_agent import UnderwritingAgent
from app.models.schemas import ConversationContext, ChatResponse, ChatStage
from app.database.database import get_db, ChatSession
from app.services.agent_orchestrator import AgentOrchestrator, OrchestrationPattern
from app.services.conversation_state_manager import ConversationStateManager, StateTransition
from app.services.pdf_service import PDFService


class MasterAgent(BaseAgent):
    """Master agent that orchestrates the entire loan conversation"""
    
    def __init__(self):
        super().__init__("Master Agent")
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.pdf_service = PDFService()
        
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
                       "💰 **Loan Application**: I'll guide you through the entire process\n"
                       "📝 **Requirements**: Just tell me loan amount, tenure, and purpose\n"
                       "✅ **Instant Approval**: Credit check and approval in minutes\n"
                       "📄 **Documents**: Minimal documentation needed\n"
                       "💳 **Disbursement**: Funds in 24-48 hours\n\n"
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
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "user",
            "message": message
        })
        
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
        
        # Update context stage from response
        context.current_stage = response.stage
        
        # Add response to conversation history
        context.conversation_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "assistant",
            "message": response.message
        })
        
        # Save session
        await self._save_session(context)
        
        # Update response with session ID
        response.session_id = context.session_id
        
        return response
    
    async def _handle_greeting(self, message: str, context: ConversationContext) -> ChatResponse:
        """Handle initial greeting and introduction"""
        
        import random
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
                           f"**Sanction Letter Details:**\n"
                           f"📄 Document: Loan Sanction Letter\n"
                           f"👤 Customer: {customer_name}\n"
                           f"💰 Amount: ₹{context.underwriting_result.loan_amount:,.0f}\n"
                           f"📅 Tenure: {context.underwriting_result.tenure} months\n"
                           f"💳 EMI: ₹{context.underwriting_result.emi:,.0f}\n\n"
                           f"The sanction letter has been saved and is ready for download.\n\n"
                           f"**Next Steps:**\n"
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
                       f"**Final Loan Details:**\n"
                       f"✅ **Approved Amount**: ₹{context.underwriting_result.loan_amount:,.0f}\n"
                       f"✅ **Tenure**: {context.underwriting_result.tenure} months\n"
                       f"✅ **EMI**: ₹{context.underwriting_result.emi:,.0f}\n"
                       f"✅ **Interest Rate**: {context.underwriting_result.interest_rate}% p.a.\n"
                       f"✅ **Loan Reference**: QL{context.session_id[:8].upper()}\n\n"
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
            db = next(get_db())
            try:
                session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
                if session:
                    context_data = json.loads(session.context) if session.context else {}
                    context = ConversationContext(**context_data)
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
        
        return context
    
    async def _save_session(self, context: ConversationContext):
        """Save session to database"""
        
        db = next(get_db())
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
                session.updated_at = datetime.utcnow()
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