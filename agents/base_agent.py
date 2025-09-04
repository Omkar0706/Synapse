# agents/base_agent.py - Updated for compatibility
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio

class AgentMessage(BaseModel):
    agent_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    confidence: float

class AgentState(BaseModel):
    agent_id: str
    current_task: Optional[str] = None
    context: Dict[str, Any] = {}
    memory: List[Dict[str, Any]] = []
    confidence: float = 0.0
    status: str = "idle"  # idle, working, escalating, completed

class BaseAgent(ABC):
    def __init__(self, agent_id: str, llm_manager, capabilities: List[str]):
        self.agent_id = agent_id
        self.llm_manager = llm_manager
        self.capabilities = capabilities
        self.state = AgentState(agent_id=agent_id)
        self.conversation_history = []
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> AgentMessage:
        pass
    
    async def communicate_with_agent(self, target_agent: str, message: str) -> AgentMessage:
        """Inter-agent communication"""
        return AgentMessage(
            agent_id=self.agent_id,
            message_type="communication",
            content={"target": target_agent, "message": message},
            timestamp=datetime.now(),
            confidence=0.9
        )
    
    def update_context(self, new_context: Dict[str, Any]):
        self.state.context.update(new_context)
        self.state.memory.append({
            "timestamp": datetime.now(),
            "action": "context_update",
            "data": new_context
        })
    
    def should_escalate(self) -> bool:
        return self.state.confidence < 0.6
