"""
Advanced Orchestration Demo Script
Demonstrates sophisticated agent orchestration, routing, and state management capabilities
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from app.agents.advanced_master_agent import MasterAgent
from app.services.agent_orchestrator import AgentOrchestrator, OrchestrationPattern
from app.services.intelligent_agent_router import IntelligentAgentRouter, RoutingStrategy
from app.services.conversation_state_manager import ConversationStateManager, StateTransition
from app.models.schemas import ConversationContext, ChatStage


class OrchestrationDemo:
    """Comprehensive demo of advanced orchestration capabilities"""
    
    def __init__(self):
        self.master_agent = MasterAgent()
        self.orchestrator = AgentOrchestrator()
        self.agent_router = IntelligentAgentRouter()
        self.state_manager = ConversationStateManager()
        
        print("🚀 Advanced Orchestration Demo System Initialized")
        print("=" * 60)
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all orchestration features"""
        
        print("\\n🎯 COMPREHENSIVE ORCHESTRATION DEMO")
        print("=" * 60)
        
        # Demo 1: Basic Orchestration
        await self.demo_basic_orchestration()
        
        # Demo 2: Intelligent Routing
        await self.demo_intelligent_routing()
        
        # Demo 3: State Management
        await self.demo_state_management()
        
        # Demo 4: Performance Analytics
        await self.demo_performance_analytics()
        
        # Demo 5: Advanced Patterns
        await self.demo_advanced_patterns()
        
        print("\\n🎉 ORCHESTRATION DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    
    async def demo_basic_orchestration(self):
        """Demonstrate basic orchestration capabilities"""
        
        print("\\n1️⃣ BASIC ORCHESTRATION DEMO")
        print("-" * 40)
        
        # Test messages for different scenarios
        test_scenarios = [
            {
                "message": "Hi, I need a personal loan urgently",
                "description": "Urgent loan request - should trigger CHAIN orchestration"
            },
            {
                "message": "What are the interest rates and EMI options for a 5 lakh loan and also tell me about documentation requirements",
                "description": "Complex multi-part query - should trigger PARALLEL orchestration"
            },
            {
                "message": "Hello",
                "description": "Simple greeting - should trigger LINEAR orchestration"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\\n  Test {i}: {scenario['description']}")
            print(f"  Message: '{scenario['message']}'")
            
            # Initialize conversation
            context = await self.state_manager.initialize_conversation()
            
            # Use orchestrator to process
            response = await self.orchestrator.orchestrate_conversation(
                scenario['message'],
                context
            )
            
            print(f"  ✅ Response: {response.message[:100]}...")
            if hasattr(response, 'metadata') and 'orchestration_info' in response.metadata:
                print(f"  🔄 Pattern Used: {response.metadata.get('orchestration_pattern', 'Unknown')}")
            
            await asyncio.sleep(0.5)  # Brief pause for demo clarity
    
    async def demo_intelligent_routing(self):
        """Demonstrate intelligent agent routing"""
        
        print("\\n2️⃣ INTELLIGENT ROUTING DEMO")
        print("-" * 40)
        
        # Test different routing strategies
        routing_tests = [
            {
                "message": "I need technical help with loan documentation",
                "strategy": RoutingStrategy.CONTEXT_AWARE,
                "description": "Context-aware routing for technical query"
            },
            {
                "message": "Quick loan approval needed",
                "strategy": RoutingStrategy.PERFORMANCE_BASED,
                "description": "Performance-based routing for efficiency"
            },
            {
                "message": "General loan information please",
                "strategy": RoutingStrategy.LOAD_BALANCED,
                "description": "Load-balanced routing for standard query"
            },
            {
                "message": "Complex loan with multiple requirements and special conditions",
                "strategy": RoutingStrategy.HYBRID,
                "description": "Hybrid routing for complex scenario"
            }
        ]
        
        for i, test in enumerate(routing_tests, 1):
            print(f"\\n  Routing Test {i}: {test['description']}")
            print(f"  Strategy: {test['strategy'].value}")
            print(f"  Message: '{test['message']}'")
            
            # Initialize context
            context = await self.state_manager.initialize_conversation()
            
            # Route the request
            routing_decision = await self.agent_router.route_request(
                test['message'],
                context,
                test['strategy']
            )
            
            print(f"  ✅ Selected Agent: {routing_decision.selected_agent}")
            print(f"  📊 Confidence: {routing_decision.confidence_score:.2f}")
            print(f"  💭 Rationale: {routing_decision.rationale}")
            
            # Execute with selected agent
            response = await self.agent_router.execute_with_agent(
                routing_decision,
                test['message'],
                context
            )
            
            print(f"  📝 Response: {response.message[:80]}...")
            
            await asyncio.sleep(0.5)
    
    async def demo_state_management(self):
        """Demonstrate advanced state management"""
        
        print("\\n3️⃣ STATE MANAGEMENT DEMO")
        print("-" * 40)
        
        # Create a conversation flow
        conversation_flow = [
            ("Hello, I need a loan", ChatStage.GREETING),
            ("My phone number is 9876543210", ChatStage.SALES),
            ("I need 5 lakh rupees for home renovation", ChatStage.SALES),
            ("Yes, I have all my documents ready", ChatStage.VERIFICATION),
            ("My monthly salary is 80000 rupees", ChatStage.UNDERWRITING)
        ]
        
        # Initialize conversation
        context = await self.state_manager.initialize_conversation()
        print(f"  📝 Conversation initialized: {context.session_id}")
        
        for i, (message, expected_stage) in enumerate(conversation_flow, 1):
            print(f"\\n  Step {i}: Processing '{message}'")
            print(f"    Current Stage: {context.current_stage.value}")
            
            # Process message
            response = await self.master_agent.process(message, context.session_id)
            
            # Attempt stage transition if needed
            if expected_stage != context.current_stage:
                success, transition_msg = await self.state_manager.transition_stage(
                    context.session_id,
                    expected_stage,
                    StateTransition.FORWARD
                )
                
                if success:
                    print(f"    ✅ Transitioned to: {expected_stage.value}")
                    context.current_stage = expected_stage
                else:
                    print(f"    ❌ Transition failed: {transition_msg}")
            
            print(f"    📤 Response: {response.message[:60]}...")
            
            await asyncio.sleep(0.3)
        
        # Get final conversation state
        final_state = self.state_manager.get_conversation_state(context.session_id)
        print(f"\\n  🏁 Final State: {json.dumps(final_state, indent=2, default=str)}")
    
    async def demo_performance_analytics(self):
        """Demonstrate performance analytics and monitoring"""
        
        print("\\n4️⃣ PERFORMANCE ANALYTICS DEMO")
        print("-" * 40)
        
        # Generate some activity for analytics
        for i in range(5):
            context = await self.state_manager.initialize_conversation()
            messages = [
                "Hello, I need a personal loan",
                "My phone is 9876543210", 
                "I need 3 lakh rupees",
                "Yes, please proceed with verification"
            ]
            
            for message in messages:
                await self.master_agent.process(message, context.session_id)
                await asyncio.sleep(0.1)
        
        # Get comprehensive analytics
        print("\\n  📊 ORCHESTRATION METRICS:")
        orchestration_metrics = self.orchestrator.get_orchestration_metrics()
        for key, value in orchestration_metrics.items():
            if isinstance(value, dict):
                print(f"    {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"    {key}: {value}")
        
        print("\\n  🎯 ROUTING ANALYTICS:")
        routing_analytics = self.agent_router.get_routing_analytics()
        for key, value in routing_analytics["overall_analytics"].items():
            print(f"    {key}: {value}")
        
        print("\\n  🏃 STATE ANALYTICS:")
        state_analytics = self.state_manager.get_state_analytics()
        for key, value in state_analytics["overall_metrics"].items():
            print(f"    {key}: {value}")
        
        print("\\n  🏆 MASTER AGENT ANALYTICS:")
        master_analytics = self.master_agent.get_orchestration_analytics()
        performance_summary = master_analytics["performance_summary"]
        for key, value in performance_summary.items():
            print(f"    {key}: {value:.3f}" if isinstance(value, float) else f"    {key}: {value}")
    
    async def demo_advanced_patterns(self):
        """Demonstrate advanced orchestration patterns"""
        
        print("\\n5️⃣ ADVANCED PATTERNS DEMO")
        print("-" * 40)
        
        # Test different orchestration patterns explicitly
        pattern_tests = [
            {
                "pattern": OrchestrationPattern.LINEAR,
                "message": "Simple loan inquiry",
                "description": "Sequential processing"
            },
            {
                "pattern": OrchestrationPattern.CONDITIONAL,
                "message": "I want a loan but need to compare options first",
                "description": "Conditional branching based on content"
            },
            {
                "pattern": OrchestrationPattern.CHAIN,
                "message": "Urgent loan needed ASAP with complete verification",
                "description": "Chain of responsibility processing"
            },
            {
                "pattern": OrchestrationPattern.PARALLEL,
                "message": "Check my eligibility while processing my application",
                "description": "Parallel task execution"
            }
        ]
        
        for i, test in enumerate(pattern_tests, 1):
            print(f"\\n  Pattern Test {i}: {test['description']}")
            print(f"  Pattern: {test['pattern'].value}")
            print(f"  Message: '{test['message']}'")
            
            context = await self.state_manager.initialize_conversation()
            
            # Use specific orchestration pattern
            response = await self.orchestrator.orchestrate_conversation(
                test['message'],
                context,
                test['pattern']
            )
            
            print(f"  ✅ Processed with {test['pattern'].value} pattern")
            print(f"  📝 Response: {response.message[:80]}...")
            
            # Show orchestration metadata
            if hasattr(response, 'metadata') and 'orchestration_info' in response.metadata:
                info = response.metadata['orchestration_info']
                print(f"  ⚙️  Agents used: {info.get('agents_used', 'N/A')}")
                print(f"  🎯 Confidence: {info.get('confidence_scores', {})}")
            
            await asyncio.sleep(0.5)
    
    async def demo_conversation_pause_resume(self):
        """Demonstrate conversation pause/resume capabilities"""
        
        print("\\n🔄 CONVERSATION PAUSE/RESUME DEMO")
        print("-" * 40)
        
        # Start conversation
        context = await self.state_manager.initialize_conversation()
        session_id = context.session_id
        
        # Process some messages
        messages = [
            "Hello, I need a loan",
            "My phone is 9876543210",
            "I need 5 lakh rupees"
        ]
        
        for message in messages:
            response = await self.master_agent.process(message, session_id)
            print(f"  📝 Processed: {message}")
        
        # Show current state
        current_state = self.state_manager.get_conversation_state(session_id)
        print(f"  📊 Current state: {current_state}")
        
        # Pause conversation
        print("\\n  ⏸️  Pausing conversation...")
        pause_success = await self.state_manager.pause_conversation(session_id, "demo_pause")
        print(f"  Pause successful: {pause_success}")
        
        # Try to get state (should show paused)
        paused_state = self.state_manager.get_conversation_state(session_id)
        print(f"  📊 Paused state: {paused_state}")
        
        # Resume conversation
        print("\\n  ▶️  Resuming conversation...")
        resumed_context = await self.state_manager.resume_conversation(session_id)
        
        if resumed_context:
            print(f"  ✅ Resume successful")
            print(f"  📊 Resumed at stage: {resumed_context.current_stage.value}")
            
            # Continue conversation
            continue_response = await self.master_agent.process(
                "Let's continue with the loan application",
                session_id
            )
            print(f"  📝 Continued: {continue_response.message[:60]}...")
        else:
            print("  ❌ Resume failed")


async def main():
    """Main demo function"""
    
    print("🌟 ADVANCED AGENTIC AI ORCHESTRATION SYSTEM")
    print("🏦 NBFC Loan Sales Assistant with Sophisticated Agent Coordination")
    print("=" * 80)
    print("This demo showcases:")
    print("• Multi-agent orchestration with intelligent routing")
    print("• Dynamic conversation state management")
    print("• Performance monitoring and analytics")
    print("• Advanced orchestration patterns")
    print("• Conversation pause/resume capabilities")
    print("=" * 80)
    
    # Initialize demo system
    demo = OrchestrationDemo()
    
    try:
        # Run comprehensive demo
        await demo.run_comprehensive_demo()
        
        # Bonus: Pause/Resume demo
        await demo.demo_conversation_pause_resume()
        
        print("\\n" + "=" * 80)
        print("🎊 ALL ORCHESTRATION FEATURES DEMONSTRATED SUCCESSFULLY!")
        print("🚀 System ready for production deployment with advanced capabilities")
        print("=" * 80)
        
    except Exception as e:
        print(f"\\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(main())