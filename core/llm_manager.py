# core/llm_manager.py - Enhanced with LogisticsModelManager
import openai
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from .model_capability import ModelCapability, LogisticsModelManager

class LMStudioManager:
    def __init__(self, config):
        self.config = config
        self.base_url = "http://localhost:1234/v1"
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key="lm-studio"
        )
        
        # Initialize model manager
        self.model_manager = LogisticsModelManager()
        
        # Enhanced model routing using LogisticsModelManager
        self.model_routing = {
            ModelCapability.REASONING: self.model_manager.get_model_by_urgency("complex"),
            ModelCapability.EMPATHY: self.model_manager.get_model_by_urgency("customer"),
            ModelCapability.SPATIAL: self.model_manager.get_model_by_urgency("spatial"),
            ModelCapability.GENERAL: "qwen/qwen3-4b",
            ModelCapability.URGENT: self.model_manager.get_model_by_urgency("urgent"),
            ModelCapability.COORDINATION: self.model_manager.get_model_for_agent("orchestrator", "coordination")
        }
        
        # Currently active model in LM Studio (only one can run at a time)
        self.current_active_model = "qwen/qwen3-4b"  # Default
        
    def get_optimal_model_for_agent(self, agent_type: str, urgency: str = "medium") -> str:
        """Get the optimal model for a specific agent and urgency level"""
        if urgency == "urgent":
            return self.model_manager.get_model_by_urgency("urgent")
        elif urgency == "complex":
            return self.model_manager.get_model_by_urgency("complex")
        else:
            return self.model_manager.get_model_for_agent(agent_type, "primary")
    
    async def generate_response_for_agent(
        self, 
        agent_type: str,
        prompt: str, 
        urgency: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response optimized for specific agent type"""
        
        optimal_model = self.get_optimal_model_for_agent(agent_type, urgency)
        
        # Use specialized system prompt for agent type
        system_prompt = self._get_agent_system_prompt(agent_type, urgency)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            if context:
                messages.insert(1, {"role": "system", "content": f"Context: {context}"})
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.current_active_model,  # Use currently loaded model
                messages=messages,
                temperature=self._get_temperature_for_agent(agent_type),
                max_tokens=self._get_max_tokens_for_agent(agent_type),
                stream=False
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "provider": "lm_studio",
                "active_model": self.current_active_model,
                "optimal_model": optimal_model,
                "agent_type": agent_type,
                "urgency": urgency,
                "confidence": self._calculate_confidence(content, agent_type)
            }
            
        except Exception as e:
            return await self._fallback_response(prompt, agent_type, str(e))
    
    def _get_agent_system_prompt(self, agent_type: str, urgency: str) -> str:
        """Get specialized system prompts for each agent type"""
        
        base_prompts = {
            "grabfood": """You are a GrabFood delivery specialist with expertise in food delivery logistics.
            Focus on food safety, temperature control, restaurant coordination, and customer satisfaction.
            Consider delivery time windows, traffic conditions, and food quality preservation.""",
            
            "grabexpress": """You are a GrabExpress package delivery expert specializing in urgent deliveries.
            Focus on package security, efficient routing, time-critical handling, and customer communication.
            Consider package value, fragility, delivery addresses, and time constraints.""",
            
            "customer_service": """You are a customer service specialist trained in empathetic communication.
            Focus on understanding customer concerns, providing clear explanations, and offering practical solutions.
            Use warm, professional language that builds trust and resolves issues effectively.""",
            
            "orchestrator": """You are a logistics operations coordinator managing multiple delivery agents.
            Focus on resource allocation, task prioritization, and coordinating between different service types.
            Ensure efficient communication and optimal decision-making across all operations."""
        }
        
        urgency_modifiers = {
            "urgent": " URGENT SITUATION: Prioritize immediate action and quick resolution.",
            "medium": " STANDARD OPERATION: Provide thorough analysis and solutions.",
            "complex": " COMPLEX SCENARIO: Use detailed reasoning and consider multiple factors."
        }
        
        base = base_prompts.get(agent_type, "You are a helpful logistics assistant.")
        modifier = urgency_modifiers.get(urgency, "")
        
        return base + modifier
    
    def _get_temperature_for_agent(self, agent_type: str) -> float:
        """Optimize creativity based on agent type"""
        temperatures = {
            "grabfood": 0.4,          # Focused but flexible for food logistics
            "grabexpress": 0.3,       # More focused for package handling
            "customer_service": 0.7,  # More creative for empathetic responses
            "orchestrator": 0.5       # Balanced for coordination
        }
        return temperatures.get(agent_type, 0.5)
    
    def _get_max_tokens_for_agent(self, agent_type: str) -> int:
        """Optimize response length based on agent type"""
        max_tokens = {
            "grabfood": 600,          # Detailed food logistics analysis
            "grabexpress": 500,       # Concise package delivery instructions
            "customer_service": 800,  # Detailed customer communication
            "orchestrator": 400       # Concise coordination instructions
        }
        return max_tokens.get(agent_type, 600)
    
    def _calculate_confidence(self, content: str, agent_type: str) -> float:
        """Calculate confidence based on response quality and agent type"""
        base_confidence = 0.8
        
        # Length checks
        if len(content) > 100:
            base_confidence += 0.05
        elif len(content) < 50:
            base_confidence -= 0.1
        
        # Agent-specific quality indicators
        quality_indicators = {
            "grabfood": ['restaurant', 'delivery', 'food', 'temperature', 'quality'],
            "grabexpress": ['package', 'urgent', 'secure', 'delivery', 'address'],
            "customer_service": ['understand', 'sorry', 'help', 'solution', 'resolve'],
            "orchestrator": ['coordinate', 'assign', 'prioritize', 'allocate', 'manage']
        }
        
        indicators = quality_indicators.get(agent_type, [])
        if any(word in content.lower() for word in indicators):
            base_confidence += 0.1
        
        # Uncertainty indicators
        uncertainty_words = ['uncertain', 'maybe', 'possibly', 'might', 'unclear']
        if any(word in content.lower() for word in uncertainty_words):
            base_confidence -= 0.15
        
        return max(0.1, min(0.95, base_confidence))
    
    async def _fallback_response(self, prompt: str, agent_type: str, error: str):
        """Agent-specific fallback responses"""
        fallback_responses = {
            "grabfood": "Food delivery analysis temporarily unavailable. Escalating to human food delivery coordinator.",
            "grabexpress": "Express delivery system offline. Switching to standard delivery protocols.",
            "customer_service": "We're experiencing technical difficulties but are working to resolve your issue promptly.",
            "orchestrator": "Coordination system temporarily offline. Switching to manual oversight mode."
        }
        
        return {
            "content": fallback_responses.get(agent_type, "System temporarily unavailable."),
            "provider": "lm_studio_fallback",
            "active_model": "fallback",
            "agent_type": agent_type,
            "confidence": 0.2,
            "error": error
        }
    
    # Legacy method for backward compatibility
    async def generate_response(self, prompt: str, capability: ModelCapability, context: Optional[Dict[str, Any]] = None):
        """Legacy method - converts capability to agent type"""
        agent_type_map = {
            ModelCapability.REASONING: "orchestrator",
            ModelCapability.EMPATHY: "customer_service", 
            ModelCapability.SPATIAL: "grabexpress",
            ModelCapability.GENERAL: "orchestrator",
            ModelCapability.URGENT: "grabexpress",
            ModelCapability.COORDINATION: "orchestrator"
        }
        
        agent_type = agent_type_map.get(capability, "orchestrator")
        urgency = "urgent" if capability == ModelCapability.URGENT else "medium"
        
        return await self.generate_response_for_agent(agent_type, prompt, urgency, context)
