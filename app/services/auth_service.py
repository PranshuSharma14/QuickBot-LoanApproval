"""
Authentication Service for Bank Portal
Handles user registration, login, OTP verification, and session management
"""

import hashlib
import secrets
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import jwt
import os
import re

from app.database.postgres_models import (
    User, OTPRecord, UserSession, UserStatus, OTPPurpose, KYCStatus,
    generate_user_id
)

# Firebase handles OTP via frontend - no SMS service needed

logger = logging.getLogger(__name__)

# Security Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "quickloan-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
OTP_EXPIRE_MINUTES = 5
OTP_MAX_ATTEMPTS = 3
OTP_RATE_LIMIT_MINUTES = 1  # Minimum gap between OTP requests


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, stored_hash = password_hash.split(":")
            computed_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
            return computed_hash == stored_hash
        except:
            return False
    
    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash OTP for secure storage"""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def create_jwt_token(user_id: str, session_id: str) -> str:
        """Create JWT access token"""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate Indian phone number"""
        # Remove spaces and country code
        phone = phone.replace(" ", "").replace("+91", "").replace("-", "")
        if len(phone) == 10 and phone.isdigit() and phone[0] in "6789":
            return True, phone
        return False, "Invalid phone number. Must be 10 digits starting with 6, 7, 8, or 9"
    
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> Tuple[bool, str]:
        """Validate Aadhaar number format"""
        aadhaar = aadhaar.replace(" ", "").replace("-", "")
        if len(aadhaar) == 12 and aadhaar.isdigit():
            return True, aadhaar
        return False, "Invalid Aadhaar number. Must be 12 digits"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, email.lower()
        return False, "Invalid email format"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number for display: XXXXXX1234"""
        if len(phone) >= 10:
            return f"XXXXXX{phone[-4:]}"
        return phone
    
    @staticmethod
    def mask_aadhaar(aadhaar: str) -> str:
        """Mask Aadhaar for display: XXXX XXXX 1234"""
        if len(aadhaar) >= 12:
            return f"XXXX XXXX {aadhaar[-4:]}"
        return aadhaar


class UserService:
    """User management service"""
    
    @staticmethod
    def check_user_exists(db: Session, phone: str = None, email: str = None, aadhaar: str = None) -> Optional[User]:
        """Check if user exists by phone, email, or aadhaar"""
        conditions = []
        if phone:
            conditions.append(User.phone == phone)
        if email:
            conditions.append(User.email == email.lower())
        if aadhaar:
            conditions.append(User.aadhaar_number == aadhaar)
        
        if conditions:
            return db.query(User).filter(or_(*conditions)).first()
        return None
    
    @staticmethod
    def get_user_by_user_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by their user_id (QL123456 format)"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """Get user by phone number"""
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    def get_user_by_id(db: Session, id: str) -> Optional[User]:
        """Get user by UUID"""
        return db.query(User).filter(User.id == id).first()
    
    @staticmethod
    def create_user(
        db: Session,
        full_name: str,
        email: str,
        phone: str,
        password: str,
        residential_address: str = None,
        aadhaar_number: str = None,
        aadhaar_card_path: str = None,
        monthly_income: float = None,
        income_certificate_path: str = None,
        pan_number: str = None,
        pan_card_path: str = None,
        phone_verified: bool = False
    ) -> Tuple[Optional[User], str]:
        """Create new user account with full KYC details"""
        try:
            # Validate inputs
            valid, phone = AuthService.validate_phone(phone)
            if not valid:
                return None, phone
            
            valid, email = AuthService.validate_email(email)
            if not valid:
                return None, email
            
            if aadhaar_number:
                valid, aadhaar_number = AuthService.validate_aadhaar(aadhaar_number)
                if not valid:
                    return None, aadhaar_number
            
            # Check if user already exists
            existing = UserService.check_user_exists(db, phone=phone, email=email, aadhaar=aadhaar_number)
            if existing:
                if existing.phone == phone:
                    return None, "Phone number already registered"
                if existing.email == email:
                    return None, "Email already registered"
                if aadhaar_number and existing.aadhaar_number == aadhaar_number:
                    return None, "Aadhaar already registered"
            
            # Determine KYC status based on documents provided
            kyc_status = KYCStatus.NOT_STARTED
            if aadhaar_number and pan_number:
                kyc_status = KYCStatus.VERIFIED if phone_verified else KYCStatus.PENDING
            elif aadhaar_number:
                kyc_status = KYCStatus.PENDING
            
            # Create user with all details
            user = User(
                user_id=generate_user_id(),
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=AuthService.hash_password(password),
                residential_address=residential_address,
                aadhaar_number=aadhaar_number,
                aadhaar_card_path=aadhaar_card_path,
                aadhaar_verified=bool(aadhaar_number),  # Consider verified if provided (bank verification)
                pan_number=pan_number,
                pan_verified=bool(pan_number),  # Consider verified if provided (NSDL verification)
                monthly_income=monthly_income,
                income_certificate_path=income_certificate_path,
                phone_verified=phone_verified,  # Set from OTP verification
                status=UserStatus.ACTIVE if phone_verified else UserStatus.PENDING_VERIFICATION,
                kyc_status=kyc_status
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"✅ Created new user: {user.user_id}")
            
            # Note: Welcome SMS is handled via Firebase or can be added later
            # User gets their credentials on the signup success screen
            
            return user, "User created successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating user: {e}", exc_info=True)
            return None, f"Error creating user: {str(e)}"
    
    @staticmethod
    def update_phone_verified(db: Session, user_id: str, verified: bool = True) -> bool:
        """Update phone verification status"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.phone_verified = verified
            if verified:
                user.status = UserStatus.ACTIVE
            db.commit()
            return True
        return False


class OTPService:
    """OTP management service with rate limiting"""
    
    @staticmethod
    def can_send_otp(db: Session, phone: str, purpose: OTPPurpose) -> Tuple[bool, str]:
        """Check if OTP can be sent (rate limiting)"""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=OTP_RATE_LIMIT_MINUTES)
        # For SQLite compatibility, also check with naive datetime
        cutoff_naive = datetime.utcnow() - timedelta(minutes=OTP_RATE_LIMIT_MINUTES)
        
        recent_otp = db.query(OTPRecord).filter(
            and_(
                OTPRecord.phone == phone,
                OTPRecord.purpose == purpose
            )
        ).order_by(OTPRecord.created_at.desc()).first()
        
        if recent_otp:
            created = recent_otp.created_at
            # Handle timezone-naive datetime from SQLite
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            time_since_created = (now - created).total_seconds()
            
            if time_since_created < OTP_RATE_LIMIT_MINUTES * 60:
                wait_seconds = int(OTP_RATE_LIMIT_MINUTES * 60 - time_since_created)
                return False, f"Please wait {wait_seconds} seconds before requesting another OTP"
        
        return True, "OK"
    
    @staticmethod
    def create_otp(db: Session, phone: str, purpose: OTPPurpose, user_id: str = None) -> Tuple[str, str]:
        """Create new OTP for phone number"""
        # Check rate limit
        can_send, message = OTPService.can_send_otp(db, phone, purpose)
        if not can_send:
            return None, message
        
        # Generate OTP
        otp = AuthService.generate_otp()
        otp_hash = AuthService.hash_otp(otp)
        
        # Invalidate previous OTPs for same phone and purpose
        db.query(OTPRecord).filter(
            and_(
                OTPRecord.phone == phone,
                OTPRecord.purpose == purpose,
                OTPRecord.is_verified == False
            )
        ).delete()
        
        # Create new OTP record
        otp_record = OTPRecord(
            user_id=user_id,
            phone=phone,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
        )
        
        db.add(otp_record)
        db.commit()
        
        logger.info(f"📱 OTP created for {AuthService.mask_phone(phone)}: {otp}")
        print(f"📱 OTP for {phone}: {otp}")  # For development - visible in console
        
        # Note: OTP is now sent via Firebase Phone Auth on the frontend
        # This backend OTP is kept for fallback/verification purposes
        
        return otp, "OTP sent successfully"
    
    @staticmethod
    def verify_otp(db: Session, phone: str, otp: str, purpose: OTPPurpose) -> Tuple[bool, str]:
        """Verify OTP"""
        otp_record = db.query(OTPRecord).filter(
            and_(
                OTPRecord.phone == phone,
                OTPRecord.purpose == purpose,
                OTPRecord.is_verified == False
            )
        ).order_by(OTPRecord.created_at.desc()).first()
        
        if not otp_record:
            return False, "No OTP found. Please request a new one"
        
        # Check expiry
        if otp_record.is_expired:
            return False, "OTP has expired. Please request a new one"
        
        # Check attempts
        if otp_record.attempts >= otp_record.max_attempts:
            return False, "Maximum attempts exceeded. Please request a new OTP"
        
        # Verify OTP
        otp_record.attempts += 1
        
        if AuthService.hash_otp(otp) == otp_record.otp_hash:
            otp_record.is_verified = True
            otp_record.verified_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"✅ OTP verified for {AuthService.mask_phone(phone)}")
            return True, "OTP verified successfully"
        
        db.commit()
        remaining = otp_record.max_attempts - otp_record.attempts
        return False, f"Invalid OTP. {remaining} attempts remaining"


class SessionService:
    """User session management"""
    
    @staticmethod
    def create_session(db: Session, user: User, ip_address: str = None, user_agent: str = None) -> Tuple[UserSession, str]:
        """Create new user session after successful authentication"""
        try:
            # Create session
            session_token = AuthService.generate_session_token()
            session = UserSession(
                user_id=user.id,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            db.add(session)
            
            # Update user last login
            user.last_login = datetime.now(timezone.utc)
            user.failed_login_attempts = 0
            
            db.commit()
            db.refresh(session)
            
            # Generate JWT token
            jwt_token = AuthService.create_jwt_token(str(user.user_id), str(session.id))
            
            logger.info(f"✅ Session created for user {user.user_id}")
            return session, jwt_token
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating session: {e}", exc_info=True)
            return None, str(e)
    
    @staticmethod
    def get_active_session(db: Session, session_id: str) -> Optional[UserSession]:
        """Get active session by ID"""
        return db.query(UserSession).filter(
            and_(
                UserSession.id == session_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.now(timezone.utc)
            )
        ).first()
    
    @staticmethod
    def invalidate_session(db: Session, session_id: str) -> bool:
        """Invalidate/logout session"""
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def invalidate_all_sessions(db: Session, user_id: str) -> int:
        """Invalidate all sessions for a user (logout everywhere)"""
        count = db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).update({"is_active": False})
        db.commit()
        return count
    
    @staticmethod
    def refresh_session(db: Session, session_id: str) -> bool:
        """Extend session expiry"""
        session = SessionService.get_active_session(db, session_id)
        if session:
            session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
            return True
        return False
