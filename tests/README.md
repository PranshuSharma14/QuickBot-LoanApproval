# NBFC Agentic AI Testing Suite

## Overview
Comprehensive testing suite for the NBFC Agentic AI Loan Sales Assistant with advanced orchestration capabilities.

## Test Structure

### 1. Test Data (`tests/dummy_data.py`)
- **8 realistic customer profiles** with different risk levels and characteristics
- **10+ conversation scenarios** covering various customer journeys  
- **Intent analysis test messages** for different customer behaviors
- **Routing test scenarios** for intelligent agent selection
- **Edge cases and error conditions** for robustness testing

### 2. Unit Tests (`tests/test_orchestration.py`)
- **MasterAgent Tests**: Basic processing, phone extraction, error handling
- **AgentOrchestrator Tests**: All orchestration patterns (Linear, Conditional, Parallel, Chain, Decision Tree)
- **IntelligentAgentRouter Tests**: All routing strategies and performance tracking
- **ConversationStateManager Tests**: State transitions, pause/resume, validation

### 3. Integration Tests (`tests/test_api.py`)
- **API Endpoint Tests**: All chat endpoints with orchestration
- **Error Handling Tests**: API-level error scenarios
- **Workflow Tests**: Complete conversation flows through API
- **Performance Tests**: Response times and concurrent requests

### 4. Load Tests (`tests/load_test.py`)
- **Realistic Load Simulation**: Multiple concurrent conversations
- **Stress Testing**: Gradual load increase to find breaking points
- **Performance Metrics**: Response times, throughput, success rates
- **Scenario-Based Testing**: Different customer journey mixes

## Test Categories

### 📋 Customer Profiles
- **Premium**: High income, excellent credit (780+ score)
- **Standard**: Middle income, good credit (720+ score)  
- **Developing**: Lower income, building credit (650+ score)
- **High Risk**: Poor credit, challenging profile (580+ score)
- **VIP**: High value customer with history
- **First Time**: New customer, no previous interactions
- **Student**: Young professional starting career
- **Senior**: Senior citizen with established profile

### 🎭 Conversation Scenarios
- **Smooth Approval**: Excellent customer, easy approval
- **Negotiation Required**: Customer wants better rates
- **Documentation Issues**: Missing or incomplete documents
- **Credit Concerns**: Credit score or history issues
- **Urgent Request**: Emergency loan needs
- **Confused Customer**: Needs education about loan process
- **Angry Customer**: Previous bad experience, needs de-escalation
- **Technical Queries**: Complex product questions
- **Complex Requirements**: Multiple conditions and special needs

### 🧠 Intelligence Testing
- **Intent Analysis**: Loan application, information seeking, urgency, price sensitivity
- **Emotional Tone**: Frustrated, excited, concerned, confused, neutral
- **Complexity Assessment**: Message length, technical terms, multiple topics
- **Context Awareness**: Previous interactions, customer profile, conversation flow

### ⚡ Performance Testing
- **Response Time**: Individual message processing speed
- **Concurrent Conversations**: Multiple users simultaneously
- **Load Scaling**: Performance under increasing load
- **Memory Stability**: Long-running conversation handling
- **Error Recovery**: System resilience and graceful degradation

## Running Tests

### Quick Start
```bash
# Setup test environment
python run_tests.py setup

# Run all tests
python run_tests.py all -v

# Check server health
python run_tests.py health
```

### Individual Test Types
```bash
# Unit tests (fast, no server required)
python run_tests.py unit -v

# Integration tests (requires mocked components)
python run_tests.py integration -v

# Performance tests (measures response times)
python run_tests.py performance -v

# Load tests (requires running server)
python run_tests.py load

# Demo (showcases all features)
python run_tests.py demo
```

### Manual Testing
```bash
# Direct pytest execution
pytest tests/test_orchestration.py -v
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test classes
pytest tests/test_orchestration.py::TestMasterAgent -v
```

## Test Data Examples

### Sample Customer
```python
{
    "name": "Rajesh Kumar",
    "phone": "9876543210", 
    "profile": "PREMIUM",
    "credit_score": 780,
    "monthly_income": 150000,
    "preferred_amount": 500000,
    "urgency_level": "medium",
    "communication_style": "professional"
}
```

### Sample Conversation Flow
```python
{
    "scenario": "SMOOTH_APPROVAL",
    "conversation_flow": [
        {"user": "Hi, I need a personal loan", "stage": "GREETING"},
        {"user": "9876543210", "stage": "SALES"},
        {"user": "I need 5 lakhs for home renovation", "stage": "SALES"},
        {"user": "Yes, I can provide all documents", "stage": "VERIFICATION"}
    ]
}
```

## Expected Test Results

### Performance Benchmarks
- **Response Time**: < 3 seconds per message
- **Concurrent Users**: 50+ simultaneous conversations
- **Success Rate**: > 95% under normal load
- **Memory Usage**: Stable over extended periods

### Orchestration Metrics
- **Route Accuracy**: > 90% optimal agent selection
- **State Transitions**: 100% validation compliance
- **Error Recovery**: Graceful handling of all edge cases
- **Load Distribution**: Even utilization across agents

## Advanced Testing Features

### 1. Scenario-Based Testing
Tests complete customer journeys from greeting to loan approval/rejection.

### 2. Intelligent Routing Validation  
Verifies that the routing algorithm selects optimal agents based on context.

### 3. Performance Profiling
Measures and analyzes system performance under various conditions.

### 4. Edge Case Coverage
Tests system behavior with malformed inputs, errors, and unusual scenarios.

### 5. Concurrent Load Simulation
Simulates realistic user behavior with multiple simultaneous conversations.

## Test Coverage Goals

- **Code Coverage**: > 85%
- **Scenario Coverage**: All major customer journeys
- **Error Path Coverage**: All error conditions and recovery paths
- **Performance Coverage**: Various load levels and usage patterns
- **Integration Coverage**: All API endpoints and orchestration flows

## Continuous Integration

The test suite is designed for CI/CD integration:
- Fast unit tests for quick feedback
- Comprehensive integration tests for release validation  
- Performance tests for regression detection
- Load tests for production readiness verification

This testing suite ensures the NBFC Agentic AI system is production-ready with enterprise-grade reliability and performance! 🚀