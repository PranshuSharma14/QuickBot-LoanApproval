"""
Authentication API Endpoints for Bank Portal
Handles signup, login, OTP verification, and user management
"""

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from sqlalchemy.orm import Session
import os
import uuid
import logging
import shutil

from app.database.postgres_models import (
    get_postgres_db, User, UserLoan, LoanStatus, OTPPurpose, UserStatus
)
from app.services.auth_service import (
    AuthService, UserService, OTPService, SessionService
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ========== REQUEST/RESPONSE SCHEMAS ==========

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    confirm_password: str
    residential_address: str
    aadhaar_number: str
    monthly_income: float
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('full_name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class LoginRequest(BaseModel):
    user_id: str  # Can be user_id or phone
    password: str


class OTPRequest(BaseModel):
    phone: str
    purpose: str = "login"  # login, signup, phone_verification


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str
    purpose: str = "login"


class LoginWithOTPRequest(BaseModel):
    user_id: str
    password: str


class VerifyLoginOTPRequest(BaseModel):
    phone: str
    otp: str
    session_token: str  # Temporary token from password verification
    email_verified: Optional[bool] = False  # True if OTP was verified via email (frontend)


class UserProfileResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    phone_verified: bool
    residential_address: Optional[str]
    aadhaar_masked: Optional[str]
    kyc_status: str
    status: str
    
    class Config:
        from_attributes = True


# ========== AUTHENTICATION ENDPOINTS ==========

@router.post("/signup")
async def signup(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    residential_address: str = Form(...),
    aadhaar_number: str = Form(...),
    monthly_income: float = Form(...),
    pan_number: str = Form(None),  # Optional PAN card number
    aadhaar_card: UploadFile = File(None),
    pan_card: UploadFile = File(None),  # Optional PAN card upload
    income_certificate: UploadFile = File(None),
    phone_verified: str = Form("false"),  # String from FormData - will be converted to bool
    db: Session = Depends(get_postgres_db)
):
    """
    Register new user with complete KYC details.
    Phone must be verified via OTP before signup completes.
    """
    try:
        # Convert phone_verified from string to boolean
        phone_verified_bool = str(phone_verified).lower() in ('true', '1', 'yes')
        
        # Convert monthly_income to integer to avoid floating point precision issues
        monthly_income_int = int(round(monthly_income))
        
        # Validate passwords match
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Validate PAN format if provided
        if pan_number:
            pan_number = pan_number.upper().strip()
            import re
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
                raise HTTPException(status_code=400, detail="Invalid PAN format. Must be like ABCDE1234F")
        
        # Handle Aadhaar card upload
        aadhaar_card_path = None
        if aadhaar_card and aadhaar_card.filename:
            upload_dir = "uploads/aadhaar_cards"
            os.makedirs(upload_dir, exist_ok=True)
            file_ext = os.path.splitext(aadhaar_card.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(aadhaar_card.file, buffer)
            aadhaar_card_path = file_path
        
        # Handle income certificate upload
        income_cert_path = None
        if income_certificate and income_certificate.filename:
            upload_dir = "uploads/income_certificates"
            os.makedirs(upload_dir, exist_ok=True)
            file_ext = os.path.splitext(income_certificate.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(income_certificate.file, buffer)
            income_cert_path = file_path
        
        # Handle PAN card upload
        pan_card_path = None
        if pan_card and pan_card.filename:
            upload_dir = "uploads/pan_cards"
            os.makedirs(upload_dir, exist_ok=True)
            file_ext = os.path.splitext(pan_card.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(pan_card.file, buffer)
            pan_card_path = file_path
        
        # Create user with all KYC details
        user, message = UserService.create_user(
            db=db,
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
            residential_address=residential_address,
            aadhaar_number=aadhaar_number,
            aadhaar_card_path=aadhaar_card_path,
            monthly_income=monthly_income_int,  # Use converted int value
            income_certificate_path=income_cert_path,
            pan_number=pan_number,
            pan_card_path=pan_card_path,
            phone_verified=phone_verified_bool  # Use converted bool value
        )
        
        if not user:
            raise HTTPException(status_code=400, detail=message)
        
        # If phone was already verified, don't need to send OTP
        if phone_verified_bool:
            return {
                "success": True,
                "message": "Account created successfully! You can now login.",
                "user_id": user.user_id,
                "phone_masked": AuthService.mask_phone(user.phone),
                "requires_otp_verification": False
            }
        
        # Send OTP for phone verification
        otp, otp_message = OTPService.create_otp(
            db=db,
            phone=user.phone,
            purpose=OTPPurpose.SIGNUP,
            user_id=str(user.id)
        )
        
        return {
            "success": True,
            "message": "Account created. Please verify your phone number.",
            "user_id": user.user_id,
            "phone_masked": AuthService.mask_phone(user.phone),
            "requires_otp_verification": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-otp")
async def send_otp(
    request: OTPRequest,
    db: Session = Depends(get_postgres_db)
):
    """Send OTP to phone number"""
    try:
        # Validate phone
        valid, phone = AuthService.validate_phone(request.phone)
        if not valid:
            raise HTTPException(status_code=400, detail=phone)
        
        # Map purpose string to enum
        purpose_map = {
            "login": OTPPurpose.LOGIN,
            "signup": OTPPurpose.SIGNUP,
            "phone_verification": OTPPurpose.PHONE_VERIFICATION
        }
        purpose = purpose_map.get(request.purpose, OTPPurpose.LOGIN)
        
        # For login, verify user exists
        if purpose == OTPPurpose.LOGIN:
            user = UserService.get_user_by_phone(db, phone)
            if not user:
                raise HTTPException(status_code=404, detail="No account found with this phone number")
        
        # Create and send OTP
        otp, message = OTPService.create_otp(db, phone, purpose)
        
        if not otp:
            raise HTTPException(status_code=429, detail=message)
        
        return {
            "success": True,
            "message": f"OTP sent to {AuthService.mask_phone(phone)}",
            "expires_in_seconds": 300  # 5 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send OTP error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-otp")
async def verify_otp(
    request: OTPVerifyRequest,
    db: Session = Depends(get_postgres_db)
):
    """Verify OTP for phone verification (signup flow)"""
    try:
        # Validate phone
        valid, phone = AuthService.validate_phone(request.phone)
        if not valid:
            raise HTTPException(status_code=400, detail=phone)
        
        # Map purpose
        purpose_map = {
            "login": OTPPurpose.LOGIN,
            "signup": OTPPurpose.SIGNUP,
            "phone_verification": OTPPurpose.PHONE_VERIFICATION
        }
        purpose = purpose_map.get(request.purpose, OTPPurpose.SIGNUP)
        
        # Verify OTP
        verified, message = OTPService.verify_otp(db, phone, request.otp, purpose)
        
        if not verified:
            raise HTTPException(status_code=400, detail=message)
        
        # If signup/phone verification, update user phone_verified status
        if purpose in [OTPPurpose.SIGNUP, OTPPurpose.PHONE_VERIFICATION]:
            user = UserService.get_user_by_phone(db, phone)
            if user:
                UserService.update_phone_verified(db, str(user.id), True)
        
        return {
            "success": True,
            "message": "Phone verified successfully",
            "phone_verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify OTP error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_postgres_db)
):
    """
    Step 1 of login: Verify credentials.
    Returns phone number for OTP verification.
    """
    try:
        # Find user by user_id or phone
        user = UserService.get_user_by_user_id(db, request.user_id)
        if not user:
            # Try phone number
            valid, phone = AuthService.validate_phone(request.user_id)
            if valid:
                user = UserService.get_user_by_phone(db, phone)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid User ID or Phone number")
        
        # Check if account is blocked
        if user.status == UserStatus.BLOCKED:
            raise HTTPException(status_code=403, detail="Account is blocked. Please contact support.")
        
        # Verify password
        if not AuthService.verify_password(request.password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.BLOCKED
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Generate temporary session token for OTP verification step
        temp_token = AuthService.generate_session_token()
        
        # Note: OTP is generated and sent by frontend via EmailJS
        # Backend no longer generates OTP for login - email verification is handled client-side
        logger.info(f"Login credentials verified for user: {user.user_id}, awaiting email OTP verification")
        
        # Mask email for display
        email_parts = user.email.split('@')
        email_masked = f"{email_parts[0][:3]}***@{email_parts[1]}" if len(email_parts) == 2 else user.email
        
        return {
            "success": True,
            "message": f"OTP will be sent to {email_masked}",
            "phone_masked": AuthService.mask_phone(user.phone),
            "phone": user.phone,  # For OTP verification
            "email": user.email,  # For email OTP
            "email_masked": email_masked,
            "temp_token": temp_token,
            "requires_otp": True,
            "user_id": user.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-login")
async def verify_login_otp(
    request: VerifyLoginOTPRequest,
    req: Request,
    db: Session = Depends(get_postgres_db)
):
    """
    Step 2 of login: Verify OTP and create session.
    Returns JWT token for authenticated requests.
    """
    try:
        # Validate phone
        valid, phone = AuthService.validate_phone(request.phone)
        if not valid:
            raise HTTPException(status_code=400, detail=phone)
        
        # Skip backend OTP verification if already verified via email (frontend EmailJS)
        if not request.email_verified:
            # Verify OTP from backend storage
            verified, message = OTPService.verify_otp(db, phone, request.otp, OTPPurpose.LOGIN)
            
            if not verified:
                raise HTTPException(status_code=400, detail=message)
        else:
            logger.info(f"OTP verified via email for phone: {AuthService.mask_phone(phone)}")
        
        # Get user
        user = UserService.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create session
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent")
        
        session, jwt_token = SessionService.create_session(db, user, ip_address, user_agent)
        
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return {
            "success": True,
            "message": "Login successful",
            "token": jwt_token,
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_masked": AuthService.mask_phone(user.phone)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_postgres_db)
):
    """Logout and invalidate session"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Extract token
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        # Verify token
        payload = AuthService.verify_jwt_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Invalidate session
        SessionService.invalidate_session(db, payload.get("session_id"))
        
        return {"success": True, "message": "Logged out successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_postgres_db)
):
    """Get current logged-in user profile"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        payload = AuthService.verify_jwt_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = UserService.get_user_by_user_id(db, payload.get("user_id"))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "phone_masked": AuthService.mask_phone(user.phone),
                "phone_verified": user.phone_verified,
                "residential_address": user.residential_address,
                "aadhaar_masked": AuthService.mask_aadhaar(user.aadhaar_number) if user.aadhaar_number else None,
                "monthly_income": float(user.monthly_income) if user.monthly_income else None,
                "kyc_status": user.kyc_status.value if user.kyc_status else "not_started",
                "status": user.status.value if user.status else "pending"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========== HELPER DEPENDENCY ==========

async def get_current_user_from_token(
    authorization: str = Header(None),
    db: Session = Depends(get_postgres_db)
) -> User:
    """Dependency to get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    payload = AuthService.verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = UserService.get_user_by_user_id(db, payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
