"""
Intelligent Agent Router for dynamic agent selection and workflow management
Implements sophisticated routing algorithms and agent performance tracking
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass
import statistics

from app.models.schemas import ConversationContext, ChatResponse, ChatStage
from app.agents.sales_agent import SalesAgent
from app.agents.verification_agent import VerificationAgent
from app.agents.underwriting_agent import UnderwritingAgent


class RoutingStrategy(Enum):
    """Agent routing strategies"""
    PERFORMANCE_BASED = "performance"      # Route based on agent performance
    LOAD_BALANCED = "load_balanced"        # Distribute load evenly
    CONTEXT_AWARE = "context_aware"        # Route based on context analysis
    HYBRID = "hybrid"                      # Combination of strategies
    MACHINE_LEARNING = "ml"                # ML-based routing (future)


class AgentCapability(Enum):
    """Agent capabilities for intelligent routing"""
    CUSTOMER_ENGAGEMENT = "engagement"
    TECHNICAL_QUERIES = "technical"
    COMPLEX_NEGOTIATIONS = "negotiation"
    DOCUMENT_VERIFICATION = "verification"
    RISK_ASSESSMENT = "risk"
    EMOTIONAL_SUPPORT = "emotional"


@dataclass
class AgentPerformanceMetrics:
    """Agent performance tracking"""
    total_requests: int = 0
    successful_responses: int = 0
    average_response_time: float = 0.0
    customer_satisfaction: float = 0.0
    error_count: int = 0
    specialization_scores: Dict[AgentCapability, float] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.specialization_scores is None:
            self.specialization_scores = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class RoutingDecision:
    """Routing decision with rationale"""
    selected_agent: str
    confidence_score: float
    rationale: str
    alternative_agents: List[str]
    expected_performance: float
    routing_strategy: RoutingStrategy


class IntelligentAgentRouter:
    """
    Intelligent agent router with performance tracking and dynamic selection
    Implements sophisticated algorithms for optimal agent routing
    """
    
    def __init__(self):
        # Initialize agents
        self.agents = {
            "sales": SalesAgent(),
            "verification": VerificationAgent(),
            "underwriting": UnderwritingAgent()
        }
        
        # Performance tracking
        self.performance_metrics: Dict[str, AgentPerformanceMetrics] = {
            agent_name: AgentPerformanceMetrics() for agent_name in self.agents.keys()
        }
        
        # Agent capabilities mapping
        self.agent_capabilities = self._initialize_agent_capabilities()
        
        # Routing history and analytics
        self.routing_history: List[Dict[str, Any]] = []
        self.routing_analytics = {
            "total_routings": 0,
            "strategy_usage": {strategy: 0 for strategy in RoutingStrategy},
            "agent_utilization": {agent: 0 for agent in self.agents.keys()},
            "average_routing_time": 0.0,
            "successful_routings": 0
        }
        
        # Dynamic weights for routing algorithms
        self.routing_weights = {
            "performance": 0.4,
            "load_balance": 0.2,
            "context_match": 0.3,
            "availability": 0.1
        }
        
        # Agent availability tracking
        self.agent_availability = {agent: True for agent in self.agents.keys()}
        self.agent_load = {agent: 0 for agent in self.agents.keys()}
    
    def _initialize_agent_capabilities(self) -> Dict[str, Dict[AgentCapability, float]]:
        """Initialize agent capability scores"""
        
        return {
            "sales": {
                AgentCapability.CUSTOMER_ENGAGEMENT: 0.9,
                AgentCapability.COMPLEX_NEGOTIATIONS: 0.8,
                AgentCapability.EMOTIONAL_SUPPORT: 0.7,
                AgentCapability.TECHNICAL_QUERIES: 0.5,
                AgentCapability.DOCUMENT_VERIFICATION: 0.3,
                AgentCapability.RISK_ASSESSMENT: 0.4
            },
            "verification": {
                AgentCapability.DOCUMENT_VERIFICATION: 0.9,
                AgentCapability.TECHNICAL_QUERIES: 0.8,
                AgentCapability.RISK_ASSESSMENT: 0.7,
                AgentCapability.CUSTOMER_ENGAGEMENT: 0.6,
                AgentCapability.COMPLEX_NEGOTIATIONS: 0.4,
                AgentCapability.EMOTIONAL_SUPPORT: 0.5
            },
            "underwriting": {
                AgentCapability.RISK_ASSESSMENT: 0.9,
                AgentCapability.TECHNICAL_QUERIES: 0.8,
                AgentCapability.COMPLEX_NEGOTIATIONS: 0.7,
                AgentCapability.DOCUMENT_VERIFICATION: 0.6,
                AgentCapability.CUSTOMER_ENGAGEMENT: 0.5,
                AgentCapability.EMOTIONAL_SUPPORT: 0.4
            }
        }
    
    async def route_request(
        self,
        message: str,
        context: ConversationContext,
        routing_strategy: RoutingStrategy = RoutingStrategy.HYBRID,
        force_agent: Optional[str] = None
    ) -> RoutingDecision:
        """
        Intelligently route request to optimal agent
        """
        
        start_time = datetime.now()
        
        try:
            # Update analytics
            self.routing_analytics["total_routings"] += 1
            self.routing_analytics["strategy_usage"][routing_strategy] += 1
            
            # Force routing if specified
            if force_agent and force_agent in self.agents:
                return RoutingDecision(
                    selected_agent=force_agent,
                    confidence_score=1.0,
                    rationale=f"Forced routing to {force_agent}",
                    alternative_agents=list(self.agents.keys()),
                    expected_performance=0.8,
                    routing_strategy=routing_strategy
                )
            
            # Analyze request context and requirements
            context_analysis = await self._analyze_request_context(message, context)
            
            # Apply routing strategy
            if routing_strategy == RoutingStrategy.PERFORMANCE_BASED:
                decision = await self._performance_based_routing(context_analysis)
            elif routing_strategy == RoutingStrategy.LOAD_BALANCED:
                decision = await self._load_balanced_routing(context_analysis)
            elif routing_strategy == RoutingStrategy.CONTEXT_AWARE:
                decision = await self._context_aware_routing(context_analysis)
            elif routing_strategy == RoutingStrategy.HYBRID:
                decision = await self._hybrid_routing(context_analysis)
            else:
                # Default to hybrid
                decision = await self._hybrid_routing(context_analysis)
            
            # Update routing history
            await self._update_routing_history(decision, context_analysis, start_time)
            
            # Update agent utilization
            self.routing_analytics["agent_utilization"][decision.selected_agent] += 1
            self.agent_load[decision.selected_agent] += 1
            
            return decision
            
        except Exception as e:
            print(f"Routing error: {e}")
            # Fallback to default agent
            return RoutingDecision(
                selected_agent="sales",
                confidence_score=0.5,
                rationale=f"Fallback routing due to error: {e}",
                alternative_agents=list(self.agents.keys()),
                expected_performance=0.6,
                routing_strategy=routing_strategy
            )
    
    async def _analyze_request_context(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Analyze request context for intelligent routing"""
        
        analysis = {
            "message_length": len(message),
            "complexity_score": self._calculate_complexity_score(message),
            "emotional_tone": self._analyze_emotional_tone(message),
            "required_capabilities": await self._identify_required_capabilities(message, context),
            "urgency_level": self._assess_urgency(message),
            "context_stage": context.current_stage,
            "customer_profile": await self._analyze_customer_profile(context),
            "conversation_history_length": len(getattr(context, 'conversation_history', [])),
            "previous_agents_used": self._get_previous_agents(context)
        }
        
        return analysis
    
    def _calculate_complexity_score(self, message: str) -> float:
        """Calculate message complexity for routing decisions"""
        
        complexity_factors = {
            "length": min(len(message) / 200, 1.0) * 0.2,
            "questions": min(message.count("?") / 3, 1.0) * 0.3,
            "technical_terms": self._count_technical_terms(message) * 0.25,
            "multiple_topics": self._detect_multiple_topics(message) * 0.25
        }
        
        return sum(complexity_factors.values())
    
    def _count_technical_terms(self, message: str) -> float:
        """Count technical terms in message"""
        
        technical_terms = [
            "interest rate", "emi", "processing fee", "credit score", "cibil",
            "collateral", "guarantor", "tenure", "principal", "documentation",
            "verification", "approval", "sanction", "disbursement"
        ]
        
        message_lower = message.lower()
        count = sum(1 for term in technical_terms if term in message_lower)
        return min(count / 5, 1.0)  # Normalize to 0-1
    
    def _detect_multiple_topics(self, message: str) -> float:
        """Detect if message contains multiple topics"""
        
        topic_indicators = ["and", "also", "additionally", "furthermore", "moreover"]
        sentence_count = len(message.split("."))
        
        indicator_count = sum(1 for indicator in topic_indicators if indicator in message.lower())
        
        # Combine sentence count and topic indicators
        return min((sentence_count + indicator_count) / 5, 1.0)
    
    def _analyze_emotional_tone(self, message: str) -> str:
        """Analyze emotional tone of message"""
        
        message_lower = message.lower()
        
        # Frustrated/Angry
        if any(word in message_lower for word in ["frustrated", "angry", "upset", "terrible", "awful"]):
            return "frustrated"
        
        # Excited/Positive
        if any(word in message_lower for word in ["excited", "great", "awesome", "wonderful"]):
            return "excited"
        
        # Worried/Concerned
        if any(word in message_lower for word in ["worried", "concerned", "anxious", "nervous"]):
            return "concerned"
        
        # Confused
        if any(word in message_lower for word in ["confused", "unclear", "don't understand"]):
            return "confused"
        
        return "neutral"
    
    async def _identify_required_capabilities(self, message: str, context: ConversationContext) -> List[AgentCapability]:
        """Identify required capabilities based on message and context"""
        
        required_capabilities = []
        message_lower = message.lower()
        
        # Customer engagement
        if any(word in message_lower for word in ["help", "assistance", "support", "guide"]):
            required_capabilities.append(AgentCapability.CUSTOMER_ENGAGEMENT)
        
        # Technical queries
        if any(word in message_lower for word in ["how", "what", "technical", "process", "procedure"]):
            required_capabilities.append(AgentCapability.TECHNICAL_QUERIES)
        
        # Complex negotiations
        if any(word in message_lower for word in ["negotiate", "better rate", "discount", "lower", "reduce"]):
            required_capabilities.append(AgentCapability.COMPLEX_NEGOTIATIONS)
        
        # Document verification
        if any(word in message_lower for word in ["document", "verify", "proof", "upload", "submit"]):
            required_capabilities.append(AgentCapability.DOCUMENT_VERIFICATION)
        
        # Risk assessment
        if any(word in message_lower for word in ["eligible", "qualify", "credit", "income", "score"]):
            required_capabilities.append(AgentCapability.RISK_ASSESSMENT)
        
        # Emotional support
        emotional_tone = self._analyze_emotional_tone(message)
        if emotional_tone in ["frustrated", "concerned", "confused"]:
            required_capabilities.append(AgentCapability.EMOTIONAL_SUPPORT)
        
        return required_capabilities
    
    def _assess_urgency(self, message: str) -> float:
        """Assess urgency level of the request"""
        
        urgency_keywords = ["urgent", "immediate", "asap", "emergency", "quick", "fast", "now"]
        message_lower = message.lower()
        
        urgency_score = 0.0
        for keyword in urgency_keywords:
            if keyword in message_lower:
                urgency_score += 0.2
        
        # Check for time-sensitive indicators
        if any(phrase in message_lower for phrase in ["need today", "by tomorrow", "deadline"]):
            urgency_score += 0.4
        
        return min(urgency_score, 1.0)
    
    async def _analyze_customer_profile(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze customer profile for personalized routing"""
        
        profile = {
            "experience_level": "beginner",  # Default
            "interaction_style": "standard",
            "complexity_preference": 0.5,
            "previous_satisfaction": 0.7
        }
        
        # Analyze conversation history if available
        if hasattr(context, 'conversation_history') and context.conversation_history:
            history = context.conversation_history
            
            # Determine experience level
            if len(history) > 10:
                profile["experience_level"] = "experienced"
            elif len(history) > 5:
                profile["experience_level"] = "intermediate"
            
            # Analyze interaction style
            user_messages = [msg for msg in history if msg.get("sender") == "user"]
            if user_messages:
                avg_length = sum(len(msg["message"]) for msg in user_messages) / len(user_messages)
                profile["interaction_style"] = "detailed" if avg_length > 100 else "concise"
        
        return profile
    
    def _get_previous_agents(self, context: ConversationContext) -> List[str]:
        """Get list of previously used agents in conversation"""
        
        previous_agents = []
        
        if hasattr(context, 'conversation_history') and context.conversation_history:
            for message in context.conversation_history:
                if message.get("sender") == "assistant" and "metadata" in message:
                    agent = message["metadata"].get("agent")
                    if agent and agent not in previous_agents:
                        previous_agents.append(agent)
        
        return previous_agents
    
    async def _performance_based_routing(self, context_analysis: Dict[str, Any]) -> RoutingDecision:
        """Route based on agent performance metrics"""
        
        best_agent = None
        best_score = 0.0
        agent_scores = {}
        
        for agent_name, metrics in self.performance_metrics.items():
            # Calculate performance score
            success_rate = metrics.successful_responses / max(metrics.total_requests, 1)
            satisfaction_score = metrics.customer_satisfaction
            error_rate = 1.0 - (metrics.error_count / max(metrics.total_requests, 1))
            
            # Performance score calculation
            performance_score = (success_rate * 0.4 + satisfaction_score * 0.4 + error_rate * 0.2)
            
            agent_scores[agent_name] = performance_score
            
            if performance_score > best_score and self.agent_availability[agent_name]:
                best_score = performance_score
                best_agent = agent_name
        
        # Fallback to sales if no agent selected
        if not best_agent:
            best_agent = "sales"
            best_score = 0.6
        
        # Get alternative agents sorted by performance
        alternatives = sorted(
            [agent for agent in agent_scores.keys() if agent != best_agent],
            key=lambda x: agent_scores[x],
            reverse=True
        )
        
        return RoutingDecision(
            selected_agent=best_agent,
            confidence_score=best_score,
            rationale=f"Selected based on performance metrics (score: {best_score:.2f})",
            alternative_agents=alternatives,
            expected_performance=best_score,
            routing_strategy=RoutingStrategy.PERFORMANCE_BASED
        )
    
    async def _load_balanced_routing(self, context_analysis: Dict[str, Any]) -> RoutingDecision:
        """Route based on load balancing"""
        
        # Find agent with lowest current load
        available_agents = [agent for agent, available in self.agent_availability.items() if available]
        
        if not available_agents:
            # All agents busy, use least loaded
            best_agent = min(self.agent_load.keys(), key=lambda x: self.agent_load[x])
        else:
            best_agent = min(available_agents, key=lambda x: self.agent_load[x])
        
        current_load = self.agent_load[best_agent]
        max_load = max(self.agent_load.values()) if self.agent_load else 0
        
        # Calculate confidence based on load distribution
        confidence = 1.0 - (current_load / max(max_load, 1))
        confidence = max(confidence, 0.3)  # Minimum confidence
        
        alternatives = sorted(
            [agent for agent in self.agents.keys() if agent != best_agent],
            key=lambda x: self.agent_load[x]
        )
        
        return RoutingDecision(
            selected_agent=best_agent,
            confidence_score=confidence,
            rationale=f"Selected for load balancing (current load: {current_load})",
            alternative_agents=alternatives,
            expected_performance=0.7,
            routing_strategy=RoutingStrategy.LOAD_BALANCED
        )
    
    async def _context_aware_routing(self, context_analysis: Dict[str, Any]) -> RoutingDecision:
        """Route based on context analysis and agent capabilities"""
        
        required_capabilities = context_analysis.get("required_capabilities", [])
        stage = context_analysis.get("context_stage")
        
        agent_scores = {}
        
        for agent_name in self.agents.keys():
            score = 0.0
            
            # Score based on stage appropriateness
            if stage == ChatStage.SALES and agent_name == "sales":
                score += 0.4
            elif stage == ChatStage.VERIFICATION and agent_name == "verification":
                score += 0.4
            elif stage == ChatStage.UNDERWRITING and agent_name == "underwriting":
                score += 0.4
            
            # Score based on required capabilities
            if required_capabilities:
                capability_score = 0.0
                for capability in required_capabilities:
                    agent_capability_score = self.agent_capabilities[agent_name].get(capability, 0.0)
                    capability_score += agent_capability_score
                
                capability_score = capability_score / len(required_capabilities)
                score += capability_score * 0.6
            
            # Adjust for emotional tone
            emotional_tone = context_analysis.get("emotional_tone", "neutral")
            if emotional_tone in ["frustrated", "concerned"] and agent_name == "sales":
                score += 0.2  # Sales agent better for emotional support
            
            agent_scores[agent_name] = score
        
        # Select best agent
        best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
        best_score = agent_scores[best_agent]
        
        # Get alternatives
        alternatives = sorted(
            [agent for agent in agent_scores.keys() if agent != best_agent],
            key=lambda x: agent_scores[x],
            reverse=True
        )
        
        return RoutingDecision(
            selected_agent=best_agent,
            confidence_score=min(best_score, 1.0),
            rationale=f"Selected based on context analysis and capabilities",
            alternative_agents=alternatives,
            expected_performance=best_score,
            routing_strategy=RoutingStrategy.CONTEXT_AWARE
        )
    
    async def _hybrid_routing(self, context_analysis: Dict[str, Any]) -> RoutingDecision:
        """Hybrid routing combining multiple strategies"""
        
        # Get decisions from different strategies
        performance_decision = await self._performance_based_routing(context_analysis)
        load_decision = await self._load_balanced_routing(context_analysis)
        context_decision = await self._context_aware_routing(context_analysis)
        
        # Calculate weighted scores
        agent_scores = {}
        
        for agent_name in self.agents.keys():
            score = 0.0
            
            # Performance weight
            if performance_decision.selected_agent == agent_name:
                score += performance_decision.confidence_score * self.routing_weights["performance"]
            
            # Load balance weight
            if load_decision.selected_agent == agent_name:
                score += load_decision.confidence_score * self.routing_weights["load_balance"]
            
            # Context weight
            if context_decision.selected_agent == agent_name:
                score += context_decision.confidence_score * self.routing_weights["context_match"]
            
            # Availability weight
            if self.agent_availability[agent_name]:
                score += self.routing_weights["availability"]
            
            agent_scores[agent_name] = score
        
        # Select best agent
        best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
        best_score = agent_scores[best_agent]
        
        # Create rationale
        rationale_parts = []
        if performance_decision.selected_agent == best_agent:
            rationale_parts.append("high performance")
        if load_decision.selected_agent == best_agent:
            rationale_parts.append("optimal load")
        if context_decision.selected_agent == best_agent:
            rationale_parts.append("context match")
        
        rationale = f"Hybrid routing based on: {', '.join(rationale_parts)}"
        
        # Get alternatives
        alternatives = sorted(
            [agent for agent in agent_scores.keys() if agent != best_agent],
            key=lambda x: agent_scores[x],
            reverse=True
        )
        
        return RoutingDecision(
            selected_agent=best_agent,
            confidence_score=min(best_score, 1.0),
            rationale=rationale,
            alternative_agents=alternatives,
            expected_performance=best_score * 0.8,  # Slightly conservative
            routing_strategy=RoutingStrategy.HYBRID
        )
    
    async def execute_with_agent(self, decision: RoutingDecision, message: str, context: ConversationContext) -> ChatResponse:
        """Execute request with selected agent and track performance"""
        
        agent_name = decision.selected_agent
        agent = self.agents[agent_name]
        
        start_time = datetime.now()
        
        try:
            # Execute with selected agent
            response = await agent.process(message, context)
            
            # Track performance
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_agent_performance(agent_name, True, execution_time, response)
            
            # Add routing metadata to response
            if hasattr(response, 'metadata'):
                response.metadata.update({
                    "routing_decision": {
                        "selected_agent": agent_name,
                        "confidence_score": decision.confidence_score,
                        "rationale": decision.rationale,
                        "strategy": decision.routing_strategy.value
                    }
                })
            
            self.routing_analytics["successful_routings"] += 1
            
            return response
            
        except Exception as e:
            # Track failure
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_agent_performance(agent_name, False, execution_time)
            
            print(f"Agent execution error for {agent_name}: {e}")
            
            # Try alternative agent
            if decision.alternative_agents:
                alternative_agent = decision.alternative_agents[0]
                try:
                    response = await self.agents[alternative_agent].process(message, context)
                    return response
                except Exception as fallback_error:
                    print(f"Fallback agent {alternative_agent} also failed: {fallback_error}")
            
            # Return error response
            return ChatResponse(
                session_id=context.session_id,
                message="I apologize for the technical difficulty. Please try again.",
                stage=context.current_stage,
                requires_input=True,
                final=False
            )
    
    async def _update_agent_performance(self, agent_name: str, success: bool, execution_time: float, response: Optional[ChatResponse] = None):
        """Update agent performance metrics"""
        
        metrics = self.performance_metrics[agent_name]
        
        # Update basic metrics
        metrics.total_requests += 1
        if success:
            metrics.successful_responses += 1
        else:
            metrics.error_count += 1
        
        # Update average response time
        if metrics.average_response_time == 0:
            metrics.average_response_time = execution_time
        else:
            # Rolling average
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + execution_time) / 
                metrics.total_requests
            )
        
        metrics.last_updated = datetime.now()
        
        # Update satisfaction (simplified for demo)
        if success and response:
            # Simple satisfaction estimation based on response characteristics
            satisfaction_estimate = self._estimate_satisfaction(response)
            if metrics.customer_satisfaction == 0:
                metrics.customer_satisfaction = satisfaction_estimate
            else:
                # Rolling average
                metrics.customer_satisfaction = (
                    (metrics.customer_satisfaction * (metrics.successful_responses - 1) + satisfaction_estimate) /
                    metrics.successful_responses
                )
    
    def _estimate_satisfaction(self, response: ChatResponse) -> float:
        """Estimate customer satisfaction based on response characteristics"""
        
        satisfaction = 0.7  # Base satisfaction
        
        # Adjust based on response completeness
        if len(response.message) > 50:
            satisfaction += 0.1
        
        # Adjust based on stage progression
        if not response.requires_input or response.stage != ChatStage.GREETING:
            satisfaction += 0.1
        
        return min(satisfaction, 1.0)
    
    async def _update_routing_history(self, decision: RoutingDecision, context_analysis: Dict[str, Any], start_time: datetime):
        """Update routing history for analytics"""
        
        routing_time = (datetime.now() - start_time).total_seconds()
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "selected_agent": decision.selected_agent,
            "confidence_score": decision.confidence_score,
            "routing_strategy": decision.routing_strategy.value,
            "routing_time": routing_time,
            "context_complexity": context_analysis.get("complexity_score", 0),
            "message_length": context_analysis.get("message_length", 0),
            "required_capabilities": [cap.value for cap in context_analysis.get("required_capabilities", [])]
        }
        
        self.routing_history.append(history_entry)
        
        # Update analytics
        current_avg = self.routing_analytics["average_routing_time"]
        total_routings = self.routing_analytics["total_routings"]
        self.routing_analytics["average_routing_time"] = (
            (current_avg * (total_routings - 1) + routing_time) / total_routings
        )
        
        # Keep only last 1000 entries
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive routing analytics"""
        
        return {
            "overall_analytics": self.routing_analytics,
            "agent_performance": {
                agent: {
                    "total_requests": metrics.total_requests,
                    "success_rate": metrics.successful_responses / max(metrics.total_requests, 1),
                    "average_response_time": metrics.average_response_time,
                    "customer_satisfaction": metrics.customer_satisfaction,
                    "error_rate": metrics.error_count / max(metrics.total_requests, 1)
                } for agent, metrics in self.performance_metrics.items()
            },
            "routing_patterns": self._analyze_routing_patterns(),
            "performance_trends": self._calculate_performance_trends()
        }
    
    def _analyze_routing_patterns(self) -> Dict[str, Any]:
        """Analyze routing patterns from history"""
        
        if not self.routing_history:
            return {}
        
        # Most common routing strategy
        strategy_counts = {}
        for entry in self.routing_history:
            strategy = entry["routing_strategy"]
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        most_common_strategy = max(strategy_counts.keys(), key=lambda x: strategy_counts[x])
        
        # Average complexity by agent
        agent_complexity = {}
        for entry in self.routing_history:
            agent = entry["selected_agent"]
            complexity = entry["context_complexity"]
            
            if agent not in agent_complexity:
                agent_complexity[agent] = []
            agent_complexity[agent].append(complexity)
        
        # Calculate averages
        for agent in agent_complexity:
            agent_complexity[agent] = statistics.mean(agent_complexity[agent])
        
        return {
            "most_common_strategy": most_common_strategy,
            "strategy_distribution": strategy_counts,
            "average_complexity_by_agent": agent_complexity,
            "total_patterns_analyzed": len(self.routing_history)
        }
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        
        # Get recent performance (last 100 routings)
        recent_history = self.routing_history[-100:] if len(self.routing_history) > 100 else self.routing_history
        
        if len(recent_history) < 10:
            return {"insufficient_data": True}
        
        # Calculate trends
        routing_times = [entry["routing_time"] for entry in recent_history]
        confidence_scores = [entry["confidence_score"] for entry in recent_history]
        
        return {
            "average_routing_time_trend": statistics.mean(routing_times),
            "routing_time_consistency": statistics.stdev(routing_times) if len(routing_times) > 1 else 0,
            "average_confidence_trend": statistics.mean(confidence_scores),
            "confidence_consistency": statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0
        }
    
    def update_agent_availability(self, agent_name: str, available: bool):
        """Update agent availability status"""
        
        if agent_name in self.agent_availability:
            self.agent_availability[agent_name] = available
    
    def adjust_routing_weights(self, new_weights: Dict[str, float]):
        """Adjust routing algorithm weights dynamically"""
        
        # Validate weights
        if abs(sum(new_weights.values()) - 1.0) < 0.01:
            self.routing_weights.update(new_weights)
        else:
            print("Warning: Routing weights must sum to 1.0")
    
    async def cleanup_old_data(self, max_age_days: int = 30):
        """Clean up old routing history and performance data"""
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        # Clean routing history
        self.routing_history = [
            entry for entry in self.routing_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
        ]
        
        print(f"Cleaned up routing data older than {max_age_days} days")