# agents/service_agents.py - Updated for LogisticsModelManager
from agents.base_agent import BaseAgent, AgentMessage
from datetime import datetime
from typing import Dict, Any

class GrabFoodAgent(BaseAgent):
    def __init__(self, llm_manager):
        super().__init__(
            agent_id="grabfood_specialist",
            llm_manager=llm_manager,
            capabilities=["food_delivery", "restaurant_coordination", "temperature_management"]
        )
    
    async def process_task(self, task: Dict[str, Any]) -> AgentMessage:
        self.state.status = "working"
        self.state.current_task = task.get("task_id")
        
        # Determine urgency level
        urgency = self._determine_urgency(task)
        
        # Use agent-specific LM Studio method
        prompt = f"""
        FOOD DELIVERY DISRUPTION ANALYSIS:
        
        Disruption: {task.get('disruption')}
        Restaurant: {task.get('restaurant', 'Unknown')}
        Food Type: {task.get('food_type', 'Mixed')}
        Affected Orders: {task.get('affected_orders', 1)}
        Urgency Level: {urgency}
        Current Time: {datetime.now().strftime('%H:%M')}
        Location: {task.get('location', 'Unknown')}
        
        Provide comprehensive food delivery solution including:
        1. Food safety and quality assessment
        2. Restaurant coordination strategy  
        3. Delivery time optimization
        4. Customer communication plan
        5. Alternative solutions if needed
        
        Consider food temperature, delivery windows, and customer satisfaction.
        """
        
        response = await self.llm_manager.generate_response_for_agent(
            "grabfood", prompt, urgency, self.state.context
        )
        
        self.state.confidence = response["confidence"]
        self.state.status = "completed" if response["confidence"] > 0.7 else "escalating"
        
        return AgentMessage(
            agent_id=self.agent_id,
            message_type="task_completion",
            content={
                "solution": response["content"],
                "confidence": response["confidence"],
                "model_used": response.get("active_model", "unknown"),
                "optimal_model": response.get("optimal_model", "unknown"),
                "urgency": urgency,
                "requires_escalation": self.should_escalate(),
                "next_actions": self._extract_action_items(response["content"])
            },
            timestamp=datetime.now(),
            confidence=response["confidence"]
        )
    
    def _determine_urgency(self, task: Dict[str, Any]) -> str:
        """Determine urgency level for food delivery tasks"""
        factors = {
            "urgent": [
                task.get('urgency') == 'high',
                task.get('affected_orders', 0) > 10,
                'food poisoning' in task.get('disruption', '').lower(),
                'temperature' in task.get('disruption', '').lower(),
                'contamination' in task.get('disruption', '').lower(),
                'expired' in task.get('disruption', '').lower()
            ],
            "complex": [
                task.get('affected_orders', 0) > 5,
                'multiple' in task.get('disruption', '').lower(),
                task.get('severity') == 'high',
                'restaurant' in task.get('disruption', '').lower() and 'closed' in task.get('disruption', '').lower()
            ]
        }
        
        if sum(factors["urgent"]) >= 2:
            return "urgent"
        elif sum(factors["complex"]) >= 2:
            return "complex"
        else:
            return "medium"
    
    def _extract_action_items(self, content: str) -> list:
        """Extract actionable items from response"""
        actions = []
        if "contact restaurant" in content.lower():
            actions.append("restaurant_contact")
        if "alternative route" in content.lower():
            actions.append("route_optimization")
        if "customer notification" in content.lower():
            actions.append("customer_communication")
        if "refund" in content.lower() or "compensation" in content.lower():
            actions.append("customer_compensation")
        return actions

class GrabExpressAgent(BaseAgent):
    def __init__(self, llm_manager):
        super().__init__(
            agent_id="grabexpress_specialist",
            llm_manager=llm_manager,
            capabilities=["package_delivery", "route_optimization", "time_critical_handling"]
        )
    
    async def process_task(self, task: Dict[str, Any]) -> AgentMessage:
        self.state.status = "working"
        self.state.current_task = task.get("task_id")
        
        # Determine urgency level
        urgency = self._determine_urgency(task)
        
        prompt = f"""
        PACKAGE DELIVERY DISRUPTION ANALYSIS:
        
        Disruption: {task.get('disruption')}
        Package Type: {task.get('package_type', 'General')}
        Package Value: {task.get('package_value', 'Unknown')}
        Urgency: {task.get('urgency', 'normal')}
        Pickup Location: {task.get('pickup_location', 'Unknown')}
        Delivery Location: {task.get('delivery_location', 'Unknown')}
        Fragile: {task.get('fragile', False)}
        Current Location: {task.get('location', 'Unknown')}
        
        Provide express delivery solution focusing on:
        1. Time optimization and route planning
        2. Package security and handling
        3. Alternative delivery options
        4. Customer communication strategy
        5. Cost efficiency considerations
        
        Account for package value, fragility, and delivery constraints.
        """
        
        response = await self.llm_manager.generate_response_for_agent(
            "grabexpress", prompt, urgency, self.state.context
        )
        
        self.state.confidence = response["confidence"]
        self.state.status = "completed" if response["confidence"] > 0.7 else "escalating"
        
        return AgentMessage(
            agent_id=self.agent_id,
            message_type="task_completion",
            content={
                "solution": response["content"],
                "confidence": response["confidence"],
                "model_used": response.get("active_model", "unknown"),
                "optimal_model": response.get("optimal_model", "unknown"),
                "urgency": urgency,
                "requires_escalation": self.should_escalate(),
                "route_optimization": await self._optimize_route(task),
                "security_measures": self._assess_security_needs(task)
            },
            timestamp=datetime.now(),
            confidence=response["confidence"]
        )
    
    def _determine_urgency(self, task: Dict[str, Any]) -> str:
        """Determine urgency level for express delivery tasks"""
        factors = {
            "urgent": [
                task.get('urgency') == 'high',
                task.get('package_value', 0) > 50000,
                'medical' in task.get('package_type', '').lower(),
                'emergency' in task.get('disruption', '').lower(),
                'time-sensitive' in task.get('disruption', '').lower()
            ],
            "complex": [
                task.get('fragile', False),
                'multiple' in task.get('disruption', '').lower(),
                task.get('package_value', 0) > 10000,
                'wrong address' in task.get('disruption', '').lower()
            ]
        }
        
        if sum(factors["urgent"]) >= 2:
            return "urgent"
        elif sum(factors["complex"]) >= 2:
            return "complex"
        else:
            return "medium"
    
    async def _optimize_route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route optimization specific to express delivery"""
        # Simulate route optimization logic
        return {
            "optimal_route": f"Optimized route from {task.get('pickup_location')} to {task.get('delivery_location')}",
            "estimated_time": "25 minutes",
            "alternative_routes": 2,
            "traffic_conditions": "Moderate"
        }
    
    def _assess_security_needs(self, task: Dict[str, Any]) -> list:
        """Assess security measures needed for package"""
        security_measures = []
        package_value = task.get('package_value', 0)
        
        if package_value > 10000:
            security_measures.append("signature_required")
        if task.get('package_type') == 'documents':
            security_measures.append("document_verification")
        if task.get('fragile', False):
            security_measures.append("fragile_handling")
        if package_value > 50000:
            security_measures.append("insurance_verification")
            
        return security_measures

class CustomerServiceAgent(BaseAgent):
    def __init__(self, llm_manager):
        super().__init__(
            agent_id="customer_service_specialist",
            llm_manager=llm_manager,
            capabilities=["customer_communication", "conflict_resolution", "empathy"]
        )
    
    async def process_task(self, task: Dict[str, Any]) -> AgentMessage:
        self.state.status = "working"
        self.state.current_task = task.get("task_id")
        
        # Determine sentiment and urgency
        sentiment = self._analyze_sentiment(task)
        urgency = "urgent" if sentiment in ["angry", "frustrated"] else "medium"
        
        prompt = f"""
        CUSTOMER SERVICE SITUATION:
        
        Customer Issue: {task.get('customer_issue', task.get('disruption', 'General inquiry'))}
        Customer Sentiment: {sentiment}
        Service Type: {task.get('service_type', 'general')}
        Previous Interactions: {task.get('history', 'None')}
        Customer Tier: {task.get('customer_tier', 'standard')}
        Issue Complexity: {task.get('issue_complexity', 'medium')}
        
        Generate empathetic and solution-focused customer communication that:
        1. Acknowledges the customer's situation with empathy
        2. Provides clear explanation of what happened
        3. Offers concrete solutions or alternatives
        4. Sets appropriate expectations for resolution
        5. Maintains professional and caring tone
        
        Consider the customer's emotional state and provide appropriate support.
        """
        
        response = await self.llm_manager.generate_response_for_agent(
            "customer_service", prompt, urgency, self.state.context
        )
        
        self.state.confidence = response["confidence"]
        self.state.status = "completed" if response["confidence"] > 0.7 else "escalating"
        
        return AgentMessage(
            agent_id=self.agent_id,
            message_type="customer_communication",
            content={
                "customer_message": response["content"],
                "sentiment_analysis": sentiment,
                "confidence": response["confidence"],
                "model_used": response.get("active_model", "unknown"),
                "optimal_model": response.get("optimal_model", "unknown"),
                "escalation_needed": response["confidence"] < 0.7,
                "follow_up_required": self._needs_follow_up(task),
                "suggested_compensation": self._suggest_compensation(task, sentiment)
            },
            timestamp=datetime.now(),
            confidence=response["confidence"]
        )
    
    def _analyze_sentiment(self, task: Dict[str, Any]) -> str:
        """Analyze customer sentiment from task data"""
        disruption_text = task.get('customer_issue', task.get('disruption', '')).lower()
        
        # Negative sentiment indicators
        if any(word in disruption_text for word in ['angry', 'furious', 'outraged', 'unacceptable']):
            return "angry"
        elif any(word in disruption_text for word in ['frustrated', 'annoyed', 'disappointed', 'upset']):
            return "frustrated"
        elif any(word in disruption_text for word in ['confused', 'unclear', 'don\'t understand']):
            return "confused"
        elif any(word in disruption_text for word in ['happy', 'satisfied', 'good', 'excellent']):
            return "positive"
        else:
            return task.get('sentiment', 'neutral')
    
    def _needs_follow_up(self, task: Dict[str, Any]) -> bool:
        """Determine if follow-up is required"""
        high_value_customer = task.get('customer_tier') == 'premium'
        complex_issue = task.get('issue_complexity', 'low') == 'high'
        negative_sentiment = self._analyze_sentiment(task) in ['angry', 'frustrated']
        repeated_issue = 'history' in task and len(str(task['history'])) > 10
        
        return high_value_customer or complex_issue or negative_sentiment or repeated_issue
    
    def _suggest_compensation(self, task: Dict[str, Any], sentiment: str) -> Dict[str, Any]:
        """Suggest appropriate compensation based on situation"""
        compensation = {"type": None, "amount": 0, "reason": None}
        
        service_type = task.get('service_type', 'general')
        
        if sentiment in ['angry', 'frustrated']:
            if service_type == 'grabfood':
                compensation = {
                    "type": "credit",
                    "amount": 100,  # INR
                    "reason": "Food delivery disruption compensation"
                }
            elif service_type == 'grabexpress':
                compensation = {
                    "type": "discount",
                    "amount": 50,  # Percentage
                    "reason": "Express delivery delay compensation"
                }
        
        return compensation

# Helper function for agent initialization
def initialize_all_agents(llm_manager):
    """Initialize all service agents with the LLM manager"""
    return {
        "grabfood": GrabFoodAgent(llm_manager),
        "grabexpress": GrabExpressAgent(llm_manager),
        "customer_service": CustomerServiceAgent(llm_manager)
    }
