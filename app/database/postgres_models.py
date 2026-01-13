"""
PostgreSQL Database Models for Bank Portal
Comprehensive user, loan, and EMI tracking system
Supports both PostgreSQL and SQLite (demo mode)
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime, 
    Text, ForeignKey, Enum as SQLEnum, Numeric, Index, TypeDecorator
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone, timedelta
import uuid
import os
import enum
import logging

logger = logging.getLogger(__name__)


# Custom UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type"""
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value)) if value else None
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value) if isinstance(value, str) else value
        return value


# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL Database URL from environment - fallback to SQLite for demo
DATABASE_URL = os.getenv("DATABASE_URL", None)
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "quickloan_users.db")

# Check if we should use PostgreSQL or SQLite fallback
USE_SQLITE_FALLBACK = not DATABASE_URL or "postgresql" not in DATABASE_URL


def resolve_neon_host(url: str) -> str:
    """
    Resolve Neon hostname using Google DNS if system DNS fails.
    Returns URL with IP and endpoint parameter for SNI.
    """
    import socket
    import re
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        # Try system DNS first
        try:
            socket.setdefaulttimeout(3)
            ip = socket.gethostbyname(hostname)
            logger.info(f"✅ DNS resolved {hostname} -> {ip}")
            return url  # System DNS works, use original URL
        except socket.gaierror:
            logger.warning(f"⚠️ System DNS failed for {hostname}, using Google DNS...")
        
        # Use dnspython for Google DNS resolution
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '8.8.4.4']
            resolver.timeout = 5
            resolver.lifetime = 10
            answers = resolver.resolve(hostname, 'A')
            ip = str(answers[0])
            logger.info(f"✅ Google DNS resolved {hostname} -> {ip}")
            
            # Extract endpoint ID from hostname (e.g., ep-cold-snow-ahaotf2r)
            endpoint_match = re.match(r'^(ep-[a-z]+-[a-z]+-[a-z0-9]+)', hostname)
            endpoint_id = endpoint_match.group(1) if endpoint_match else None
            
            # Reconstruct URL with IP and endpoint parameter
            new_netloc = f"{parsed.username}:{parsed.password}@{ip}:{parsed.port or 5432}"
            query_params = dict(parse_qs(parsed.query))
            query_params['sslmode'] = ['require']
            if endpoint_id:
                query_params['options'] = [f'endpoint={endpoint_id}']
            
            new_query = urlencode({k: v[0] for k, v in query_params.items()})
            new_url = urlunparse((parsed.scheme, new_netloc, parsed.path, '', new_query, ''))
            
            logger.info(f"🔄 Using resolved URL with IP: {ip}")
            return new_url
            
        except ImportError:
            logger.warning("⚠️ dnspython not installed, trying direct IP connection")
            # Fallback: use known Neon IPs
            neon_ips = ['98.89.62.209', '23.21.74.185', '18.215.6.120']
            for ip in neon_ips:
                try:
                    socket.create_connection((ip, 5432), timeout=5)
                    endpoint_match = re.match(r'^(ep-[a-z]+-[a-z]+-[a-z0-9]+)', hostname)
                    endpoint_id = endpoint_match.group(1) if endpoint_match else None
                    
                    new_netloc = f"{parsed.username}:{parsed.password}@{ip}:{parsed.port or 5432}"
                    query_params = {'sslmode': 'require'}
                    if endpoint_id:
                        query_params['options'] = f'endpoint={endpoint_id}'
                    new_query = urlencode(query_params)
                    new_url = urlunparse((parsed.scheme, new_netloc, parsed.path, '', new_query, ''))
                    logger.info(f"✅ Connected via fallback IP: {ip}")
                    return new_url
                except:
                    continue
            raise Exception("All Neon IPs unreachable")
            
    except Exception as e:
        logger.error(f"❌ DNS resolution failed: {e}")
        return url  # Return original URL as last resort


def create_sqlite_engine():
    """Create SQLite engine as fallback"""
    sqlite_url = f"sqlite:///{SQLITE_PATH}"
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

def test_postgres_connection(pg_engine):
    """Test if PostgreSQL connection works"""
    try:
        with pg_engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection test failed: {e}")
        return False

if USE_SQLITE_FALLBACK:
    # Use SQLite for demo mode
    engine = create_sqlite_engine()
    logger.info(f"📦 Using SQLite database for demo mode: {SQLITE_PATH}")
else:
    # Try Neon PostgreSQL (or any PostgreSQL) for production
    # Resolve DNS issues for Neon
    if "neon.tech" in DATABASE_URL:
        logger.info("🚀 Detected Neon PostgreSQL - configuring for serverless")
        DATABASE_URL = resolve_neon_host(DATABASE_URL)
    
    engine_args = {
        "pool_pre_ping": True,
        "pool_size": 3,
        "max_overflow": 5,
        "pool_recycle": 300,
        "connect_args": {"connect_timeout": 15}  # 15 second timeout for Neon cold starts
    }
    
    try:
        engine = create_engine(DATABASE_URL, **engine_args)
        # Test the connection immediately
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        logger.info("🐘 Using PostgreSQL database (Neon serverless)" if "neon.tech" in DATABASE_URL else "🐘 Using PostgreSQL database")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        logger.info("📦 Falling back to SQLite database for demo mode")
        engine = create_sqlite_engine()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


# ========== ENUMS ==========

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"


class LoanStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    ONGOING = "ongoing"
    CLOSED = "closed"
    DEFAULTED = "defaulted"


class EMIStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"


class OTPPurpose(str, enum.Enum):
    LOGIN = "login"
    SIGNUP = "signup"
    RESET_PASSWORD = "reset_password"
    PHONE_VERIFICATION = "phone_verification"


class KYCStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ========== MODELS ==========

class User(Base):
    """User account table - stores all registered users"""
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), unique=True, nullable=False, index=True)  # Human-readable ID like "QL123456"
    
    # Personal Details
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    phone_verified = Column(Boolean, default=False)
    
    # Address
    residential_address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # KYC Details
    aadhaar_number = Column(String(12), unique=True, nullable=True)  # Stored encrypted
    aadhaar_card_path = Column(String(500))  # Uploaded Aadhaar card image/PDF
    aadhaar_verified = Column(Boolean, default=False)
    pan_number = Column(String(10), unique=True, nullable=True)
    pan_verified = Column(Boolean, default=False)
    kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.NOT_STARTED)
    
    # Financial Details
    monthly_income = Column(Numeric(15, 2))
    income_certificate_path = Column(String(500))
    employment_type = Column(String(50))  # salaried, self_employed, business
    employer_name = Column(String(200))
    
    # Account Security
    password_hash = Column(String(255), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    loans = relationship("UserLoan", back_populates="user", lazy="dynamic")
    otp_records = relationship("OTPRecord", back_populates="user", lazy="dynamic")
    sessions = relationship("UserSession", back_populates="user", lazy="dynamic")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_phone_email', 'phone', 'email'),
    )


class OTPRecord(Base):
    """OTP verification records with rate limiting"""
    __tablename__ = "otp_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    phone = Column(String(15), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)  # Stored as hash
    purpose = Column(SQLEnum(OTPPurpose), nullable=False)
    
    # OTP Lifecycle
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True))
    
    # Relationship
    user = relationship("User", back_populates="otp_records")
    
    @property
    def is_expired(self):
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        # Handle both timezone-aware and naive datetimes (SQLite doesn't store timezone)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires


class UserSession(Base):
    """Active user sessions for security tracking"""
    __tablename__ = "user_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    
    # Session Details
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    device_info = Column(String(200))
    
    # Session Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", back_populates="sessions")


class UserLoan(Base):
    """User loan applications - one user can have multiple loans"""
    __tablename__ = "user_loans"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    loan_id = Column(String(20), unique=True, nullable=False, index=True)  # Like "QL-LN-123456"
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Loan Details
    loan_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2))
    interest_rate = Column(Numeric(5, 2))
    tenure_months = Column(Integer)
    purpose = Column(String(100))
    
    # EMI Details
    emi_amount = Column(Numeric(15, 2))
    total_emis = Column(Integer)
    emis_paid = Column(Integer, default=0)
    next_emi_date = Column(DateTime(timezone=True))
    
    # Balances
    disbursed_amount = Column(Numeric(15, 2))
    outstanding_balance = Column(Numeric(15, 2))
    total_interest_paid = Column(Numeric(15, 2), default=0)
    total_principal_paid = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.DRAFT)
    rejection_reason = Column(Text)
    
    # AI Processing
    credit_score = Column(Integer)
    ai_recommendation = Column(Text)
    underwriting_notes = Column(Text)
    
    # Documents
    sanction_letter_path = Column(String(500))
    agreement_path = Column(String(500))
    
    # Chat Session Link
    chat_session_id = Column(String(100))
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    approved_at = Column(DateTime(timezone=True))
    disbursed_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="loans")
    emi_payments = relationship("EMIPayment", back_populates="loan", lazy="dynamic")
    status_history = relationship("LoanStatusHistory", back_populates="loan", lazy="dynamic")


class EMIPayment(Base):
    """EMI payment tracking for each loan"""
    __tablename__ = "emi_payments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    loan_id = Column(GUID(), ForeignKey("user_loans.id"), nullable=False)
    
    # EMI Details
    emi_number = Column(Integer, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    amount_due = Column(Numeric(15, 2), nullable=False)
    principal_component = Column(Numeric(15, 2))
    interest_component = Column(Numeric(15, 2))
    
    # Payment Details
    amount_paid = Column(Numeric(15, 2), default=0)
    payment_date = Column(DateTime(timezone=True))
    payment_mode = Column(String(50))  # auto_debit, upi, netbanking, etc.
    transaction_id = Column(String(100))
    
    # Status
    status = Column(SQLEnum(EMIStatus), default=EMIStatus.PENDING)
    late_fee = Column(Numeric(10, 2), default=0)
    
    # Relationship
    loan = relationship("UserLoan", back_populates="emi_payments")


class LoanStatusHistory(Base):
    """Audit trail for loan status changes"""
    __tablename__ = "loan_status_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    loan_id = Column(GUID(), ForeignKey("user_loans.id"), nullable=False)
    
    previous_status = Column(SQLEnum(LoanStatus))
    new_status = Column(SQLEnum(LoanStatus), nullable=False)
    changed_by = Column(String(100))  # user, system, agent_name
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    loan = relationship("UserLoan", back_populates="status_history")


# ========== DATABASE FUNCTIONS ==========

def reconnect_engine():
    """Attempt to reconnect to PostgreSQL with fresh DNS resolution"""
    global engine, SessionLocal
    
    if USE_SQLITE_FALLBACK:
        return  # SQLite doesn't need reconnection
    
    try:
        # Re-resolve DNS and reconnect
        db_url = os.getenv("DATABASE_URL", "")
        if "neon.tech" in db_url:
            db_url = resolve_neon_host(db_url)
        
        engine_args = {
            "pool_pre_ping": True,
            "pool_size": 3,
            "max_overflow": 5,
            "pool_recycle": 300,
            "connect_args": {"connect_timeout": 15}
        }
        
        new_engine = create_engine(db_url, **engine_args)
        with new_engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        
        engine = new_engine
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("🔄 Database reconnected successfully")
    except Exception as e:
        logger.error(f"❌ Reconnection failed: {e}")


def get_postgres_db():
    """Dependency to get PostgreSQL database session with retry logic"""
    import time
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection with a simple query
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            try:
                yield db
            finally:
                db.close()
            return
        except Exception as e:
            if "could not translate host name" in str(e) or "Name or service not known" in str(e):
                logger.warning(f"⚠️ DNS resolution failed (attempt {attempt + 1}/{max_retries}), retrying...")
                if attempt < max_retries - 1:
                    reconnect_engine()
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ All connection attempts failed")
                    raise
            else:
                raise


def init_postgres_db():
    """Initialize PostgreSQL database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL database tables created successfully")
        print("✅ PostgreSQL database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating PostgreSQL tables: {e}", exc_info=True)
        print(f"❌ Error creating PostgreSQL tables: {e}")
        return False


def get_db_session_with_retry():
    """Get a database session with automatic retry on connection failures"""
    import time
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            if "could not translate host name" in str(e) or "Name or service not known" in str(e):
                logger.warning(f"⚠️ DNS resolution failed (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    reconnect_engine()
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
            else:
                raise
    return None


def generate_user_id():
    """Generate unique user ID like QL123456"""
    import random
    return f"QL{random.randint(100000, 999999)}"


def generate_loan_id():
    """Generate unique loan ID like QL-LN-123456"""
    import random
    return f"QL-LN-{random.randint(100000, 999999)}"
