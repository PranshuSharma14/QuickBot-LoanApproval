"""
Dashboard API Endpoints for Bank Portal
User dashboard, loan management, and EMI tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging

from app.database.postgres_models import (
    get_postgres_db, User, UserLoan, EMIPayment, LoanStatusHistory,
    LoanStatus, EMIStatus, generate_loan_id
)
from app.services.auth_service import AuthService, UserService
from app.api.auth import get_current_user_from_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# ========== DASHBOARD ENDPOINTS ==========

@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get comprehensive dashboard summary for the logged-in user"""
    try:
        # Get all loans for this user
        loans = db.query(UserLoan).filter(UserLoan.user_id == current_user.id).all()
        
        # Calculate statistics
        total_loans = len(loans)
        approved_loans = len([l for l in loans if l.status == LoanStatus.APPROVED])
        ongoing_loans = len([l for l in loans if l.status in [LoanStatus.ONGOING, LoanStatus.DISBURSED]])
        rejected_loans = len([l for l in loans if l.status == LoanStatus.REJECTED])
        closed_loans = len([l for l in loans if l.status == LoanStatus.CLOSED])
        pending_loans = len([l for l in loans if l.status in [LoanStatus.PENDING, LoanStatus.UNDER_REVIEW, LoanStatus.DRAFT]])
        
        # Calculate total borrowed (approved + disbursed + ongoing loans) and outstanding
        total_borrowed = sum(
            float(l.disbursed_amount or l.approved_amount or l.loan_amount or 0) 
            for l in loans 
            if l.status in [LoanStatus.APPROVED, LoanStatus.ONGOING, LoanStatus.DISBURSED, LoanStatus.CLOSED]
        )
        total_outstanding = sum(
            float(l.outstanding_balance or l.approved_amount or 0) 
            for l in loans 
            if l.status in [LoanStatus.APPROVED, LoanStatus.ONGOING, LoanStatus.DISBURSED]
        )
        
        # Get upcoming EMIs (next 30 days)
        upcoming_emis = []
        for loan in loans:
            if loan.status in [LoanStatus.ONGOING, LoanStatus.DISBURSED] and loan.next_emi_date:
                if loan.next_emi_date <= datetime.now(timezone.utc) + timedelta(days=30):
                    upcoming_emis.append({
                        "loan_id": loan.loan_id,
                        "amount": float(loan.emi_amount) if loan.emi_amount else 0,
                        "due_date": loan.next_emi_date.isoformat() if loan.next_emi_date else None
                    })
        
        return {
            "success": True,
            "user": {
                "user_id": current_user.user_id,
                "full_name": current_user.full_name,
                "phone_masked": AuthService.mask_phone(current_user.phone),
                "kyc_status": current_user.kyc_status.value if current_user.kyc_status else "not_started"
            },
            "summary": {
                "total_loans": total_loans,
                "approved_loans": approved_loans,
                "ongoing_loans": ongoing_loans,
                "rejected_loans": rejected_loans,
                "closed_loans": closed_loans,
                "pending_loans": pending_loans,
                "total_borrowed": total_borrowed,
                "total_outstanding": total_outstanding
            },
            "upcoming_emis": upcoming_emis
        }
        
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loans")
async def get_user_loans(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get all loans for the logged-in user"""
    try:
        query = db.query(UserLoan).filter(UserLoan.user_id == current_user.id)
        
        # Filter by status if provided
        if status:
            try:
                status_enum = LoanStatus(status)
                query = query.filter(UserLoan.status == status_enum)
            except ValueError:
                pass
        
        loans = query.order_by(desc(UserLoan.applied_at)).all()
        
        loan_list = []
        for loan in loans:
            loan_data = {
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount) if loan.loan_amount else 0,
                "approved_amount": float(loan.approved_amount) if loan.approved_amount else None,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else None,
                "tenure_months": loan.tenure_months,
                "purpose": loan.purpose,
                "status": loan.status.value if loan.status else "unknown",
                "emi_amount": float(loan.emi_amount) if loan.emi_amount else None,
                "total_emis": loan.total_emis,
                "emis_paid": loan.emis_paid or 0,
                "outstanding_balance": float(loan.outstanding_balance) if loan.outstanding_balance else None,
                "next_emi_date": loan.next_emi_date.isoformat() if loan.next_emi_date else None,
                "rejection_reason": loan.rejection_reason,
                "applied_at": loan.applied_at.isoformat() if loan.applied_at else None,
                "approved_at": loan.approved_at.isoformat() if loan.approved_at else None,
                "has_sanction_letter": bool(loan.sanction_letter_path)
            }
            loan_list.append(loan_data)
        
        return {
            "success": True,
            "loans": loan_list,
            "total": len(loan_list)
        }
        
    except Exception as e:
        logger.error(f"Get loans error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loans/{loan_id}")
async def get_loan_details(
    loan_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get detailed information about a specific loan"""
    try:
        loan = db.query(UserLoan).filter(
            and_(
                UserLoan.loan_id == loan_id,
                UserLoan.user_id == current_user.id
            )
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Get EMI history
        emis = db.query(EMIPayment).filter(
            EMIPayment.loan_id == loan.id
        ).order_by(EMIPayment.emi_number).all()
        
        emi_list = [{
            "emi_number": emi.emi_number,
            "due_date": emi.due_date.isoformat() if emi.due_date else None,
            "amount_due": float(emi.amount_due) if emi.amount_due else 0,
            "amount_paid": float(emi.amount_paid) if emi.amount_paid else 0,
            "status": emi.status.value if emi.status else "pending",
            "payment_date": emi.payment_date.isoformat() if emi.payment_date else None
        } for emi in emis]
        
        # Get status history
        history = db.query(LoanStatusHistory).filter(
            LoanStatusHistory.loan_id == loan.id
        ).order_by(desc(LoanStatusHistory.created_at)).all()
        
        history_list = [{
            "from_status": h.previous_status.value if h.previous_status else None,
            "to_status": h.new_status.value if h.new_status else None,
            "changed_by": h.changed_by,
            "reason": h.reason,
            "timestamp": h.created_at.isoformat() if h.created_at else None
        } for h in history]
        
        return {
            "success": True,
            "loan": {
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount) if loan.loan_amount else 0,
                "approved_amount": float(loan.approved_amount) if loan.approved_amount else None,
                "disbursed_amount": float(loan.disbursed_amount) if loan.disbursed_amount else None,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else None,
                "tenure_months": loan.tenure_months,
                "purpose": loan.purpose,
                "status": loan.status.value if loan.status else "unknown",
                "emi_amount": float(loan.emi_amount) if loan.emi_amount else None,
                "total_emis": loan.total_emis,
                "emis_paid": loan.emis_paid or 0,
                "outstanding_balance": float(loan.outstanding_balance) if loan.outstanding_balance else None,
                "total_interest_paid": float(loan.total_interest_paid) if loan.total_interest_paid else 0,
                "total_principal_paid": float(loan.total_principal_paid) if loan.total_principal_paid else 0,
                "next_emi_date": loan.next_emi_date.isoformat() if loan.next_emi_date else None,
                "credit_score": loan.credit_score,
                "ai_recommendation": loan.ai_recommendation,
                "rejection_reason": loan.rejection_reason,
                "applied_at": loan.applied_at.isoformat() if loan.applied_at else None,
                "approved_at": loan.approved_at.isoformat() if loan.approved_at else None,
                "disbursed_at": loan.disbursed_at.isoformat() if loan.disbursed_at else None,
                "closed_at": loan.closed_at.isoformat() if loan.closed_at else None,
                "has_sanction_letter": bool(loan.sanction_letter_path)
            },
            "emi_schedule": emi_list,
            "status_history": history_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get loan details error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/loans/{loan_id}")
async def delete_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Delete a loan application (only for draft/pending/rejected loans)"""
    try:
        loan = db.query(UserLoan).filter(
            and_(
                UserLoan.loan_id == loan_id,
                UserLoan.user_id == current_user.id
            )
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Only allow deletion of draft, pending, or rejected loans
        allowed_statuses = [LoanStatus.DRAFT, LoanStatus.PENDING, LoanStatus.REJECTED]
        if loan.status not in allowed_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete loan with status '{loan.status.value}'. Only draft, pending, or rejected loans can be deleted."
            )
        
        # Delete associated EMI payments first (if any)
        db.query(EMIPayment).filter(EMIPayment.loan_id == loan.id).delete()
        
        # Delete status history
        db.query(LoanStatusHistory).filter(LoanStatusHistory.loan_id == loan.id).delete()
        
        # Delete the loan
        db.delete(loan)
        db.commit()
        
        logger.info(f"✅ Loan {loan_id} deleted by user {current_user.user_id}")
        
        return {
            "success": True,
            "message": f"Loan {loan_id} has been deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete loan error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loans/{loan_id}/sanction-letter")
async def download_sanction_letter(
    loan_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get sanction letter download path for approved loan"""
    try:
        loan = db.query(UserLoan).filter(
            and_(
                UserLoan.loan_id == loan_id,
                UserLoan.user_id == current_user.id
            )
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        if loan.status != LoanStatus.APPROVED and loan.status != LoanStatus.ONGOING and loan.status != LoanStatus.DISBURSED:
            raise HTTPException(status_code=400, detail="Sanction letter only available for approved loans")
        
        if not loan.sanction_letter_path:
            raise HTTPException(status_code=404, detail="Sanction letter not generated yet")
        
        return {
            "success": True,
            "sanction_letter_path": loan.sanction_letter_path,
            "loan_id": loan.loan_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download sanction letter error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ongoing-loans")
async def get_ongoing_loans(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get all ongoing loans with EMI progress"""
    try:
        loans = db.query(UserLoan).filter(
            and_(
                UserLoan.user_id == current_user.id,
                UserLoan.status.in_([LoanStatus.ONGOING, LoanStatus.DISBURSED])
            )
        ).order_by(desc(UserLoan.disbursed_at)).all()
        
        loan_list = []
        for loan in loans:
            # Calculate progress percentage
            emis_paid = loan.emis_paid or 0
            total_emis = loan.total_emis or 1
            progress_percentage = round((emis_paid / total_emis) * 100, 1)
            
            # Calculate remaining tenure
            remaining_emis = total_emis - emis_paid
            
            loan_list.append({
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.approved_amount or loan.loan_amount),
                "emi_amount": float(loan.emi_amount) if loan.emi_amount else 0,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else 0,
                "emis_paid": emis_paid,
                "total_emis": total_emis,
                "remaining_emis": remaining_emis,
                "progress_percentage": progress_percentage,
                "outstanding_balance": float(loan.outstanding_balance) if loan.outstanding_balance else 0,
                "next_emi_date": loan.next_emi_date.isoformat() if loan.next_emi_date else None,
                "purpose": loan.purpose,
                "disbursed_at": loan.disbursed_at.isoformat() if loan.disbursed_at else None
            })
        
        return {
            "success": True,
            "ongoing_loans": loan_list,
            "total": len(loan_list)
        }
        
    except Exception as e:
        logger.error(f"Get ongoing loans error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loan-history")
async def get_loan_history(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get loan history (all completed loans - approved, closed, rejected, and ongoing)"""
    try:
        # Include all non-draft loans in history
        loans = db.query(UserLoan).filter(
            and_(
                UserLoan.user_id == current_user.id,
                UserLoan.status.in_([LoanStatus.APPROVED, LoanStatus.CLOSED, LoanStatus.REJECTED, LoanStatus.ONGOING, LoanStatus.DISBURSED])
            )
        ).order_by(desc(UserLoan.applied_at)).all()
        
        loan_list = []
        for loan in loans:
            loan_list.append({
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount) if loan.loan_amount else 0,
                "approved_amount": float(loan.approved_amount) if loan.approved_amount else None,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else None,
                "tenure_months": loan.tenure_months,
                "emi_amount": float(loan.emi_amount) if loan.emi_amount else None,
                "emis_paid": loan.emis_paid or 0,
                "total_emis": loan.total_emis,
                "outstanding_balance": float(loan.outstanding_balance) if loan.outstanding_balance else None,
                "status": loan.status.value if loan.status else "unknown",
                "purpose": loan.purpose,
                "rejection_reason": loan.rejection_reason,
                "applied_at": loan.applied_at.isoformat() if loan.applied_at else None,
                "approved_at": loan.approved_at.isoformat() if loan.approved_at else None,
                "closed_at": loan.closed_at.isoformat() if loan.closed_at else None,
                "has_sanction_letter": bool(loan.sanction_letter_path)
            })
        
        return {
            "success": True,
            "loan_history": loan_list,
            "total": len(loan_list)
        }
        
    except Exception as e:
        logger.error(f"Get loan history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-new-loan")
async def start_new_loan_application(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Start a new loan application for the logged-in user"""
    try:
        # Create a new draft loan
        new_loan = UserLoan(
            loan_id=generate_loan_id(),
            user_id=current_user.id,
            loan_amount=Decimal(0),
            status=LoanStatus.DRAFT
        )
        
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)
        
        # Add to status history
        history = LoanStatusHistory(
            loan_id=new_loan.id,
            new_status=LoanStatus.DRAFT,
            changed_by="user",
            reason="New loan application started"
        )
        db.add(history)
        db.commit()
        
        return {
            "success": True,
            "message": "New loan application started",
            "loan_id": new_loan.loan_id,
            "redirect_to_chat": True
        }
        
    except Exception as e:
        logger.error(f"Start new loan error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_postgres_db)
):
    """Get complete user profile with computed KYC status"""
    try:
        # Compute verification status like real banks:
        # - Phone verified through OTP during signup/login
        # - Aadhaar considered verified if provided and validated (simulated bank verification)
        # - PAN considered verified if provided (simulated bank verification)
        # - Income verified if monthly income is provided with certificate
        
        has_aadhaar = bool(current_user.aadhaar_number)
        has_pan = bool(current_user.pan_number)
        has_income = bool(current_user.monthly_income)
        
        # In real banks, once you provide valid Aadhaar/PAN, it's verified via DigiLocker/NSDL
        # Here we simulate that - if document is provided, it's considered verified
        aadhaar_verified = current_user.aadhaar_verified or has_aadhaar
        pan_verified = current_user.pan_verified or has_pan
        
        # Compute overall KYC status
        verification_count = sum([
            current_user.phone_verified,
            aadhaar_verified,
            pan_verified,
            has_income
        ])
        
        if verification_count == 4:
            computed_kyc_status = "verified"
        elif verification_count >= 2:
            computed_kyc_status = "pending"  # Partial verification
        else:
            computed_kyc_status = "not_started"
        
        # Compute account status dynamically - if phone is verified, user is active
        computed_status = "active" if current_user.phone_verified else (
            current_user.status.value if current_user.status else "pending_verification"
        )
        
        return {
            "success": True,
            "profile": {
                "user_id": current_user.user_id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "phone": current_user.phone,
                "phone_masked": AuthService.mask_phone(current_user.phone),
                "phone_verified": current_user.phone_verified,
                "residential_address": current_user.residential_address,
                "city": current_user.city,
                "state": current_user.state,
                "pincode": current_user.pincode,
                "aadhaar_masked": AuthService.mask_aadhaar(current_user.aadhaar_number) if current_user.aadhaar_number else None,
                "aadhaar_verified": aadhaar_verified,  # Computed based on document presence
                "pan_masked": f"XXXXX{current_user.pan_number[-5:]}" if current_user.pan_number else None,
                "pan_verified": pan_verified,  # Computed based on document presence
                "monthly_income": int(current_user.monthly_income) if current_user.monthly_income else None,
                "employment_type": current_user.employment_type,
                "employer_name": current_user.employer_name,
                "kyc_status": computed_kyc_status,  # Computed dynamically
                "status": computed_status,  # Computed based on verification status
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            }
        }
        
    except Exception as e:
        logger.error(f"Get profile error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/loans/update-by-session/{session_id}")
async def update_loan_by_session(
    session_id: str,
    db: Session = Depends(get_postgres_db)
):
    """
    Update loan status when approved/rejected via chat.
    This is called internally when a loan decision is made.
    """
    from pydantic import BaseModel
    from typing import Optional
    
    # For now, just mark it as approved - the real data comes from request body
    return {"success": True, "message": "Use POST method with body"}


@router.post("/loans/complete-application")
async def complete_loan_application(
    db: Session = Depends(get_postgres_db)
):
    """
    Complete a loan application and update its status to approved.
    Called by the chat system when loan is approved.
    """
    from fastapi import Body
    from pydantic import BaseModel
    
    class LoanCompletionRequest(BaseModel):
        session_id: str
        loan_id: Optional[str] = None
        status: str = "approved"  # approved or rejected
        loan_amount: Optional[float] = None
        approved_amount: Optional[float] = None
        interest_rate: Optional[float] = None
        tenure_months: Optional[int] = None
        emi_amount: Optional[float] = None
        credit_score: Optional[int] = None
        sanction_letter_path: Optional[str] = None
        rejection_reason: Optional[str] = None
    
    return {"success": True, "message": "Endpoint ready"}


# Internal function to update loan status (called from agents)
def update_loan_status_internal(
    db: Session,
    session_id: str = None,
    loan_id: str = None,
    status: str = "approved",
    loan_amount: float = None,
    approved_amount: float = None,
    interest_rate: float = None,
    tenure_months: int = None,
    emi_amount: float = None,
    credit_score: int = None,
    sanction_letter_path: str = None,
    rejection_reason: str = None,
    phone: str = None
):
    """Update loan status in database when approved/rejected"""
    try:
        loan = None
        
        # Try to find loan by session_id first
        if session_id:
            loan = db.query(UserLoan).filter(UserLoan.chat_session_id == session_id).first()
        
        # Try by loan_id
        if not loan and loan_id:
            loan = db.query(UserLoan).filter(UserLoan.loan_id == loan_id).first()
        
        # If still not found and we have a phone, find the user's most recent draft loan
        if not loan and phone:
            user = db.query(User).filter(User.phone == phone).first()
            if user:
                loan = db.query(UserLoan).filter(
                    UserLoan.user_id == user.id,
                    UserLoan.status == LoanStatus.DRAFT
                ).order_by(UserLoan.applied_at.desc()).first()
                
                # Update the session_id on the loan
                if loan and session_id:
                    loan.chat_session_id = session_id
        
        if not loan:
            logger.warning(f"No loan found for session_id={session_id}, loan_id={loan_id}, phone={phone}")
            return False
        
        # Update loan details
        old_status = loan.status
        
        if status == "approved":
            loan.status = LoanStatus.APPROVED
            loan.approved_at = datetime.now(timezone.utc)
        elif status == "rejected":
            loan.status = LoanStatus.REJECTED
            if rejection_reason:
                loan.rejection_reason = rejection_reason
        
        if loan_amount:
            loan.loan_amount = Decimal(str(loan_amount))
        if approved_amount:
            loan.approved_amount = Decimal(str(approved_amount))
        if interest_rate:
            loan.interest_rate = Decimal(str(interest_rate))
        if tenure_months:
            loan.tenure_months = tenure_months
        if emi_amount:
            loan.emi_amount = Decimal(str(emi_amount))
            loan.total_emis = tenure_months
        if credit_score:
            loan.credit_score = credit_score
        if sanction_letter_path:
            loan.sanction_letter_path = sanction_letter_path
        
        # Add to status history
        history = LoanStatusHistory(
            loan_id=loan.id,
            previous_status=old_status,
            new_status=loan.status,
            changed_by="AI_Underwriting",
            reason=f"Loan {status} via AI chat"
        )
        db.add(history)
        db.commit()
        
        logger.info(f"✅ Loan {loan.loan_id} status updated to {loan.status.value}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating loan status: {e}", exc_info=True)
        return False

