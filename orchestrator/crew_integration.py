# orchestrator/crew_integration.py - LM Studio Only Version
import os
from typing import Dict, Any

class CrewAIIntegration:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        # Use your LM Studio manager instead of OpenAI
        self.local_llm = llm_manager
        
    async def execute_crew_task(self, crew_type: str, disruption_data: Dict[str, Any]):
        """Execute crew task using LM Studio instead of OpenAI"""
        
        crew_prompts = {
            "traffic_crisis": f"""
            Traffic Crisis Management Team Response:
            Situation: {disruption_data.get('description')}
            Location: {disruption_data.get('location', 'Unknown')}
            
            Coordinate immediate response for traffic-related logistics disruption.
            Provide multi-step action plan including route alternatives, 
            driver coordination, and customer communication strategy.
            """,
            
            "merchant_coordination": f"""
            Merchant Coordination Team Response:
            Situation: {disruption_data.get('description')}
            Merchant: {disruption_data.get('location', 'Unknown')}
            
            Coordinate with merchant partners to resolve operational disruptions.
            Focus on maintaining service quality and customer satisfaction.
            """,
            
            "customer_retention": f"""
            Customer Retention Team Response:
            Situation: {disruption_data.get('description')}
            Affected Customers: {disruption_data.get('affected_orders', 1)}
            
            Develop comprehensive customer retention strategy addressing
            immediate concerns, compensation, and long-term relationship preservation.
            """
        }
        
        prompt = crew_prompts.get(crew_type, f"Handle disruption: {disruption_data.get('description')}")
        
        # Use LM Studio for crew analysis
        response = await self.local_llm.generate_response_for_agent(
            f"crew_{crew_type}",
            prompt,
            disruption_data.get('urgency', 'medium')
        )
        
        return {
            "crew_type": crew_type,
            "analysis": response.get("content", ""),
            "confidence": response.get("confidence", 0.8),
            "provider": "lm_studio_local"
        }
