"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class LoanPurpose(str, Enum):
    """Enum for loan purposes"""
    PERSONAL = "personal"
    HOME_IMPROVEMENT = "home_improvement"
    EDUCATION = "education"
    MEDICAL = "medical"
    BUSINESS = "business"
    WEDDING = "wedding"
    TRAVEL = "travel"
    DEBT_CONSOLIDATION = "debt_consolidation"


class ApplicationStatus(str, Enum):
    """Enum for application status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SALARY_SLIP_REQUIRED = "salary_slip_required"


class ChatStage(str, Enum):
    """Enum for chat stages"""
    GREETING = "greeting"
    SALES = "sales"
    VERIFICATION = "verification"
    ESCALATED = "escalated"
    UNDERWRITING = "underwriting"
    SALARY_SLIP = "salary_slip"
    DECISION = "decision"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ChatMessage(BaseModel):
    """Incoming chat message"""
    session_id: Optional[str] = None
    message: str
    phone: Optional[str] = None


class ChatResponse(BaseModel):
    """Outgoing chat response"""
    session_id: str
    message: str
    stage: ChatStage
    requires_input: bool = True
    options: Optional[list] = None
    file_upload: bool = False
    final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class LoanRequest(BaseModel):
    """Loan request details"""
    amount: Optional[float] = None
    tenure: Optional[int] = None  # in months
    purpose: Optional[LoanPurpose] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and (v < 10000 or v > 5000000):
            raise ValueError('Loan amount must be between ₹10,000 and ₹50,00,000')
        return v
    
    @validator('tenure')
    def validate_tenure(cls, v):
        if v is not None and (v < 6 or v > 84):
            raise ValueError('Tenure must be between 6 and 84 months')
        return v


class CustomerVerification(BaseModel):
    """Customer verification response"""
    phone: str
    verified: bool
    customer_data: Optional[dict] = None
    message: str


class CreditScoreResponse(BaseModel):
    """Credit score API response"""
    phone: str
    credit_score: int
    score_band: str  # Excellent, Good, Fair, Poor
    message: str


class PreApprovedOfferResponse(BaseModel):
    """Pre-approved offer API response"""
    phone: str
    pre_approved_limit: float
    interest_rate: float
    message: str


class SalarySlipUpload(BaseModel):
    """Salary slip upload response"""
    uploaded: bool
    filename: str
    salary: Optional[float] = None
    message: str


class UnderwritingResult(BaseModel):
    """Underwriting decision result"""
    approved: bool
    loan_amount: float
    emi: float
    interest_rate: float
    tenure: int
    reason: str
    requires_salary_slip: bool = False


class SanctionLetter(BaseModel):
    """Sanction letter details"""
    application_id: int
    customer_name: str
    loan_amount: float
    interest_rate: float
    tenure: int
    emi: float
    file_path: str


class ConversationContext(BaseModel):
    """Conversation context for agents"""
    session_id: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_data: Optional[dict] = None
    loan_request: Optional[LoanRequest] = None
    verification_status: Optional[bool] = None
    credit_score: Optional[int] = None
    pre_approved_limit: Optional[float] = None
    underwriting_result: Optional[UnderwritingResult] = None
    salary_slip_uploaded: Optional[bool] = None
    conversation_history: list = []
    current_stage: ChatStage = ChatStage.GREETING
    metadata: Optional[Dict[str, Any]] = None