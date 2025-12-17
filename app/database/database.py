"""
Database setup and configuration for the loan assistant
Uses SQLite for simplicity with dummy customer data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = "sqlite:///./loan_assistant.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


class Customer(Base):
    """Customer table with dummy data for testing"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    pan = Column(String, unique=True)
    salary = Column(Float)  # Monthly salary in INR
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LoanApplication(Base):
    """Loan application records"""
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    customer_phone = Column(String)
    loan_amount = Column(Float)
    tenure = Column(Integer)  # in months
    purpose = Column(String)
    status = Column(String)  # pending, approved, rejected
    credit_score = Column(Integer)
    pre_approved_limit = Column(Float)
    emi = Column(Float)
    interest_rate = Column(Float)
    sanction_letter_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ChatSession(Base):
    """Chat session tracking"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    customer_phone = Column(String, nullable=True)
    current_stage = Column(String, default="greeting")  # greeting, sales, verification, underwriting, decision
    context = Column(String)  # JSON string of conversation context
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create dummy data"""
    Base.metadata.create_all(bind=engine)
    
    # Create dummy customers if not exists
    db = SessionLocal()
    try:
        if db.query(Customer).count() == 0:
            dummy_customers = [
                Customer(
                    phone="9876543210",
                    name="Rajesh Kumar",
                    address="123 MG Road, Bangalore, Karnataka 560001",
                    pan="ABCDE1234F",
                    salary=75000
                ),
                Customer(
                    phone="9876543211",
                    name="Priya Sharma",
                    address="456 CP Plaza, Delhi 110001",
                    pan="FGHIJ5678K",
                    salary=45000
                ),
                Customer(
                    phone="9876543212",
                    name="Amit Patel",
                    address="789 FC Road, Pune, Maharashtra 411004",
                    pan="KLMNO9012P",
                    salary=95000
                ),
                Customer(
                    phone="9876543213",
                    name="Sneha Reddy",
                    address="321 Jubilee Hills, Hyderabad, Telangana 500033",
                    pan="QRSTU3456V",
                    salary=35000
                ),
                Customer(
                    phone="9876543214",
                    name="Vikash Singh",
                    address="654 Sector 15, Gurgaon, Haryana 122001",
                    pan="WXYZ7890A",
                    salary=120000
                ),
                Customer(
                    phone="9876543215",
                    name="Kavya Nair",
                    address="987 Marine Drive, Mumbai, Maharashtra 400002",
                    pan="BCDEF1234G",
                    salary=55000
                ),
                Customer(
                    phone="9876543216",
                    name="Rohit Agarwal",
                    address="147 Park Street, Kolkata, West Bengal 700016",
                    pan="HIJKL5678M",
                    salary=68000
                ),
                Customer(
                    phone="9876543217",
                    name="Deepika Rao",
                    address="258 Residency Road, Bangalore, Karnataka 560025",
                    pan="NOPQR9012S",
                    salary=82000
                ),
                Customer(
                    phone="9876543218",
                    name="Arjun Mehta",
                    address="369 Linking Road, Mumbai, Maharashtra 400050",
                    pan="TUVWX3456Y",
                    salary=110000
                ),
                Customer(
                    phone="9876543219",
                    name="Ananya Joshi",
                    address="741 Koramangala, Bangalore, Karnataka 560034",
                    pan="ZABCD7890E",
                    salary=40000
                )
            ]
            
            for customer in dummy_customers:
                db.add(customer)
            db.commit()
            logger.info("✅ Initialized database with 10 dummy customers")
            print("✅ Initialized database with 10 dummy customers")
    
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}", exc_info=True)
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()