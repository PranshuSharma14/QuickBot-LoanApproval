"""
Comprehensive Test Suite for NBFC Agentic AI System
Tests orchestration, agents, routing, and state management
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime

# Test imports
from app.agents.advanced_master_agent import MasterAgent
from app.services.agent_orchestrator import AgentOrchestrator, OrchestrationPattern
from app.services.intelligent_agent_router import IntelligentAgentRouter, RoutingStrategy
from app.services.conversation_state_manager import ConversationStateManager, StateTransition
from app.models.schemas import ConversationContext, ChatResponse, ChatStage, LoanRequest
from tests.dummy_data import (
    DUMMY_CUSTOMERS, TEST_CONVERSATION_SCENARIOS, ConversationScenario,
    CustomerProfile, TEST_MESSAGES, ROUTING_TEST_SCENARIOS, 
    STATE_TRANSITION_TESTS, EDGE_CASE_SCENARIOS
)


class TestMasterAgent:
    """Test cases for Advanced Master Agent"""
    
    @pytest.fixture
    def master_agent(self):
        return MasterAgent()
    
    @pytest.fixture
    def sample_context(self):
        return ConversationContext(
            session_id="test_session_001",
            current_stage=ChatStage.GREETING,
            conversation_history=[],
            customer_phone="9876543210",
            loan_request=None
        )
    
    @pytest.mark.asyncio
    async def test_basic_greeting_processing(self, master_agent, sample_context):
        """Test basic greeting message processing"""
        
        response = await master_agent.process(
            "Hello, I need a personal loan",
            session_id="test_session_001"
        )
        
        assert response is not None
        assert response.session_id == "test_session_001"
        assert "loan" in response.message.lower()
        assert response.requires_input is True
    
    @pytest.mark.asyncio
    async def test_phone_extraction(self, master_agent):
        """Test phone number extraction from messages"""
        
        phone_messages = [
            "My number is 9876543210",
            "+91 9876543210",
            "Call me at 09876543210",
            "9876543210 is my mobile"
        ]
        
        for message in phone_messages:
            response = await master_agent.process(message)
            # Should extract phone and potentially progress to sales stage
            assert response is not None
    
    @pytest.mark.asyncio
    async def test_conversation_intelligence(self, master_agent):
        """Test conversation intelligence and intent analysis"""
        
        # Test different intents
        intent_tests = [
            ("I urgently need money TODAY", "urgency"),
            ("What are your interest rates?", "information_seeking"),
            ("Your service is terrible", "frustrated"),
            ("This is awesome!", "excited")
        ]
        
        for message, expected_intent in intent_tests:
            response = await master_agent.process(message)
            assert response is not None
            # Could check response.metadata for intent analysis if implemented
    
    @pytest.mark.asyncio
    async def test_customer_profile_handling(self, master_agent):
        """Test handling of different customer profiles"""
        
        # Test with different customer profiles
        for customer in DUMMY_CUSTOMERS[:3]:  # Test first 3 customers
            response = await master_agent.process(
                f"Hi, I need a loan. My number is {customer['phone']}"
            )
            
            assert response is not None
            assert customer['phone'] in response.message or "loan" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, master_agent):
        """Test graceful error handling"""
        
        # Test with problematic inputs
        error_test_cases = [
            None,  # None input
            "",    # Empty string
            "x" * 10000,  # Very long string
            "@@##$$%%",    # Special characters
        ]
        
        for test_input in error_test_cases:
            try:
                response = await master_agent.process(test_input or "")
                assert response is not None  # Should handle gracefully
                assert "error" in response.message.lower() or "sorry" in response.message.lower()
            except Exception as e:
                # Should not throw unhandled exceptions
                pytest.fail(f"Unhandled exception for input '{test_input}': {e}")


class TestAgentOrchestrator:
    """Test cases for Agent Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator()
    
    @pytest.fixture
    def sample_context(self):
        context = ConversationContext(
            session_id="test_orch_001",
            current_stage=ChatStage.SALES,
            conversation_history=[],
            customer_phone="9876543210",
            loan_request=None
        )
        # Add metadata
        context.metadata = {
            "conversation_complexity": 0.5,
            "user_intent_analysis": {"loan_application": 0.8, "urgency": 0.3}
        }
        return context
    
    @pytest.mark.asyncio
    async def test_orchestration_patterns(self, orchestrator, sample_context):
        """Test different orchestration patterns"""
        
        patterns_to_test = [
            OrchestrationPattern.LINEAR,
            OrchestrationPattern.CONDITIONAL,
            OrchestrationPattern.HYBRID
        ]
        
        for pattern in patterns_to_test:
            response = await orchestrator.orchestrate_conversation(
                "I need a 5 lakh loan",
                sample_context,
                pattern
            )
            
            assert response is not None
            assert response.session_id == sample_context.session_id
    
    @pytest.mark.asyncio
    async def test_context_enrichment(self, orchestrator, sample_context):
        """Test context enrichment functionality"""
        
        enriched_context = await orchestrator._enrich_context(sample_context)
        
        assert hasattr(enriched_context, 'metadata')
        assert 'conversation_id' in enriched_context.metadata
        assert 'start_time' in enriched_context.metadata
        assert 'agent_history' in enriched_context.metadata
    
    @pytest.mark.asyncio
    async def test_parallel_orchestration(self, orchestrator, sample_context):
        """Test parallel orchestration capabilities"""
        
        # Set context for underwriting stage to trigger parallel processing
        sample_context.current_stage = ChatStage.UNDERWRITING
        sample_context.customer_phone = "9876543210"  # Valid customer
        
        response = await orchestrator.orchestrate_conversation(
            "Please process my application",
            sample_context,
            OrchestrationPattern.PARALLEL
        )
        
        assert response is not None
        # In parallel processing, multiple tasks should have been executed
    
    def test_orchestration_metrics(self, orchestrator):
        """Test orchestration metrics collection"""
        
        metrics = orchestrator.get_orchestration_metrics()
        
        assert "total_conversations" in metrics
        assert "successful_routings" in metrics
        assert "agent_performance" in metrics


class TestIntelligentAgentRouter:
    """Test cases for Intelligent Agent Router"""
    
    @pytest.fixture
    def agent_router(self):
        return IntelligentAgentRouter()
    
    @pytest.fixture
    def test_context(self):
        context = ConversationContext(
            session_id="router_test_001",
            current_stage=ChatStage.SALES,
            conversation_history=[],
            customer_phone="9876543210",
            loan_request=None
        )
        return context
    
    @pytest.mark.asyncio
    async def test_routing_strategies(self, agent_router, test_context):
        """Test different routing strategies"""
        
        strategies = [
            RoutingStrategy.PERFORMANCE_BASED,
            RoutingStrategy.LOAD_BALANCED,
            RoutingStrategy.CONTEXT_AWARE,
            RoutingStrategy.HYBRID
        ]
        
        for strategy in strategies:
            decision = await agent_router.route_request(
                "I need help with my loan application",
                test_context,
                strategy
            )
            
            assert decision.selected_agent in agent_router.agents
            assert 0.0 <= decision.confidence_score <= 1.0
            assert decision.routing_strategy == strategy
            assert isinstance(decision.alternative_agents, list)
    
    @pytest.mark.asyncio
    async def test_context_analysis(self, agent_router, test_context):
        """Test context analysis for routing"""
        
        test_messages = [
            ("This is urgent, I need help immediately", {"urgency": "high"}),
            ("Can you explain how EMI calculation works?", {"complexity": "medium"}),
            ("I'm frustrated with your service", {"emotional_tone": "frustrated"}),
            ("I have a very complex financial situation with multiple income sources", {"complexity": "high"})
        ]
        
        for message, expected_analysis in test_messages.items():
            context_analysis = await agent_router._analyze_request_context(message, test_context)
            
            assert "complexity_score" in context_analysis
            assert "emotional_tone" in context_analysis
            assert "required_capabilities" in context_analysis
    
    @pytest.mark.asyncio
    async def test_agent_execution(self, agent_router, test_context):
        """Test agent execution through router"""
        
        # Get routing decision
        decision = await agent_router.route_request(
            "I want to apply for a personal loan",
            test_context,
            RoutingStrategy.HYBRID
        )
        
        # Execute with selected agent
        response = await agent_router.execute_with_agent(
            decision,
            "I want to apply for a personal loan",
            test_context
        )
        
        assert response is not None
        assert response.session_id == test_context.session_id
    
    def test_performance_tracking(self, agent_router):
        """Test agent performance tracking"""
        
        # Check initial metrics
        metrics = agent_router.performance_metrics
        
        for agent_name in agent_router.agents.keys():
            assert agent_name in metrics
            assert hasattr(metrics[agent_name], 'total_requests')
            assert hasattr(metrics[agent_name], 'successful_responses')
    
    def test_routing_analytics(self, agent_router):
        """Test routing analytics"""
        
        analytics = agent_router.get_routing_analytics()
        
        assert "overall_analytics" in analytics
        assert "agent_performance" in analytics
        assert "routing_patterns" in analytics


class TestConversationStateManager:
    """Test cases for Conversation State Manager"""
    
    @pytest.fixture
    def state_manager(self):
        return ConversationStateManager()
    
    @pytest.mark.asyncio
    async def test_conversation_initialization(self, state_manager):
        """Test conversation initialization"""
        
        context = await state_manager.initialize_conversation()
        
        assert context.session_id is not None
        assert context.current_stage == ChatStage.GREETING
        assert hasattr(context, 'metadata')
        assert context.session_id in state_manager.active_conversations
    
    @pytest.mark.asyncio
    async def test_stage_transitions(self, state_manager):
        """Test stage transition logic"""
        
        # Initialize conversation
        context = await state_manager.initialize_conversation("test_state_001")
        
        # Test valid forward transition
        success, message = await state_manager.transition_stage(
            "test_state_001",
            ChatStage.SALES,
            StateTransition.FORWARD
        )
        
        assert success is True
        assert context.current_stage == ChatStage.SALES
        
        # Test invalid transition
        success, message = await state_manager.transition_stage(
            "test_state_001",
            ChatStage.APPROVED,  # Skip verification/underwriting
            StateTransition.FORWARD
        )
        
        # Should fail or require special conditions
        # Implementation depends on validation rules
    
    @pytest.mark.asyncio
    async def test_conversation_pause_resume(self, state_manager):
        """Test conversation pause and resume functionality"""
        
        # Initialize and set up conversation
        context = await state_manager.initialize_conversation("pause_test_001")
        
        # Pause conversation
        success = await state_manager.pause_conversation("pause_test_001", "testing")
        assert success is True
        assert "pause_test_001" in state_manager.paused_conversations
        assert "pause_test_001" not in state_manager.active_conversations
        
        # Resume conversation
        resumed_context = await state_manager.resume_conversation("pause_test_001")
        assert resumed_context is not None
        assert resumed_context.session_id == "pause_test_001"
        assert "pause_test_001" in state_manager.active_conversations
    
    def test_state_validation(self, state_manager):
        """Test state validation rules"""
        
        for test_case in STATE_TRANSITION_TESTS:
            # Create mock context
            context = ConversationContext(
                session_id="validation_test",
                current_stage=test_case["current_stage"],
                conversation_history=[],
                customer_phone="9876543210",
                loan_request=None
            )
            
            # This would test the internal validation logic
            # Implementation depends on specific validation rules
    
    def test_state_analytics(self, state_manager):
        """Test state analytics collection"""
        
        analytics = state_manager.get_state_analytics()
        
        assert "overall_metrics" in analytics
        assert "active_conversations" in analytics
        assert "conversation_states" in analytics


class TestScenarioBasedWorkflows:
    """Test complete conversation scenarios end-to-end"""
    
    @pytest.fixture
    def complete_system(self):
        """Setup complete system for scenario testing"""
        return {
            "master_agent": MasterAgent(),
            "orchestrator": AgentOrchestrator(),
            "router": IntelligentAgentRouter(),
            "state_manager": ConversationStateManager()
        }
    
    @pytest.mark.asyncio
    async def test_smooth_approval_scenario(self, complete_system):
        """Test smooth approval conversation scenario"""
        
        master_agent = complete_system["master_agent"]
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.SMOOTH_APPROVAL]
        
        session_id = "smooth_approval_001"
        responses = []
        
        for step in scenario["conversation_flow"]:
            response = await master_agent.process(
                step["user"],
                session_id=session_id
            )
            responses.append(response)
            
            assert response is not None
            assert response.session_id == session_id
        
        # Final response should indicate progression toward approval
        final_response = responses[-1]
        assert final_response.stage in [ChatStage.UNDERWRITING, ChatStage.APPROVED, ChatStage.VERIFICATION]
    
    @pytest.mark.asyncio
    async def test_complex_negotiation_scenario(self, complete_system):
        """Test complex negotiation scenario"""
        
        master_agent = complete_system["master_agent"]
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.NEGOTIATION_REQUIRED]
        
        session_id = "negotiation_001"
        responses = []
        
        for step in scenario["conversation_flow"]:
            response = await master_agent.process(
                step["user"],
                session_id=session_id
            )
            responses.append(response)
        
        # Should handle negotiation messages appropriately
        negotiation_responses = responses[-2:]  # Last two responses
        
        for response in negotiation_responses:
            # Should contain rate or negotiation related content
            assert any(word in response.message.lower() 
                      for word in ["rate", "offer", "consider", "best"])
    
    @pytest.mark.asyncio
    async def test_angry_customer_handling(self, complete_system):
        """Test angry customer escalation scenario"""
        
        master_agent = complete_system["master_agent"]
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.ANGRY_CUSTOMER]
        
        session_id = "angry_customer_001"
        
        # Send angry message
        response = await master_agent.process(
            "Your service is terrible, I was rejected last time",
            session_id=session_id
        )
        
        assert response is not None
        # Should contain empathetic or de-escalating language
        assert any(word in response.message.lower() 
                  for word in ["understand", "sorry", "help", "assist", "resolve"])
    
    @pytest.mark.asyncio
    async def test_documentation_issues_scenario(self, complete_system):
        """Test documentation issues handling"""
        
        master_agent = complete_system["master_agent"]
        scenario = TEST_CONVERSATION_SCENARIOS[ConversationScenario.DOCUMENTATION_ISSUES]
        
        session_id = "doc_issues_001"
        responses = []
        
        for step in scenario["conversation_flow"]:
            response = await master_agent.process(
                step["user"],
                session_id=session_id
            )
            responses.append(response)
        
        # Should provide guidance on documentation alternatives
        doc_responses = responses[-2:]
        
        for response in doc_responses:
            assert any(word in response.message.lower() 
                      for word in ["document", "alternative", "provide", "submit", "bank"])


class TestPerformanceAndLoad:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_conversations(self):
        """Test handling multiple concurrent conversations"""
        
        master_agent = MasterAgent()
        
        # Create multiple concurrent conversations
        async def single_conversation(session_id: str, message: str):
            return await master_agent.process(message, session_id=session_id)
        
        # Run 10 concurrent conversations
        tasks = []
        for i in range(10):
            task = single_conversation(
                f"concurrent_test_{i:03d}",
                f"Hello, I need a {50000 + i*10000} rupee loan"
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                pytest.fail(f"Conversation {i} failed: {response}")
            
            assert response is not None
            assert response.session_id == f"concurrent_test_{i:03d}"
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self):
        """Test response time performance"""
        
        master_agent = MasterAgent()
        
        start_time = time.time()
        response = await master_agent.process(
            "I need a 5 lakh personal loan urgently",
            session_id="performance_test"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response is not None
        assert response_time < 5.0  # Should respond within 5 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test memory usage stability over multiple requests"""
        
        master_agent = MasterAgent()
        
        # Process multiple conversations
        for i in range(100):
            response = await master_agent.process(
                f"Conversation {i}: I need a loan",
                session_id=f"memory_test_{i:03d}"
            )
            
            assert response is not None
            
            # Could add memory monitoring here if needed


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_edge_case_scenarios(self):
        """Test various edge case scenarios"""
        
        master_agent = MasterAgent()
        
        for edge_case in EDGE_CASE_SCENARIOS:
            try:
                if "messages" in edge_case:
                    # Multiple rapid messages
                    for message in edge_case["messages"]:
                        response = await master_agent.process(
                            message,
                            session_id="edge_case_test"
                        )
                        assert response is not None
                        
                        if "delay_seconds" in edge_case:
                            await asyncio.sleep(edge_case["delay_seconds"])
                else:
                    # Single message
                    response = await master_agent.process(
                        edge_case["message"],
                        session_id="edge_case_test"
                    )
                    assert response is not None
                    
            except Exception as e:
                if edge_case["expected_behavior"] == "error_handling":
                    # Expected to handle gracefully, not crash
                    assert "error" in str(e).lower() or "invalid" in str(e).lower()
                else:
                    pytest.fail(f"Unexpected error for {edge_case['name']}: {e}")
    
    @pytest.mark.asyncio
    async def test_malformed_input_handling(self):
        """Test handling of malformed inputs"""
        
        master_agent = MasterAgent()
        
        malformed_inputs = [
            {"message": None, "session_id": "test"},
            {"message": "test", "session_id": None},
            {"message": "", "session_id": ""},
            {"message": "test" * 1000, "session_id": "long_test"}
        ]
        
        for input_data in malformed_inputs:
            try:
                response = await master_agent.process(
                    input_data["message"] or "",
                    session_id=input_data["session_id"] or "fallback"
                )
                # Should handle gracefully
                assert response is not None
                
            except Exception as e:
                # Should not crash completely
                assert "error" in str(e).lower() or "invalid" in str(e).lower()


# Test configuration
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Configure pytest for async testing"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as requiring asyncio"
    )


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])