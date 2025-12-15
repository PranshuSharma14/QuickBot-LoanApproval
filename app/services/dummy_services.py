"""
Dummy services for simulating external APIs
All data is synthetic for demonstration purposes only
"""

import random
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.schemas import CustomerVerification, CreditScoreResponse, PreApprovedOfferResponse
from app.database.database import get_db, Customer


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
        """Simulate CRM customer verification API"""
        
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
        
        db = next(get_db())
        try:
            customer = db.query(Customer).filter(Customer.phone == phone).first()
            
            if not customer:
                # Return default score for unknown customers
                score = 600
            else:
                # Generate deterministic but realistic credit score based on customer data
                # This ensures consistent results for the same customer
                seed_value = sum(ord(c) for c in customer.pan)
                random.seed(seed_value)
                
                # Score distribution: 70% good (700+), 20% fair (650-699), 10% poor (<650)
                score_tier = random.choices(
                    ['excellent', 'good', 'fair', 'poor'],
                    weights=[25, 45, 20, 10],
                    k=1
                )[0]
                
                if score_tier == 'excellent':
                    score = random.randint(750, 850)
                elif score_tier == 'good':
                    score = random.randint(700, 749)
                elif score_tier == 'fair':
                    score = random.randint(650, 699)
                else:
                    score = random.randint(550, 649)
            
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
        
        finally:
            db.close()
    
    async def get_preapproved_offer(self, phone: str) -> PreApprovedOfferResponse:
        """Simulate Offer Engine API for pre-approved limits"""
        
        db = next(get_db())
        try:
            customer = db.query(Customer).filter(Customer.phone == phone).first()
            
            if not customer:
                return PreApprovedOfferResponse(
                    phone=phone,
                    pre_approved_limit=50000,
                    interest_rate=15.0,
                    message="Default pre-approved offer"
                )
            
            # Calculate pre-approved limit based on salary
            # Formula: 3-8 times monthly salary based on credit profile
            salary = customer.salary
            
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
        
        finally:
            db.close()
    
    async def process_salary_slip(self, file_path: str, phone: str) -> Dict[str, Any]:
        """Simulate salary slip processing and OCR"""
        
        # In real implementation, this would:
        # 1. Use OCR to extract text from uploaded file
        # 2. Parse salary information using regex/NLP
        # 3. Verify with employer database
        
        # For simulation, get actual salary from database
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
                return {
                    "success": False,
                    "extracted_salary": 0,
                    "confidence": 0,
                    "verification_status": "failed",
                    "message": "Unable to verify salary slip"
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