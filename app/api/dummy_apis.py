"""
Dummy API endpoints for simulating external services
These APIs simulate CRM, Credit Bureau, and Offer Engine
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import os
import aiofiles

from app.services.dummy_services import DummyServices
from app.models.schemas import CustomerVerification, CreditScoreResponse, PreApprovedOfferResponse

router = APIRouter()

# Initialize dummy services
dummy_services = DummyServices()


@router.post("/crm/verify", response_model=CustomerVerification)
async def verify_customer(phone: str = Form(...)):
    """
    Dummy CRM API endpoint for customer verification
    Simulates checking customer details in CRM system
    """
    try:
        result = await dummy_services.verify_customer(phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CRM verification failed: {str(e)}")


@router.get("/credit-score/{phone}", response_model=CreditScoreResponse)
async def get_credit_score(phone: str):
    """
    Dummy Credit Bureau API endpoint
    Simulates fetching credit score from credit bureau
    """
    try:
        result = await dummy_services.get_credit_score(phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credit score fetch failed: {str(e)}")


@router.get("/offer/preapproved/{phone}", response_model=PreApprovedOfferResponse)
async def get_preapproved_offer(phone: str):
    """
    Dummy Offer Engine API endpoint
    Simulates fetching pre-approved loan offers
    """
    try:
        result = await dummy_services.get_preapproved_offer(phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offer fetch failed: {str(e)}")


@router.post("/upload/salary-slip")
async def upload_salary_slip(
    file: UploadFile = File(...),
    phone: str = Form(...)
):
    """
    Dummy salary slip upload endpoint
    Simulates OCR processing of salary slip documents
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload PDF, JPG, or PNG files only."
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, f"{phone}_{file.filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process salary slip (simulate OCR)
        result = await dummy_services.process_salary_slip(file_path, phone)
        
        return {
            "uploaded": result["success"],
            "filename": file.filename,
            "salary": result.get("extracted_salary", 0),
            "confidence": result.get("confidence", 0),
            "message": result["message"],
            "file_path": file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/dummy-data/customers")
async def get_dummy_customers():
    """
    Get list of dummy customers for testing
    This endpoint helps developers know what phone numbers to test with
    """
    try:
        customers = dummy_services.get_dummy_customer_data()
        return {
            "message": "Dummy customer data for testing",
            "count": len(customers),
            "customers": customers,
            "note": "This is synthetic data for demonstration purposes only"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dummy data: {str(e)}")


@router.get("/external-apis/health")
async def external_apis_health():
    """Health check for all dummy external APIs"""
    return {
        "status": "healthy",
        "apis": {
            "crm_verification": "active",
            "credit_bureau": "active", 
            "offer_engine": "active",
            "salary_slip_processor": "active"
        },
        "note": "All APIs are mock/dummy implementations"
    }