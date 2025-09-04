from typing import Dict
from core.llm_manager import LMStudioManager
from .service_agents import GrabFoodAgent, GrabExpressAgent, CustomerServiceAgent
from typing import Dict, Any, List

class AgentFactory:
    @staticmethod
    def create_agents(llm_manager: LMStudioManager) -> Dict[str, Any]:
        agents = {
            "food": GrabFoodAgent(llm_manager),
            "express": GrabExpressAgent(llm_manager),
            "customer_service": CustomerServiceAgent(llm_manager)
        }
        
        # Initialize agent states
        for agent in agents.values():
            agent.state.context = {}
        
        return agents