"""
Comprehensive Dummy Data for NBFC Agentic AI Testing
Includes realistic customer profiles, conversation scenarios, and test data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
from enum import Enum

from app.models.schemas import ChatStage


class CustomerProfile(Enum):
    """Customer profile types for testing"""
    PREMIUM = "premium"          # High income, excellent credit
    STANDARD = "standard"        # Middle income, good credit  
    DEVELOPING = "developing"    # Lower income, building credit
    HIGH_RISK = "high_risk"     # Poor credit, high risk
    FIRST_TIME = "first_time"   # New customer, no history
    VIP = "vip"                 # High value customer
    STUDENT = "student"         # Young professional/student
    SENIOR = "senior"           # Senior citizen


class ConversationScenario(Enum):
    """Different conversation scenarios for testing"""
    SMOOTH_APPROVAL = "smooth_approval"
    NEGOTIATION_REQUIRED = "negotiation_required"
    DOCUMENTATION_ISSUES = "documentation_issues"
    CREDIT_CONCERNS = "credit_concerns"
    URGENT_REQUEST = "urgent_request"
    CONFUSED_CUSTOMER = "confused_customer"
    ANGRY_CUSTOMER = "angry_customer"
    TECHNICAL_QUERIES = "technical_queries"
    COMPLEX_REQUIREMENTS = "complex_requirements"
    ABANDONMENT = "abandonment"


# Enhanced Customer Test Data
DUMMY_CUSTOMERS = [
    {
        "id": 1,
        "name": "Rajesh Kumar",
        "phone": "9876543210",
        "email": "rajesh.kumar@email.com",
        "profile": CustomerProfile.PREMIUM,
        "credit_score": 780,
        "monthly_income": 150000,
        "employment_type": "Salaried",
        "company": "TCS",
        "experience_years": 8,
        "existing_loans": 1,
        "city": "Bangalore",
        "preferred_amount": 500000,
        "urgency_level": "medium",
        "communication_style": "professional",
        "previous_interactions": 3,
        "satisfaction_history": [4.5, 4.8, 4.9],
        "preferred_contact": "WhatsApp"
    },
    {
        "id": 2,
        "name": "Priya Sharma",
        "phone": "9876543211",
        "email": "priya.sharma@email.com",
        "profile": CustomerProfile.STANDARD,
        "credit_score": 720,
        "monthly_income": 80000,
        "employment_type": "Salaried",
        "company": "Infosys",
        "experience_years": 5,
        "existing_loans": 0,
        "city": "Mumbai",
        "preferred_amount": 300000,
        "urgency_level": "high",
        "communication_style": "friendly",
        "previous_interactions": 1,
        "satisfaction_history": [4.2],
        "preferred_contact": "Email"
    },
    {
        "id": 3,
        "name": "Mohammad Ali",
        "phone": "9876543212",
        "email": "mohammad.ali@email.com",
        "profile": CustomerProfile.DEVELOPING,
        "credit_score": 650,
        "monthly_income": 45000,
        "employment_type": "Self-Employed",
        "company": "Own Business",
        "experience_years": 3,
        "existing_loans": 2,
        "city": "Delhi",
        "preferred_amount": 200000,
        "urgency_level": "low",
        "communication_style": "detailed",
        "previous_interactions": 0,
        "satisfaction_history": [],
        "preferred_contact": "Phone"
    },
    {
        "id": 4,
        "name": "Anjali Reddy",
        "phone": "9876543213",
        "email": "anjali.reddy@email.com",
        "profile": CustomerProfile.VIP,
        "credit_score": 820,
        "monthly_income": 250000,
        "employment_type": "Business Owner",
        "company": "Reddy Enterprises",
        "experience_years": 15,
        "existing_loans": 3,
        "city": "Hyderabad",
        "preferred_amount": 1000000,
        "urgency_level": "medium",
        "communication_style": "concise",
        "previous_interactions": 12,
        "satisfaction_history": [4.9, 4.8, 4.9, 5.0, 4.7],
        "preferred_contact": "WhatsApp"
    },
    {
        "id": 5,
        "name": "Vikash Singh",
        "phone": "9876543214",
        "email": "vikash.singh@email.com",
        "profile": CustomerProfile.HIGH_RISK,
        "credit_score": 580,
        "monthly_income": 35000,
        "employment_type": "Contract",
        "company": "Various",
        "experience_years": 2,
        "existing_loans": 3,
        "city": "Patna",
        "preferred_amount": 150000,
        "urgency_level": "high",
        "communication_style": "anxious",
        "previous_interactions": 2,
        "satisfaction_history": [3.2, 3.8],
        "preferred_contact": "Phone"
    },
    {
        "id": 6,
        "name": "Kavitha Nair",
        "phone": "9876543215",
        "email": "kavitha.nair@email.com",
        "profile": CustomerProfile.STUDENT,
        "credit_score": 690,
        "monthly_income": 55000,
        "employment_type": "Salaried",
        "company": "Wipro",
        "experience_years": 1,
        "existing_loans": 1,
        "city": "Kochi",
        "preferred_amount": 100000,
        "urgency_level": "medium",
        "communication_style": "curious",
        "previous_interactions": 0,
        "satisfaction_history": [],
        "preferred_contact": "WhatsApp"
    },
    {
        "id": 7,
        "name": "Suresh Gupta",
        "phone": "9876543216",
        "email": "suresh.gupta@email.com",
        "profile": CustomerProfile.SENIOR,
        "credit_score": 750,
        "monthly_income": 120000,
        "employment_type": "Retired",
        "company": "Pension",
        "experience_years": 35,
        "existing_loans": 0,
        "city": "Pune",
        "preferred_amount": 400000,
        "urgency_level": "low",
        "communication_style": "traditional",
        "previous_interactions": 5,
        "satisfaction_history": [4.0, 4.3, 4.1, 4.4, 4.2],
        "preferred_contact": "Phone"
    },
    {
        "id": 8,
        "name": "Neha Agarwal",
        "phone": "9876543217",
        "email": "neha.agarwal@email.com",
        "profile": CustomerProfile.FIRST_TIME,
        "credit_score": 710,
        "monthly_income": 70000,
        "employment_type": "Salaried",
        "company": "Accenture",
        "experience_years": 3,
        "existing_loans": 0,
        "city": "Gurgaon",
        "preferred_amount": 250000,
        "urgency_level": "medium",
        "communication_style": "hesitant",
        "previous_interactions": 0,
        "satisfaction_history": [],
        "preferred_contact": "Email"
    }
]


# Test Conversation Scenarios
TEST_CONVERSATION_SCENARIOS = {
    ConversationScenario.SMOOTH_APPROVAL: {
        "description": "Customer with excellent profile, smooth approval process",
        "customer_profile": CustomerProfile.PREMIUM,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES, ChatStage.VERIFICATION, ChatStage.UNDERWRITING, ChatStage.APPROVED],
        "conversation_flow": [
            {"user": "Hi, I need a personal loan", "stage": ChatStage.GREETING},
            {"user": "9876543210", "stage": ChatStage.SALES},
            {"user": "I need 5 lakhs for home renovation", "stage": ChatStage.SALES},
            {"user": "Yes, I can provide all documents", "stage": ChatStage.VERIFICATION},
            {"user": "12.5% is fine", "stage": ChatStage.UNDERWRITING}
        ],
        "expected_outcome": "approved",
        "complexity_level": "low"
    },
    
    ConversationScenario.NEGOTIATION_REQUIRED: {
        "description": "Customer wants better rates, requires negotiation",
        "customer_profile": CustomerProfile.STANDARD,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES, ChatStage.VERIFICATION, ChatStage.UNDERWRITING],
        "conversation_flow": [
            {"user": "Hello, I want a loan with best rates", "stage": ChatStage.GREETING},
            {"user": "9876543211", "stage": ChatStage.SALES},
            {"user": "3 lakhs needed, but 12% rate is too high", "stage": ChatStage.SALES},
            {"user": "Can you offer something better? I have good credit", "stage": ChatStage.SALES},
            {"user": "10% would be good", "stage": ChatStage.SALES}
        ],
        "expected_outcome": "negotiated_approval",
        "complexity_level": "medium"
    },
    
    ConversationScenario.DOCUMENTATION_ISSUES: {
        "description": "Customer has documentation concerns",
        "customer_profile": CustomerProfile.DEVELOPING,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES, ChatStage.VERIFICATION],
        "conversation_flow": [
            {"user": "I need a loan but have limited documents", "stage": ChatStage.GREETING},
            {"user": "9876543212", "stage": ChatStage.SALES},
            {"user": "2 lakhs for business", "stage": ChatStage.SALES},
            {"user": "I don't have salary slips, self-employed", "stage": ChatStage.VERIFICATION},
            {"user": "What other documents can I provide?", "stage": ChatStage.VERIFICATION}
        ],
        "expected_outcome": "documentation_pending",
        "complexity_level": "high"
    },
    
    ConversationScenario.URGENT_REQUEST: {
        "description": "Customer with urgent loan requirement",
        "customer_profile": CustomerProfile.VIP,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES, ChatStage.VERIFICATION, ChatStage.UNDERWRITING, ChatStage.APPROVED],
        "conversation_flow": [
            {"user": "Emergency loan needed TODAY", "stage": ChatStage.GREETING},
            {"user": "9876543213", "stage": ChatStage.SALES},
            {"user": "10 lakhs immediately for medical emergency", "stage": ChatStage.SALES},
            {"user": "I'm your VIP customer, need instant approval", "stage": ChatStage.SALES}
        ],
        "expected_outcome": "fast_track_approval",
        "complexity_level": "high"
    },
    
    ConversationScenario.CONFUSED_CUSTOMER: {
        "description": "Customer confused about loan process",
        "customer_profile": CustomerProfile.FIRST_TIME,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES],
        "conversation_flow": [
            {"user": "I don't understand how loans work", "stage": ChatStage.GREETING},
            {"user": "What is EMI? What documents needed?", "stage": ChatStage.GREETING},
            {"user": "Is it safe? Will you steal my data?", "stage": ChatStage.GREETING},
            {"user": "9876543217", "stage": ChatStage.SALES},
            {"user": "How much can I get with 70000 salary?", "stage": ChatStage.SALES}
        ],
        "expected_outcome": "education_required",
        "complexity_level": "medium"
    },
    
    ConversationScenario.ANGRY_CUSTOMER: {
        "description": "Previously disappointed customer",
        "customer_profile": CustomerProfile.HIGH_RISK,
        "expected_stages": [ChatStage.GREETING, ChatStage.SALES],
        "conversation_flow": [
            {"user": "Your service is terrible, I was rejected last time", "stage": ChatStage.GREETING},
            {"user": "Why should I trust you again?", "stage": ChatStage.GREETING},
            {"user": "9876543214", "stage": ChatStage.SALES},
            {"user": "I need loan but you people are useless", "stage": ChatStage.SALES}
        ],
        "expected_outcome": "escalation_required",
        "complexity_level": "high"
    }
}


# Test Messages for Different Intent Analysis
TEST_MESSAGES = {
    "loan_application": [
        "I need a personal loan",
        "Want to borrow 5 lakhs",
        "Apply for credit",
        "Need money urgently",
        "Personal loan inquiry"
    ],
    "information_seeking": [
        "What are your interest rates?",
        "How does the loan process work?",
        "What documents do I need?",
        "Explain EMI calculation",
        "Tell me about eligibility criteria"
    ],
    "urgency": [
        "Need loan TODAY",
        "Emergency funds required ASAP",
        "Urgent financial help needed",
        "Immediate loan approval required",
        "Quick money needed"
    ],
    "price_sensitivity": [
        "What's the cheapest loan option?",
        "Can you reduce the interest rate?",
        "Looking for affordable loans",
        "Best rates available?",
        "Lower EMI options?"
    ],
    "trust_concerns": [
        "Is this service legitimate?",
        "Are you a real bank?",
        "Will my data be safe?",
        "Is this a scam?",
        "Can I trust you with my information?"
    ],
    "technical_support": [
        "Website is not working",
        "Can't upload documents",
        "App is crashing",
        "Having technical issues",
        "System error occurred"
    ],
    "complex_negotiations": [
        "I have multiple loan offers, need best deal",
        "Can you match competitor's rate?",
        "Need customized loan structure",
        "Special terms for bulk borrowing",
        "Flexible repayment options needed"
    ]
}


# Performance Test Data
AGENT_PERFORMANCE_TEST_DATA = {
    "sales_agent": {
        "successful_scenarios": [
            ConversationScenario.SMOOTH_APPROVAL,
            ConversationScenario.NEGOTIATION_REQUIRED,
            ConversationScenario.CONFUSED_CUSTOMER
        ],
        "challenging_scenarios": [
            ConversationScenario.ANGRY_CUSTOMER,
            ConversationScenario.COMPLEX_REQUIREMENTS
        ],
        "expected_metrics": {
            "success_rate": 0.85,
            "average_response_time": 1.2,
            "customer_satisfaction": 4.3
        }
    },
    "verification_agent": {
        "successful_scenarios": [
            ConversationScenario.SMOOTH_APPROVAL,
            ConversationScenario.URGENT_REQUEST
        ],
        "challenging_scenarios": [
            ConversationScenario.DOCUMENTATION_ISSUES,
            ConversationScenario.COMPLEX_REQUIREMENTS
        ],
        "expected_metrics": {
            "success_rate": 0.78,
            "average_response_time": 2.1,
            "customer_satisfaction": 4.1
        }
    },
    "underwriting_agent": {
        "successful_scenarios": [
            ConversationScenario.SMOOTH_APPROVAL,
            ConversationScenario.NEGOTIATION_REQUIRED
        ],
        "challenging_scenarios": [
            ConversationScenario.CREDIT_CONCERNS,
            ConversationScenario.URGENT_REQUEST
        ],
        "expected_metrics": {
            "success_rate": 0.72,
            "average_response_time": 3.5,
            "customer_satisfaction": 4.0
        }
    }
}


# Routing Test Scenarios
ROUTING_TEST_SCENARIOS = [
    {
        "scenario": "High complexity customer query",
        "message": "I need a complex loan structure with flexible EMIs, multiple guarantors, and special terms for my business expansion",
        "expected_routing": "context_aware",
        "expected_agent": "sales",
        "complexity_score": 0.9
    },
    {
        "scenario": "Simple loan inquiry",
        "message": "I need 2 lakhs personal loan",
        "expected_routing": "linear",
        "expected_agent": "sales",
        "complexity_score": 0.2
    },
    {
        "scenario": "Urgent VIP customer",
        "message": "Emergency loan needed immediately for medical treatment",
        "expected_routing": "chain",
        "expected_agent": "sales",
        "complexity_score": 0.7
    },
    {
        "scenario": "Technical documentation query",
        "message": "What specific income proofs are accepted for self-employed applicants?",
        "expected_routing": "context_aware",
        "expected_agent": "verification",
        "complexity_score": 0.6
    },
    {
        "scenario": "Angry customer escalation",
        "message": "This is terrible service, I want to speak to someone who can actually help",
        "expected_routing": "hybrid",
        "expected_agent": "sales",
        "complexity_score": 0.8
    }
]


# State Transition Test Cases
STATE_TRANSITION_TESTS = [
    {
        "name": "Natural flow progression",
        "current_stage": ChatStage.GREETING,
        "expected_next": ChatStage.SALES,
        "trigger": "phone_number_provided",
        "should_succeed": True
    },
    {
        "name": "Skip verification for VIP",
        "current_stage": ChatStage.SALES,
        "expected_next": ChatStage.UNDERWRITING,
        "trigger": "vip_customer_fast_track",
        "should_succeed": True
    },
    {
        "name": "Invalid backward transition",
        "current_stage": ChatStage.APPROVED,
        "expected_next": ChatStage.GREETING,
        "trigger": "user_confusion",
        "should_succeed": False
    },
    {
        "name": "Emergency escalation",
        "current_stage": ChatStage.SALES,
        "expected_next": ChatStage.ESCALATED,
        "trigger": "customer_frustration",
        "should_succeed": True
    }
]


# Load Testing Data
LOAD_TEST_SCENARIOS = [
    {
        "concurrent_users": 10,
        "duration_minutes": 5,
        "scenario_mix": {
            ConversationScenario.SMOOTH_APPROVAL: 0.4,
            ConversationScenario.NEGOTIATION_REQUIRED: 0.3,
            ConversationScenario.DOCUMENTATION_ISSUES: 0.2,
            ConversationScenario.URGENT_REQUEST: 0.1
        }
    },
    {
        "concurrent_users": 50,
        "duration_minutes": 10,
        "scenario_mix": {
            ConversationScenario.SMOOTH_APPROVAL: 0.3,
            ConversationScenario.NEGOTIATION_REQUIRED: 0.25,
            ConversationScenario.CONFUSED_CUSTOMER: 0.2,
            ConversationScenario.ANGRY_CUSTOMER: 0.15,
            ConversationScenario.URGENT_REQUEST: 0.1
        }
    }
]


def get_customer_by_phone(phone: str) -> Dict[str, Any]:
    """Get customer data by phone number"""
    for customer in DUMMY_CUSTOMERS:
        if customer["phone"] == phone:
            return customer
    return None


def get_test_scenario(scenario: ConversationScenario) -> Dict[str, Any]:
    """Get test scenario data"""
    return TEST_CONVERSATION_SCENARIOS.get(scenario, {})


def get_random_customer(profile: CustomerProfile = None) -> Dict[str, Any]:
    """Get random customer, optionally filtered by profile"""
    if profile:
        matching_customers = [c for c in DUMMY_CUSTOMERS if c["profile"] == profile]
        return random.choice(matching_customers) if matching_customers else None
    return random.choice(DUMMY_CUSTOMERS)


def generate_test_messages(intent: str, count: int = 5) -> List[str]:
    """Generate test messages for specific intent"""
    if intent in TEST_MESSAGES:
        return random.sample(TEST_MESSAGES[intent], min(count, len(TEST_MESSAGES[intent])))
    return []


def get_expected_agent_metrics(agent_name: str) -> Dict[str, float]:
    """Get expected performance metrics for an agent"""
    return AGENT_PERFORMANCE_TEST_DATA.get(agent_name, {}).get("expected_metrics", {})


# Analytics Test Data
ANALYTICS_TEST_EXPECTATIONS = {
    "conversation_completion_rate": 0.75,
    "average_conversation_length": 8.5,
    "customer_satisfaction_threshold": 4.0,
    "agent_response_time_threshold": 3.0,
    "successful_routing_rate": 0.90,
    "escalation_rate_threshold": 0.05
}


# Edge Case Test Scenarios
EDGE_CASE_SCENARIOS = [
    {
        "name": "Extremely long message",
        "message": "I need a loan " + "for business expansion " * 100,
        "expected_behavior": "truncation_and_processing"
    },
    {
        "name": "Empty message",
        "message": "",
        "expected_behavior": "error_handling"
    },
    {
        "name": "Non-English text",
        "message": "मुझे लोन चाहिए",
        "expected_behavior": "language_detection_or_fallback"
    },
    {
        "name": "Special characters only",
        "message": "@@@@@@!!!!####",
        "expected_behavior": "graceful_handling"
    },
    {
        "name": "SQL injection attempt",
        "message": "'; DROP TABLE customers; --",
        "expected_behavior": "security_handling"
    },
    {
        "name": "Rapid fire messages",
        "messages": ["Hi", "Need loan", "5 lakhs", "Now", "URGENT"],
        "delay_seconds": 0.1,
        "expected_behavior": "rate_limiting_or_queuing"
    }
]