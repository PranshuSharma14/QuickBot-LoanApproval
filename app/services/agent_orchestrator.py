"""
Advanced Agent Orchestrator for sophisticated multi-agent coordination
Implements advanced patterns like Agent Chain, Conditional Routing, and Context Management
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import json
import asyncio
from datetime import datetime
import uuid

from app.models.schemas import ConversationContext, ChatResponse, ChatStage


class OrchestrationPattern(Enum):
    """Orchestration patterns for different conversation flows"""
    LINEAR = "linear"           # Sequential agent execution
    CONDITIONAL = "conditional" # Conditional branching based on context
    PARALLEL = "parallel"       # Multiple agents working simultaneously
    CHAIN = "chain"            # Chain of responsibility pattern
    HYBRID = "hybrid"          # Combined/hybrid strategy
    DECISION_TREE = "tree"     # Complex decision tree routing


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class AgentOrchestrator:
    """Advanced agent orchestrator with sophisticated routing and state management"""
    
    def __init__(self):
        # Initialize agents with lazy loading to avoid circular imports
        self.agents = {}
        self._agents_initialized = False
        
        # Agent states tracking
        self.agent_states: Dict[str, AgentState] = {}
        
        # Orchestration rules and decision trees
        self.orchestration_rules = self._setup_orchestration_rules()
        
        # Context enrichment functions
        self.context_enrichers: List[Callable] = []
        
        # Performance metrics
        self.metrics = {
            "total_conversations": 0,
            "successful_approvals": 0,
            "average_response_time": 0,
            "agent_performance": {name: {"calls": 0, "success": 0} for name in self.agents.keys()}
        }
    
    def _setup_orchestration_rules(self) -> Dict[str, Any]:
        """Setup sophisticated orchestration rules and decision trees"""
        return {
            "stage_routing": {
                ChatStage.GREETING: {
                    "primary_agent": "master",
                    "pattern": OrchestrationPattern.LINEAR,
                    "context_requirements": [],
                    "fallback_agents": ["sales"]
                },
                ChatStage.SALES: {
                    "primary_agent": "sales",
                    "pattern": OrchestrationPattern.CONDITIONAL,
                    "context_requirements": ["customer_intent"],
                    "decision_tree": {
                        "amount_extraction": {"next": "sales", "confidence_threshold": 0.8},
                        "negotiation_needed": {"next": "sales", "escalation": True},
                        "complete": {"next": "verification"}
                    }
                },
                ChatStage.VERIFICATION: {
                    "primary_agent": "verification",
                    "pattern": OrchestrationPattern.CHAIN,
                    "context_requirements": ["customer_phone", "loan_request"],
                    "chain_sequence": ["verification", "underwriting"]
                },
                ChatStage.UNDERWRITING: {
                    "primary_agent": "underwriting",
                    "pattern": OrchestrationPattern.PARALLEL,
                    "context_requirements": ["customer_data", "verification_status"],
                    "parallel_tasks": ["credit_check", "offer_evaluation", "risk_assessment"]
                },
                ChatStage.DECISION: {
                    "primary_agent": "underwriting",
                    "pattern": OrchestrationPattern.CONDITIONAL,
                    "context_requirements": ["underwriting_result"],
                    "decision_tree": {
                        "sanction_letter": {"next": "master", "confidence_threshold": 0.9},
                        "loan_details": {"next": "underwriting", "confidence_threshold": 0.8},
                        "complete": {"next": "master"}
                    }
                },
                ChatStage.SALARY_SLIP: {
                    "primary_agent": "verification",
                    "pattern": OrchestrationPattern.LINEAR,
                    "context_requirements": ["underwriting_result"],
                    "fallback_agents": ["underwriting"]
                },
                ChatStage.APPROVED: {
                    "primary_agent": "master",
                    "pattern": OrchestrationPattern.LINEAR,
                    "context_requirements": ["underwriting_result"],
                    "fallback_agents": []
                },
                ChatStage.REJECTED: {
                    "primary_agent": "master",
                    "pattern": OrchestrationPattern.LINEAR,
                    "context_requirements": ["underwriting_result"],
                    "fallback_agents": []
                },
                ChatStage.COMPLETED: {
                    "primary_agent": "master",
                    "pattern": OrchestrationPattern.LINEAR,
                    "context_requirements": [],
                    "fallback_agents": []
                }
            },
            
            "confidence_thresholds": {
                "agent_handoff": 0.75,
                "escalation": 0.5,
                "fallback": 0.3
            },
            
            "escalation_paths": {
                "sales_failure": ["master", "verification"],
                "verification_failure": ["sales", "master"],
                "underwriting_failure": ["verification", "sales"]
            }
        }
    
    def _initialize_agents(self):
        """Lazy initialization of agents to avoid circular imports"""
        if not self._agents_initialized:
            from app.agents.sales_agent import SalesAgent
            from app.agents.verification_agent import VerificationAgent
            from app.agents.underwriting_agent import UnderwritingAgent
            
            self.agents = {
                "sales": SalesAgent(),
                "verification": VerificationAgent(),
                "underwriting": UnderwritingAgent()
            }
            
            # Agent states tracking
            self.agent_states = {
                name: AgentState.IDLE for name in self.agents.keys()
            }
            
            self._agents_initialized = True
    
    async def orchestrate_conversation(
        self, 
        message: str, 
        context: ConversationContext,
        orchestration_pattern: Optional[OrchestrationPattern] = None
    ) -> ChatResponse:
        """
        Main orchestration method with advanced routing logic
        """
        start_time = datetime.now()
        
        try:
            # Initialize agents if not already done
            self._initialize_agents()
            
            # Update metrics
            self.metrics["total_conversations"] += 1
            
            # Enrich context with additional data
            enriched_context = await self._enrich_context(context)
            
            # Determine orchestration strategy
            strategy = orchestration_pattern or self._determine_orchestration_strategy(enriched_context)
            
            # Execute orchestration based on strategy
            if strategy == OrchestrationPattern.LINEAR:
                response = await self._execute_linear_orchestration(message, enriched_context)
            elif strategy == OrchestrationPattern.CONDITIONAL:
                response = await self._execute_conditional_orchestration(message, enriched_context)
            elif strategy == OrchestrationPattern.PARALLEL:
                response = await self._execute_parallel_orchestration(message, enriched_context)
            elif strategy == OrchestrationPattern.CHAIN:
                response = await self._execute_chain_orchestration(message, enriched_context)
            else:
                response = await self._execute_decision_tree_orchestration(message, enriched_context)
            
            # Post-process response
            final_response = await self._post_process_response(response, enriched_context)
            
            # Update performance metrics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            self._update_metrics(final_response, response_time)
            
            return final_response
            
        except Exception as e:
            # Graceful error handling with fallback
            return await self._handle_orchestration_error(e, message, context)
    
    async def _enrich_context(self, context: ConversationContext) -> ConversationContext:
        """Enrich context with additional intelligence and metadata"""
        
        # Add conversation metadata
        context.metadata = {
            "conversation_id": context.session_id,
            "start_time": datetime.now().isoformat(),
            "agent_history": [],
            "confidence_scores": {},
            "escalation_count": 0,
            "context_enrichments": []
        }
        
        # Apply context enrichers
        for enricher in self.context_enrichers:
            try:
                context = await enricher(context)
            except Exception as e:
                print(f"Context enricher failed: {e}")
        
        # Add conversation intelligence
        await self._add_conversation_intelligence(context)
        
        return context
    
    async def _add_conversation_intelligence(self, context: ConversationContext):
        """Add intelligent analysis to conversation context"""
        
        # Analyze conversation sentiment and intent
        if context.conversation_history:
            last_messages = context.conversation_history[-5:]  # Last 5 messages
            
            # Simple intent detection
            user_messages = [msg["message"] for msg in last_messages if msg["sender"] == "user"]
            combined_text = " ".join(user_messages)
            
            # Intent scoring
            intent_scores = self._calculate_intent_scores(combined_text)
            context.metadata["intent_scores"] = intent_scores
            
            # Conversation flow analysis
            flow_analysis = self._analyze_conversation_flow(context.conversation_history)
            context.metadata["flow_analysis"] = flow_analysis
    
    def _calculate_intent_scores(self, text: str) -> Dict[str, float]:
        """Calculate intent scores based on conversation content"""
        
        intents = {
            "loan_application": ["loan", "money", "borrow", "credit", "finance"],
            "information_seeking": ["how", "what", "when", "where", "why"],
            "urgency": ["urgent", "immediate", "asap", "quick", "fast"],
            "price_sensitive": ["cheap", "affordable", "rate", "interest", "emi"],
            "trust_building": ["safe", "secure", "trust", "reliable", "guarantee"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
            scores[intent] = min(score, 1.0)
        
        return scores
    
    def _analyze_conversation_flow(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        
        if len(history) < 2:
            return {"stage": "early", "complexity": "low", "engagement": "high"}
        
        # Calculate metrics
        user_messages = [msg for msg in history if msg["sender"] == "user"]
        bot_messages = [msg for msg in history if msg["sender"] == "assistant"]
        
        avg_user_length = sum(len(msg["message"]) for msg in user_messages) / len(user_messages)
        avg_bot_length = sum(len(msg["message"]) for msg in bot_messages) / len(bot_messages)
        
        # Determine conversation characteristics
        complexity = "high" if avg_user_length > 100 else "medium" if avg_user_length > 50 else "low"
        engagement = "high" if len(history) > 10 else "medium" if len(history) > 5 else "low"
        
        return {
            "stage": "advanced" if len(history) > 10 else "developing",
            "complexity": complexity,
            "engagement": engagement,
            "user_responsiveness": avg_user_length / max(avg_bot_length, 1),
            "conversation_length": len(history)
        }
    
    def _determine_orchestration_strategy(self, context: ConversationContext) -> OrchestrationPattern:
        """Intelligently determine the best orchestration strategy"""
        
        # Get current stage rules
        stage_rules = self.orchestration_rules["stage_routing"].get(
            context.current_stage, 
            {"pattern": OrchestrationPattern.LINEAR}
        )
        
        # Check if we have metadata for intelligent routing
        if hasattr(context, 'metadata') and context.metadata:
            intent_scores = context.metadata.get("intent_scores", {})
            flow_analysis = context.metadata.get("flow_analysis", {})
            
            # Adjust strategy based on conversation intelligence
            if flow_analysis.get("complexity") == "high":
                return OrchestrationPattern.DECISION_TREE
            elif intent_scores.get("urgency", 0) > 0.7:
                return OrchestrationPattern.CHAIN
            elif flow_analysis.get("engagement") == "low":
                return OrchestrationPattern.LINEAR
        
        return stage_rules["pattern"]
    
    async def _execute_linear_orchestration(self, message: str, context: ConversationContext) -> ChatResponse:
        """Execute linear orchestration - agents in sequence"""
        
        stage_rules = self.orchestration_rules["stage_routing"].get(context.current_stage)
        primary_agent = stage_rules["primary_agent"]
        
        # Set agent state
        self.agent_states[primary_agent] = AgentState.PROCESSING
        
        try:
            # Execute primary agent
            response = await self.agents[primary_agent].process(message, context)
            
            # Update agent performance
            self.metrics["agent_performance"][primary_agent]["calls"] += 1
            self.metrics["agent_performance"][primary_agent]["success"] += 1
            
            self.agent_states[primary_agent] = AgentState.COMPLETED
            
            return response
            
        except Exception as e:
            self.agent_states[primary_agent] = AgentState.ERROR
            
            # Try fallback agents
            fallback_agents = stage_rules.get("fallback_agents", [])
            for fallback_agent in fallback_agents:
                try:
                    response = await self.agents[fallback_agent].process(message, context)
                    self.agent_states[fallback_agent] = AgentState.COMPLETED
                    return response
                except:
                    continue
            
            raise e
    
    async def _execute_conditional_orchestration(self, message: str, context: ConversationContext) -> ChatResponse:
        """Execute conditional orchestration with decision logic"""
        
        stage_rules = self.orchestration_rules["stage_routing"].get(context.current_stage)
        decision_tree = stage_rules.get("decision_tree", {})
        
        # Analyze message for routing decision
        routing_decision = await self._make_routing_decision(message, context, decision_tree)
        
        # Route to appropriate agent
        target_agent = routing_decision["next"]
        
        if routing_decision.get("escalation"):
            # Handle escalation
            context.metadata["escalation_count"] += 1
            
        return await self.agents[target_agent].process(message, context)
    
    async def _execute_parallel_orchestration(self, message: str, context: ConversationContext) -> ChatResponse:
        """Execute parallel orchestration - multiple agents simultaneously"""
        
        stage_rules = self.orchestration_rules["stage_routing"].get(context.current_stage)
        parallel_tasks = stage_rules.get("parallel_tasks", [])
        
        # Create tasks for parallel execution
        tasks = []
        
        if "credit_check" in parallel_tasks:
            tasks.append(self._execute_credit_check(context))
        
        if "offer_evaluation" in parallel_tasks:
            tasks.append(self._execute_offer_evaluation(context))
        
        if "risk_assessment" in parallel_tasks:
            tasks.append(self._execute_risk_assessment(context))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        aggregated_context = await self._aggregate_parallel_results(context, results)
        
        # Use underwriting agent to process final decision
        return await self.agents["underwriting"].process(message, aggregated_context)
    
    async def _execute_chain_orchestration(self, message: str, context: ConversationContext) -> ChatResponse:
        """Execute chain orchestration - responsibility chain pattern"""
        
        stage_rules = self.orchestration_rules["stage_routing"].get(context.current_stage)
        chain_sequence = stage_rules.get("chain_sequence", ["master"])
        
        current_response = None
        
        for agent_name in chain_sequence:
            try:
                # Each agent in chain processes and potentially modifies context
                current_response = await self.agents[agent_name].process(message, context)
                
                # Check if chain should continue or break
                if self._should_break_chain(current_response, context):
                    break
                    
            except Exception as e:
                # Chain broken, use last successful response or error
                if current_response is None:
                    raise e
                break
        
        return current_response
    
    async def _execute_decision_tree_orchestration(self, message: str, context: ConversationContext) -> ChatResponse:
        """Execute decision tree orchestration for complex routing"""
        
        # Complex decision tree logic
        decision_path = await self._traverse_decision_tree(message, context)
        
        # Execute the decided path
        for step in decision_path:
            agent_name = step["agent"]
            action = step["action"]
            
            if action == "process":
                response = await self.agents[agent_name].process(message, context)
            elif action == "validate":
                validation_result = await self._validate_context(context, step["validation_rules"])
                if not validation_result["valid"]:
                    # Handle validation failure
                    continue
            elif action == "enrich":
                context = await step["enrichment_function"](context)
        
        return response
    
    async def _make_routing_decision(self, message: str, context: ConversationContext, decision_tree: Dict) -> Dict[str, Any]:
        """Make intelligent routing decisions based on message and context"""
        
        # Simple rule-based routing for demo
        # In production, this would use more sophisticated NLP/ML
        
        message_lower = message.lower()
        
        # Check for amount extraction patterns
        if any(word in message_lower for word in ["rupees", "lakh", "crore", "₹"]):
            if "amount_extraction" in decision_tree:
                return decision_tree["amount_extraction"]
        
        # Check for negotiation patterns
        if any(word in message_lower for word in ["but", "however", "cheaper", "lower", "negotiate"]):
            if "negotiation_needed" in decision_tree:
                return decision_tree["negotiation_needed"]
        
        # Default to completion
        return decision_tree.get("complete", {"next": "master"})
    
    async def _execute_credit_check(self, context: ConversationContext) -> Dict[str, Any]:
        """Execute credit check as parallel task"""
        
        if context.customer_phone:
            from app.services.dummy_services import DummyServices
            dummy_services = DummyServices()
            
            credit_result = await dummy_services.get_credit_score(context.customer_phone)
            return {"type": "credit_check", "result": credit_result}
        
        return {"type": "credit_check", "result": None}
    
    async def _execute_offer_evaluation(self, context: ConversationContext) -> Dict[str, Any]:
        """Execute offer evaluation as parallel task"""
        
        if context.customer_phone:
            from app.services.dummy_services import DummyServices
            dummy_services = DummyServices()
            
            offer_result = await dummy_services.get_preapproved_offer(context.customer_phone)
            return {"type": "offer_evaluation", "result": offer_result}
        
        return {"type": "offer_evaluation", "result": None}
    
    async def _execute_risk_assessment(self, context: ConversationContext) -> Dict[str, Any]:
        """Execute risk assessment as parallel task"""
        
        # Simulate risk assessment
        risk_score = 0.0
        
        if context.credit_score:
            if context.credit_score > 750:
                risk_score = 0.1  # Low risk
            elif context.credit_score > 700:
                risk_score = 0.3  # Medium risk
            else:
                risk_score = 0.7  # High risk
        
        return {
            "type": "risk_assessment", 
            "result": {"risk_score": risk_score, "risk_category": "low" if risk_score < 0.2 else "medium" if risk_score < 0.5 else "high"}
        }
    
    async def _aggregate_parallel_results(self, context: ConversationContext, results: List) -> ConversationContext:
        """Aggregate results from parallel execution"""
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            if result["type"] == "credit_check" and result["result"]:
                context.credit_score = result["result"].credit_score
            elif result["type"] == "offer_evaluation" and result["result"]:
                context.pre_approved_limit = result["result"].pre_approved_limit
            elif result["type"] == "risk_assessment":
                context.metadata["risk_assessment"] = result["result"]
        
        return context
    
    def _should_break_chain(self, response: ChatResponse, context: ConversationContext) -> bool:
        """Determine if chain execution should break"""
        
        # Break chain if response is final or error
        return response.final or hasattr(response, 'error')
    
    async def _traverse_decision_tree(self, message: str, context: ConversationContext) -> List[Dict[str, Any]]:
        """Traverse complex decision tree for orchestration"""
        
        # Simplified decision tree traversal
        # In production, this would be more sophisticated
        
        decision_path = [
            {"agent": "master", "action": "validate", "validation_rules": ["session_exists"]},
            {"agent": "sales", "action": "process"},
            {"agent": "verification", "action": "process"}
        ]
        
        return decision_path
    
    async def _validate_context(self, context: ConversationContext, rules: List[str]) -> Dict[str, Any]:
        """Validate context against rules"""
        
        validation_results = {"valid": True, "failed_rules": []}
        
        for rule in rules:
            if rule == "session_exists" and not context.session_id:
                validation_results["valid"] = False
                validation_results["failed_rules"].append(rule)
            elif rule == "customer_phone_exists" and not context.customer_phone:
                validation_results["valid"] = False
                validation_results["failed_rules"].append(rule)
        
        return validation_results
    
    async def _post_process_response(self, response: ChatResponse, context: ConversationContext) -> ChatResponse:
        """Post-process response with additional intelligence"""
        
        # Add conversation metadata
        if hasattr(context, 'metadata'):
            response.metadata = {
                "orchestration_info": {
                    "agents_used": context.metadata.get("agent_history", []),
                    "confidence_scores": context.metadata.get("confidence_scores", {}),
                    "processing_time": datetime.now().isoformat()
                }
            }
        
        return response
    
    async def _handle_orchestration_error(self, error: Exception, message: str, context: ConversationContext) -> ChatResponse:
        """Handle orchestration errors gracefully"""
        
        print(f"Orchestration error: {error}")
        
        # Fallback to master agent
        try:
            return await self.agents["master"].process(message, context)
        except:
            # Ultimate fallback
            return ChatResponse(
                session_id=context.session_id or str(uuid.uuid4()),
                message="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                stage=context.current_stage,
                requires_input=True,
                final=False
            )
    
    def _update_metrics(self, response: ChatResponse, response_time: float):
        """Update performance metrics"""
        
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total_conversations = self.metrics["total_conversations"]
        
        self.metrics["average_response_time"] = (
            (current_avg * (total_conversations - 1) + response_time) / total_conversations
        )
        
        # Track successful approvals
        if "approved" in response.message.lower():
            self.metrics["successful_approvals"] += 1
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics"""
        # Ensure compatibility with tests expecting successful_routings
        successful_routings = self.metrics.get("successful_routings", 0)
        # Derive successful_routings from agent_performance if not present
        if successful_routings == 0 and isinstance(self.metrics.get("agent_performance"), dict):
            successful_routings = sum(v.get("success", 0) for v in self.metrics.get("agent_performance", {}).values())

        return {
            **self.metrics,
            "successful_routings": successful_routings,
            "approval_rate": self.metrics["successful_approvals"] / max(self.metrics["total_conversations"], 1),
            "agent_states": dict(self.agent_states)
        }