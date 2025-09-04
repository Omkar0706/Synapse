# orchestrator/langgraph_orchestrator.py - Fixed Version
from datetime import datetime
from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict
from agents.service_agents import GrabFoodAgent, GrabExpressAgent, CustomerServiceAgent
from core.llm_manager import LMStudioManager, ModelCapability
import asyncio

class LogisticsState(TypedDict):
    disruption: Dict[str, Any]
    current_agent: str
    agent_responses: List[Dict[str, Any]]
    final_solution: Dict[str, Any]
    escalation_needed: bool
    confidence_score: float
    conversation_history: List[Dict[str, Any]]

class LogisticsOrchestrator:
    def __init__(self, config, llm_manager=None):
        self.config = config
        # Use provided LLM manager or create new one
        self.llm_manager = llm_manager or LMStudioManager(config)
        self.agents = self._initialize_agents()
        self.graph = self._build_workflow_graph()
    
    def _initialize_agents(self):
        """Initialize agents directly instead of using factory"""
        return {
            "grabfood": GrabFoodAgent(self.llm_manager),
            "grabexpress": GrabExpressAgent(self.llm_manager),
            "customer_service": CustomerServiceAgent(self.llm_manager)
        }
    
    def _build_workflow_graph(self):
        workflow = StateGraph(LogisticsState)
        
        # Add nodes
        workflow.add_node("disruption_analysis", self.analyze_disruption)
        workflow.add_node("route_to_specialist", self.route_to_specialist)
        workflow.add_node("execute_specialist_task", self.execute_specialist_task)
        workflow.add_node("validate_solution", self.validate_solution)
        workflow.add_node("customer_communication", self.handle_customer_communication)
        workflow.add_node("escalate_to_human", self.escalate_to_human)
        workflow.add_node("finalize_solution", self.finalize_solution)
        
        # Add edges
        workflow.add_edge("disruption_analysis", "route_to_specialist")
        workflow.add_edge("route_to_specialist", "execute_specialist_task")
        workflow.add_edge("execute_specialist_task", "validate_solution")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "validate_solution",
            self._should_escalate,
            {
                "escalate": "escalate_to_human",
                "communicate": "customer_communication",
                "retry": "execute_specialist_task"
            }
        )
        
        workflow.add_edge("customer_communication", "finalize_solution")
        workflow.add_edge("escalate_to_human", END)
        workflow.add_edge("finalize_solution", END)
        
        workflow.set_entry_point("disruption_analysis")
        return workflow.compile()
    
    async def analyze_disruption(self, state: LogisticsState) -> LogisticsState:
        """Initial disruption analysis and classification"""
        disruption = state["disruption"]
        
        analysis_prompt = f"""
        Analyze this logistics disruption and classify it:
        
        Disruption Report: {disruption.get('description')}
        Service Type: {disruption.get('service_type')}
        Location: {disruption.get('location')}
        Urgency: {disruption.get('urgency', 'medium')}
        Reporter: {disruption.get('reported_by')}
        
        Classify this disruption and determine:
        1. Primary service affected (GrabFood, GrabExpress, GrabCar)
        2. Complexity level (low, medium, high)
        3. Required expertise areas
        4. Estimated resolution time
        5. Customer impact severity
        """
        
        try:
            analysis = await self.llm_manager.generate_response(
                analysis_prompt, ModelCapability.REASONING
            )
        except Exception as e:
            # Fallback analysis if LLM fails
            analysis = {
                "content": f"Basic analysis: {disruption.get('service_type', 'general')} disruption requiring {disruption.get('urgency', 'medium')} priority",
                "confidence": 0.5,
                "error": str(e)
            }
        
        state["conversation_history"].append({
            "step": "disruption_analysis",
            "input": disruption,
            "output": analysis,
            "timestamp": datetime.now().isoformat()  # Serializable timestamp
        })
        
        state["disruption"]["analysis"] = analysis
        return state
    
    async def route_to_specialist(self, state: LogisticsState) -> LogisticsState:
        """Route to appropriate specialist agent based on analysis"""
        analysis = state["disruption"]["analysis"]["content"]
        service_type = state["disruption"].get("service_type", "")
        
        # Fixed agent mapping to match actual agent keys
        if "food" in analysis.lower() or "restaurant" in analysis.lower() or service_type == "grabfood":
            specialist = "grabfood"
        elif "package" in analysis.lower() or "express" in analysis.lower() or service_type == "grabexpress":
            specialist = "grabexpress"
        else:
            specialist = "customer_service"  # Default fallback
        
        state["current_agent"] = specialist
        
        routing_prompt = f"""
        Based on disruption analysis: {analysis}
        
        Routing to {specialist} agent.
        Generate specific task briefing for the specialist including:
        1. Key problem parameters
        2. Success criteria
        3. Constraints and limitations
        4. Expected deliverables
        """
        
        try:
            briefing = await self.llm_manager.generate_response(
                routing_prompt, ModelCapability.REASONING
            )
        except Exception as e:
            briefing = {
                "content": f"Standard briefing for {specialist} agent",
                "confidence": 0.5,
                "error": str(e)
            }
        
        state["disruption"]["specialist_briefing"] = briefing
        return state
    
    async def execute_specialist_task(self, state: LogisticsState) -> LogisticsState:
        """Execute task using selected specialist agent"""
        current_agent = state["current_agent"]
        agent = self.agents[current_agent]
        
        task = {
            "task_id": f"task_{int(datetime.now().timestamp())}",
            "disruption": state["disruption"]["description"],
            "service_type": state["disruption"]["service_type"],
            "briefing": state["disruption"].get("specialist_briefing", {}),
            **state["disruption"]  # Include all disruption data
        }
        
        try:
            response = await agent.process_task(task)
            
            # Convert AgentMessage to dict manually
            response_dict = {
                "agent_id": response.agent_id,
                "message_type": response.message_type,
                "content": response.content,
                "timestamp": response.timestamp.isoformat(),
                "confidence": response.confidence
            }
        except Exception as e:
            # Fallback response if agent fails
            response_dict = {
                "agent_id": current_agent,
                "message_type": "error",
                "content": {"solution": f"Agent {current_agent} encountered an error: {str(e)}", "confidence": 0.3},
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.3
            }
        
        state["agent_responses"].append({
            "agent": current_agent,
            "response": response_dict,
            "timestamp": datetime.now().isoformat()
        })
        
        state["confidence_score"] = response_dict.get("confidence", 0.5)
        return state
    
    async def validate_solution(self, state: LogisticsState) -> LogisticsState:
        """Validate the proposed solution"""
        if not state["agent_responses"]:
            # No responses to validate
            state["final_solution"] = {
                "solution": "No solution generated",
                "validation": {"content": "No validation possible", "confidence": 0.1},
                "confidence": 0.1
            }
            return state
        
        latest_response = state["agent_responses"][-1]
        
        # Extract solution with robust fallback handling
        response_content = latest_response["response"]["content"]
        if isinstance(response_content, dict) and "solution" in response_content:
            solution = response_content["solution"]
        elif isinstance(response_content, dict):
            solution = str(response_content)
        elif isinstance(response_content, str):
            solution = response_content
        else:
            solution = "Unable to extract solution"
        
        validation_prompt = f"""
        Validate this logistics solution:
        Original Problem: {state['disruption']['description']}
        Proposed Solution: {solution}
        Agent Confidence: {latest_response['response'].get('confidence', 0.5)}
        
        Evaluate:
        1. Solution completeness
        2. Feasibility  
        3. Cost effectiveness
        4. Customer impact
        5. Implementation complexity
        
        Provide validation score (0-1) and recommendations.
        """
        
        try:
            validation = await self.llm_manager.generate_response(
                validation_prompt, ModelCapability.REASONING
            )
        except Exception as e:
            validation = {
                "content": f"Validation unavailable: {str(e)}",
                "confidence": 0.5
            }
        
        state["final_solution"] = {
            "solution": solution,
            "validation": validation,
            "confidence": latest_response["response"].get("confidence", 0.5)
        }
        
        return state
    
    async def handle_customer_communication(self, state: LogisticsState) -> LogisticsState:
        """Generate customer communication"""
        customer_agent = self.agents["customer_service"]
        
        communication_task = {
            "customer_issue": state["disruption"]["description"],
            "solution": state["final_solution"]["solution"],
            "service_type": state["disruption"]["service_type"],
            "sentiment": state["disruption"].get("customer_sentiment", "neutral")
        }
        
        try:
            communication = await customer_agent.process_task(communication_task)
            
            # Convert to dict manually
            communication_dict = {
                "agent_id": communication.agent_id,
                "message_type": communication.message_type,
                "content": communication.content,
                "timestamp": communication.timestamp.isoformat(),
                "confidence": communication.confidence
            }
        except Exception as e:
            communication_dict = {
                "agent_id": "customer_service",
                "message_type": "error",
                "content": {"customer_message": f"Communication error: {str(e)}"},
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.3
            }
        
        state["final_solution"]["customer_communication"] = communication_dict
        return state
    
    async def escalate_to_human(self, state: LogisticsState) -> LogisticsState:
        """Escalate to human operator with full context"""
        escalation_context = {
            "disruption": state["disruption"],
            "attempted_solutions": state["agent_responses"],
            "confidence_scores": [resp["response"].get("confidence", 0) for resp in state["agent_responses"]],
            "escalation_reason": "Low confidence score or complex scenario",
            "recommended_actions": state.get("final_solution", {}).get("solution", "None generated")
        }
        
        state["escalation_needed"] = True
        state["final_solution"]["escalation_context"] = escalation_context
        
        print(f"🚨 HUMAN ESCALATION REQUIRED")
        print(f"Escalation Context: {escalation_context}")
        
        return state
    
    async def finalize_solution(self, state: LogisticsState) -> LogisticsState:
        """Finalize and log the complete solution"""
        final_solution = state["final_solution"]
        
        # Log solution for learning
        solution_log = {
            "disruption_id": state["disruption"].get("id"),
            "disruption_type": state["disruption"].get("service_type"),
            "solution": final_solution.get("solution", "No solution"),
            "confidence": final_solution.get("confidence", 0),
            "agents_involved": [resp["agent"] for resp in state["agent_responses"]],
            "resolution_time": "calculated_time",
            "customer_satisfaction": "pending"
        }
        
        # Store in memory/database for future learning
        await self._store_solution_for_learning(solution_log)
        
        print(f"✅ SOLUTION FINALIZED")
        print(f"Solution: {final_solution.get('solution', 'No solution available')}")
        
        return state
    
    def _should_escalate(self, state: LogisticsState) -> str:
        """Decision logic for routing after solution validation"""
        confidence = state["confidence_score"]
        
        if confidence < getattr(self.config, 'HUMAN_ESCALATION_THRESHOLD', 0.6):
            return "escalate"
        elif confidence < getattr(self.config, 'CONFIDENCE_THRESHOLD', 0.8):
            return "retry"
        else:
            return "communicate"
    
    async def _store_solution_for_learning(self, solution_log: Dict[str, Any]):
        """Store solution in memory for future learning"""
        print(f"📚 Storing solution for learning: {solution_log.get('disruption_id', 'unknown')}")
    
    async def process_disruption(self, disruption: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for processing disruptions"""
        initial_state = LogisticsState(
            disruption=disruption,
            current_agent="",
            agent_responses=[],
            final_solution={},
            escalation_needed=False,
            confidence_score=0.0,
            conversation_history=[]
        )
        
        try:
            # Process through the workflow
            final_state = await self.graph.ainvoke(initial_state, {"recursion_limit": 50})
            return final_state
        except Exception as e:
            print(f"❌ Orchestrator error: {str(e)}")
            # Return error state
            return {
                "disruption": disruption,
                "final_solution": {"solution": f"System error: {str(e)}", "confidence": 0.1},
                "escalation_needed": True,
                "confidence_score": 0.1,
                "error": str(e)
            }
