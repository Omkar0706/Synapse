from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentMessage(BaseModel):
    agent_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    confidence: float
    metadata: Optional[Dict[str, Any]] = None