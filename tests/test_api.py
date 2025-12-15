"""
Integration Test Suite for API Endpoints
Tests the complete API layer with orchestration integration
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from main import app
from app.models.schemas import ChatMessage, ChatResponse, ChatStage
from tests.dummy_data import DUMMY_CUSTOMERS, TEST_CONVERSATION_SCENARIOS, ConversationScenario


class TestChatAPI:
    """Test cases for Chat API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_master_agent(self, monkeypatch):
        """Mock master agent for testing"""
        mock_agent = AsyncMock()
        
        async def mock_process(message, session_id=None, phone=None):
            return ChatResponse(
                session_id=session_id or "test_session",
                message=f"Mock response to: {message}",
                stage=ChatStage.SALES,
                requires_input=True,
                final=False
            )
        
        mock_agent.process = mock_process
        
        # Mock app state
        app.state.master_agent = mock_agent
        app.state.agent_router = MagicMock()
        app.state.orchestrator = MagicMock()
        app.state.state_manager = MagicMock()
        
        return mock_agent
    
    def test_health_check_endpoint(self, client):
        """Test the root health check endpoint"""
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active"
        assert data["version"] == "2.0.0"
        assert "features" in data
        assert "orchestration_status" in data
    
    def test_chat_endpoint_basic(self, client, mock_master_agent):
        """Test basic chat endpoint functionality"""
        
        chat_message = {
            "message": "Hello, I need a personal loan",
            "session_id": "test_basic_001",
            "phone": "9876543210"
        }
        
        response = client.post("/api/chat", json=chat_message)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "session_id" in data
        assert data["session_id"] == "test_basic_001"
        
        # Verify mock was called
        mock_master_agent.process.assert_called_once()
    
    def test_advanced_chat_endpoint(self, client, mock_master_agent):
        """Test advanced chat endpoint with orchestration"""
        
        chat_message = {
            "message": "I need an urgent loan of 5 lakhs",
            "session_id": "test_advanced_001",
            "phone": "9876543210"
        }
        
        response = client.post("/api/v2/chat", json=chat_message)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "session_id" in data
        assert data["session_id"] == "test_advanced_001"
    
    def test_chat_with_routing_strategy(self, client, mock_master_agent):
        """Test chat endpoint with explicit routing strategy"""
        
        chat_message = {
            "message": "Complex loan requirement with multiple conditions",
            "session_id": "test_routing_001",
            "phone": "9876543210"
        }
        
        response = client.post(
            "/api/v2/chat/route?routing_strategy=hybrid",
            json=chat_message
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_chat_health_endpoint(self, client, mock_master_agent):
        """Test chat health endpoint"""
        
        # Mock analytics responses
        app.state.agent_router.get_routing_analytics = MagicMock(return_value={
            "overall_analytics": {"successful_routings": 10, "average_routing_time": 1.5}
        })
        app.state.orchestrator.get_orchestration_metrics = MagicMock(return_value={
            "total_conversations": 50, "active_conversations": 5
        })
        
        response = client.get("/api/v2/chat/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "orchestration_systems" in data
        assert "performance_summary" in data
    
    def test_conversation_pause_endpoint(self, client, mock_master_agent):
        """Test conversation pause endpoint"""
        
        # Mock state manager
        app.state.state_manager.pause_conversation = AsyncMock(return_value=True)
        
        response = client.post("/api/v2/chat/conversation/pause?session_id=test_pause_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_conversation_resume_endpoint(self, client, mock_master_agent):
        """Test conversation resume endpoint"""
        
        # Mock context object
        mock_context = MagicMock()
        mock_context.current_stage = ChatStage.SALES
        mock_context.conversation_history = ["msg1", "msg2"]
        
        app.state.state_manager.resume_conversation = AsyncMock(return_value=mock_context)
        
        response = client.post("/api/v2/chat/conversation/resume?session_id=test_resume_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "context" in data
    
    def test_analytics_endpoint(self, client, mock_master_agent):
        """Test analytics endpoint"""
        
        # Mock analytics data
        mock_analytics = {
            "orchestration_metrics": {"total_conversations": 100},
            "routing_analytics": {"successful_routings": 95},
            "state_analytics": {"active_conversations": 10},
            "master_agent_analytics": {"success_rate": 0.95}
        }
        
        app.state.orchestrator.get_orchestration_metrics = MagicMock(return_value=mock_analytics["orchestration_metrics"])
        app.state.agent_router.get_routing_analytics = MagicMock(return_value=mock_analytics["routing_analytics"])
        app.state.state_manager.get_state_analytics = MagicMock(return_value=mock_analytics["state_analytics"])
        app.state.master_agent.get_orchestration_analytics = MagicMock(return_value=mock_analytics["master_agent_analytics"])
        
        response = client.get("/api/analytics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "orchestration_metrics" in data
        assert "routing_analytics" in data
        assert "state_analytics" in data
    
    def test_orchestration_settings_endpoint(self, client, mock_master_agent):
        """Test orchestration settings update endpoint"""
        
        # Mock router methods
        app.state.agent_router.adjust_routing_weights = MagicMock()
        app.state.agent_router.update_agent_availability = MagicMock()
        
        settings = {
            "routing_weights": {
                "performance": 0.5,
                "load_balance": 0.2,
                "context_match": 0.2,
                "availability": 0.1
            },
            "agent_availability": {
                "sales": True,
                "verification": False,
                "underwriting": True
            }
        }
        
        response = client.post("/api/orchestration/settings", json=settings)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Verify methods were called
        app.state.agent_router.adjust_routing_weights.assert_called_once()
        app.state.agent_router.update_agent_availability.assert_called()
    
    def test_error_handling(self, client, mock_master_agent):
        """Test API error handling"""
        
        # Test with invalid JSON
        response = client.post("/api/chat", json={"invalid": "data"})
        
        # Should handle validation error gracefully
        assert response.status_code in [422, 500]  # Validation error or handled error
        
        # Test with malformed request
        response = client.post("/api/chat", data="invalid json")
        assert response.status_code == 422
    
    def test_conversation_state_endpoint(self, client, mock_master_agent):
        """Test conversation state retrieval endpoint"""
        
        # Mock state data
        mock_state = {
            "session_id": "test_state_001",
            "status": "active",
            "current_stage": "sales",
            "message_count": 5
        }
        
        app.state.state_manager.get_conversation_state = MagicMock(return_value=mock_state)
        
        response = client.get("/api/v2/chat/conversation/test_state_001/state")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == "test_state_001"
        assert data["status"] == "active"


class TestDummyAPIs:
    """Test dummy APIs for external service simulation"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_kyc_verification_api(self, client):
        """Test KYC verification dummy API"""
        
        kyc_data = {
            "phone": "9876543210",
            "name": "Test User",
            "id_number": "ABCDE1234F"
        }
        
        response = client.post("/api/kyc/verify", json=kyc_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "verified" in data
        assert "verification_id" in data
        assert "confidence_score" in data
    
    def test_credit_bureau_api(self, client):
        """Test credit bureau dummy API"""
        
        response = client.get("/api/credit-bureau/score?phone=9876543210")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "credit_score" in data
        assert "report_date" in data
        assert "factors" in data
    
    def test_bank_verification_api(self, client):
        """Test bank account verification dummy API"""
        
        bank_data = {
            "account_number": "1234567890",
            "ifsc_code": "HDFC0001234",
            "phone": "9876543210"
        }
        
        response = client.post("/api/bank/verify", json=bank_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "verified" in data
        assert "account_holder_name" in data
        assert "balance_range" in data


class TestScenarioBasedAPIWorkflows:
    """Test complete API workflows for different scenarios"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_smooth_approval_workflow(self, client, mock_master_agent):
        """Test smooth approval workflow through API"""
        
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.SMOOTH_APPROVAL]
        session_id = "api_smooth_001"
        
        # Configure mock to return different stages
        responses = [
            ChatResponse(session_id=session_id, message="Welcome! Please share your phone number", stage=ChatStage.GREETING, requires_input=True, final=False),
            ChatResponse(session_id=session_id, message="Great! How much loan do you need?", stage=ChatStage.SALES, requires_input=True, final=False),
            ChatResponse(session_id=session_id, message="Perfect! Let's verify your details", stage=ChatStage.VERIFICATION, requires_input=True, final=False),
            ChatResponse(session_id=session_id, message="Congratulations! Loan approved", stage=ChatStage.APPROVED, requires_input=False, final=True)
        ]
        
        response_iter = iter(responses)
        mock_master_agent.process = AsyncMock(side_effect=lambda *args, **kwargs: next(response_iter))
        
        # Execute conversation flow
        for i, step in enumerate(scenario["conversation_flow"]):
            chat_message = {
                "message": step["user"],
                "session_id": session_id,
                "phone": "9876543210" if i == 1 else None
            }
            
            response = client.post("/api/v2/chat", json=chat_message)
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == session_id
    
    def test_negotiation_workflow(self, client, mock_master_agent):
        """Test negotiation workflow through API"""
        
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.NEGOTIATION_REQUIRED]
        session_id = "api_negotiation_001"
        
        # Mock negotiation responses
        negotiation_responses = [
            "I understand you're looking for competitive rates",
            "Let me check what we can offer",
            "Based on your profile, I can offer 11.5%",
            "That's our best rate for your profile"
        ]
        
        response_iter = iter([
            ChatResponse(session_id=session_id, message=msg, stage=ChatStage.SALES, requires_input=True, final=False)
            for msg in negotiation_responses
        ])
        mock_master_agent.process = AsyncMock(side_effect=lambda *args, **kwargs: next(response_iter))
        
        for step in scenario["conversation_flow"]:
            chat_message = {
                "message": step["user"],
                "session_id": session_id,
                "phone": "9876543211"
            }
            
            response = client.post("/api/v2/chat", json=chat_message)
            assert response.status_code == 200
    
    def test_error_recovery_workflow(self, client, mock_master_agent):
        """Test error recovery through API"""
        
        session_id = "api_error_001"
        
        # First call fails
        mock_master_agent.process = AsyncMock(side_effect=Exception("Test error"))
        
        chat_message = {
            "message": "Hello",
            "session_id": session_id,
            "phone": "9876543210"
        }
        
        response = client.post("/api/v2/chat", json=chat_message)
        
        # Should handle error gracefully
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        
        # Second call succeeds
        mock_master_agent.process = AsyncMock(return_value=ChatResponse(
            session_id=session_id,
            message="How can I help you?",
            stage=ChatStage.GREETING,
            requires_input=True,
            final=False
        ))
        
        response = client.post("/api/v2/chat", json=chat_message)
        assert response.status_code == 200


class TestAPIPerformance:
    """Test API performance characteristics"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_response_time(self, client, mock_master_agent):
        """Test API response time"""
        
        import time
        
        mock_master_agent.process = AsyncMock(return_value=ChatResponse(
            session_id="perf_test",
            message="Quick response",
            stage=ChatStage.GREETING,
            requires_input=True,
            final=False
        ))
        
        chat_message = {
            "message": "Performance test message",
            "session_id": "perf_test_001",
            "phone": "9876543210"
        }
        
        start_time = time.time()
        response = client.post("/api/v2/chat", json=chat_message)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # API should respond quickly (under 1 second for mocked agent)
        assert response_time < 1.0
    
    def test_concurrent_requests(self, client, mock_master_agent):
        """Test handling of concurrent API requests"""
        
        import concurrent.futures
        import threading
        
        mock_master_agent.process = AsyncMock(return_value=ChatResponse(
            session_id="concurrent_test",
            message="Concurrent response",
            stage=ChatStage.GREETING,
            requires_input=True,
            final=False
        ))
        
        def make_request(request_id):
            chat_message = {
                "message": f"Concurrent request {request_id}",
                "session_id": f"concurrent_{request_id}",
                "phone": "9876543210"
            }
            return client.post("/api/v2/chat", json=chat_message)
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])