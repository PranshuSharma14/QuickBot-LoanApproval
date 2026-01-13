"""
Dummy services for simulating external APIs
All data is synthetic for demonstration purposes only
"""

import random
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.schemas import CustomerVerification, CreditScoreResponse, PreApprovedOfferResponse
from app.database.database import get_db, Customer


def get_postgres_user_by_phone(phone: str):
    """Get user from PostgreSQL database by phone number with retry logic"""
    try:
        from app.database.postgres_models import get_db_session_with_retry, User
        db = get_db_session_with_retry()
        if db is None:
            return None
        try:
            user = db.query(User).filter(User.phone == phone).first()
            return user
        finally:
            db.close()
    except Exception as e:
        print(f"PostgreSQL user lookup error: {e}")
        return None


class DummyServices:
    """Dummy services to simulate external API calls"""
    
    def __init__(self):
        # Credit score bands mapping
        self.score_bands = {
            (750, 900): "Excellent",
            (700, 749): "Good", 
            (650, 699): "Fair",
            (0, 649): "Poor"
        }
        
        # Interest rates based on credit score
        self.interest_rates = {
            "Excellent": 10.5,
            "Good": 12.0,
            "Fair": 14.5,
            "Poor": 18.0
        }
    
    async def verify_customer(self, phone: str) -> CustomerVerification:
        """Simulate CRM customer verification API - checks both SQLite and PostgreSQL"""
        
        # First check PostgreSQL users table (registered users)
        pg_user = get_postgres_user_by_phone(phone)
        if pg_user:
            return CustomerVerification(
                phone=phone,
                verified=True,
                customer_data={
                    "name": pg_user.full_name,
                    "address": pg_user.residential_address or "Not provided",
                    "pan": "XXXXXX" + (pg_user.aadhaar_number[-4:] if pg_user.aadhaar_number else "0000"),
                    "salary": float(pg_user.monthly_income) if pg_user.monthly_income else 50000,
                    "email": pg_user.email,
                    "user_id": pg_user.user_id
                },
                message=f"Customer {pg_user.full_name} verified successfully (Registered User)"
            )
        
        # Fallback to SQLite Customer table (demo data)
        db = next(get_db())
        try:
            customer = db.query(Customer).filter(Customer.phone == phone).first()
            
            if customer:
                return CustomerVerification(
                    phone=phone,
                    verified=True,
                    customer_data={
                        "name": customer.name,
                        "address": customer.address,
                        "pan": customer.pan,
                        "salary": customer.salary
                    },
                    message=f"Customer {customer.name} verified successfully"
                )
            else:
                return CustomerVerification(
                    phone=phone,
                    verified=False,
                    customer_data=None,
                    message="Customer not found in CRM system"
                )
        
        finally:
            db.close()
    
    async def get_credit_score(self, phone: str) -> CreditScoreResponse:
        """Simulate Credit Bureau API for credit score"""
        
        # First check PostgreSQL user
        pg_user = get_postgres_user_by_phone(phone)
        customer = None
        salary_for_seed = 50000
        
        if pg_user:
            salary_for_seed = float(pg_user.monthly_income) if pg_user.monthly_income else 50000
            # Use phone as seed for consistent score
            seed_value = sum(ord(c) for c in phone)
        else:
            db = next(get_db())
            try:
                customer = db.query(Customer).filter(Customer.phone == phone).first()
                if customer:
                    seed_value = sum(ord(c) for c in customer.pan)
                    salary_for_seed = customer.salary
                else:
                    seed_value = sum(ord(c) for c in phone)
            finally:
                db.close()
        
        if not pg_user and not customer:
            # Return default score for unknown customers
            score = 600
        else:
            # Generate credit score based primarily on salary
            # Higher salary = higher credit score (more financially stable)
            random.seed(seed_value)
            
            # Base score calculation from salary
            if salary_for_seed >= 200000:
                # Very high income - excellent credit (750-850)
                base_score = 750
                variance = random.randint(0, 100)
            elif salary_for_seed >= 100000:
                # High income - good to excellent credit (720-820)
                base_score = 720
                variance = random.randint(0, 100)
            elif salary_for_seed >= 75000:
                # Good income - good credit (700-780)
                base_score = 700
                variance = random.randint(0, 80)
            elif salary_for_seed >= 50000:
                # Medium income - fair to good credit (680-750)
                base_score = 680
                variance = random.randint(0, 70)
            elif salary_for_seed >= 30000:
                # Lower income - fair credit (650-720)
                base_score = 650
                variance = random.randint(0, 70)
            else:
                # Low income - poor to fair credit (580-680)
                base_score = 580
                variance = random.randint(0, 100)
            
            score = min(850, base_score + variance)
        
        # Determine score band
        score_band = "Poor"
        for (min_score, max_score), band in self.score_bands.items():
            if min_score <= score <= max_score:
                score_band = band
                break
        
        return CreditScoreResponse(
            phone=phone,
            credit_score=score,
            score_band=score_band,
            message=f"Credit score retrieved from bureau: {score} ({score_band})"
        )
    
    async def get_preapproved_offer(self, phone: str) -> PreApprovedOfferResponse:
        """Simulate Offer Engine API for pre-approved limits"""
        
        # First check PostgreSQL user
        pg_user = get_postgres_user_by_phone(phone)
        salary = None
        
        if pg_user:
            salary = float(pg_user.monthly_income) if pg_user.monthly_income else 50000
        else:
            db = next(get_db())
            try:
                customer = db.query(Customer).filter(Customer.phone == phone).first()
                if customer:
                    salary = customer.salary
            finally:
                db.close()
        
        if salary is None:
            return PreApprovedOfferResponse(
                phone=phone,
                pre_approved_limit=50000,
                interest_rate=15.0,
                message="Default pre-approved offer"
            )
        
        # Calculate pre-approved limit based on salary
        # Formula: 3-8 times monthly salary based on credit profile
        
        # Get credit score to determine multiplier
        credit_result = await self.get_credit_score(phone)
        score_band = credit_result.score_band
        
        # Salary multiplier based on credit score
        multipliers = {
            "Excellent": random.uniform(6, 8),
            "Good": random.uniform(4, 6),
            "Fair": random.uniform(3, 4),
            "Poor": random.uniform(2, 3)
        }
        
        multiplier = multipliers.get(score_band, 3)
        pre_approved_limit = int(salary * multiplier)
        
        # Cap at reasonable limits
        pre_approved_limit = min(pre_approved_limit, 2000000)  # Max 20 lakhs
        pre_approved_limit = max(pre_approved_limit, 50000)    # Min 50k
        
        # Round to nearest 10k
        pre_approved_limit = round(pre_approved_limit / 10000) * 10000
        
        # Get interest rate
        interest_rate = self.interest_rates.get(score_band, 15.0)
        
        return PreApprovedOfferResponse(
            phone=phone,
            pre_approved_limit=float(pre_approved_limit),
            interest_rate=interest_rate,
            message=f"Pre-approved limit: ₹{pre_approved_limit:,} at {interest_rate}% p.a."
        )
    
    async def process_salary_slip(self, file_path: str, phone: str) -> Dict[str, Any]:
        """Simulate salary slip processing and OCR"""
        
        # In real implementation, this would:
        # 1. Use OCR to extract text from uploaded file
        # 2. Parse salary information using regex/NLP
        # 3. Verify with employer database
        
        # First check PostgreSQL user
        pg_user = get_postgres_user_by_phone(phone)
        
        if pg_user:
            # Get salary from PostgreSQL user
            actual_salary = float(pg_user.monthly_income) if pg_user.monthly_income else 50000
            variation = random.uniform(0.95, 1.05)  # ±5% variation
            extracted_salary = actual_salary * variation
            
            return {
                "success": True,
                "extracted_salary": round(extracted_salary, 0),
                "confidence": random.uniform(0.9, 0.99),
                "verification_status": "verified",
                "message": f"Salary slip processed successfully. Monthly salary: ₹{extracted_salary:,.0f}"
            }
        
        # Fallback to SQLite dummy database
        db = next(get_db())
        try:
            customer = db.query(Customer).filter(Customer.phone == phone).first()
            
            if customer:
                # Add some variation to simulate real salary slip
                actual_salary = customer.salary
                variation = random.uniform(0.95, 1.05)  # ±5% variation
                extracted_salary = actual_salary * variation
                
                return {
                    "success": True,
                    "extracted_salary": round(extracted_salary, 0),
                    "confidence": random.uniform(0.9, 0.99),
                    "verification_status": "verified",
                    "message": f"Salary slip processed successfully. Monthly salary: ₹{extracted_salary:,.0f}"
                }
            else:
                # No user found in either database, still accept the upload
                return {
                    "success": True,
                    "extracted_salary": 50000,
                    "confidence": 0.85,
                    "verification_status": "pending",
                    "message": "Salary slip uploaded successfully. Verification pending."
                }
        
        finally:
            db.close()
    
    def get_dummy_customer_data(self) -> list:
        """Get list of all dummy customers for reference"""
        
        db = next(get_db())
        try:
            customers = db.query(Customer).all()
            return [
                {
                    "phone": customer.phone,
                    "name": customer.name,
                    "salary": customer.salary,
                    "address": customer.address,
                    "pan": customer.pan
                }
                for customer in customers
            ]
        finally:
            db.close()