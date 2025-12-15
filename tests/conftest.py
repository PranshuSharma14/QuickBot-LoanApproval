"""
Test Configuration and Setup
"""

import pytest
import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure pytest for async testing
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as requiring asyncio"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "load: mark test as load test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case test"
    )


# Common test fixtures
@pytest.fixture
def sample_customer():
    """Sample customer data for testing"""
    return {
        "id": 999,
        "name": "Test Customer",
        "phone": "9999999999",
        "email": "test@example.com",
        "credit_score": 750,
        "monthly_income": 100000,
        "employment_type": "Salaried",
        "company": "Test Company",
        "preferred_amount": 500000
    }


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing"""
    return "test_session_12345"