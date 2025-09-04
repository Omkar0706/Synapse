# core/model_capability.py - True Multi-Model Implementation
from enum import Enum
from typing import Dict, Any, List

class ModelCapability(str, Enum):
    REASONING = "reasoning"
    EMPATHY = "empathy" 
    SPATIAL = "spatial"
    GENERAL = "general"
    URGENT = "urgent"
    COORDINATION = "coordination"

class TaskType(str, Enum):
    ROUTE_OPTIMIZATION = "route_optimization"
    CUSTOMER_COMMUNICATION = "customer_communication"
    STRATEGIC_PLANNING = "strategic_planning"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    EMERGENCY_RESPONSE = "emergency_response"

class LogisticsModelManager:
    def __init__(self):
        # ✅ SPECIALIZED MODELS FOR SPECIFIC TASKS
        self.task_model_mapping = {
            # Route & Spatial Intelligence
            TaskType.ROUTE_OPTIMIZATION: "qwen/qwen3-4b-thinking-2507",
            
            # Customer Communication & Empathy
            TaskType.CUSTOMER_COMMUNICATION: "microsoft/phi-4-mini-reasoning",
            
            # Complex Strategic Reasoning
            TaskType.STRATEGIC_PLANNING: "deepseek/deepseek-r1-0528-qwen3-8b",
            
            # Emotion & Sentiment Understanding
            TaskType.SENTIMENT_ANALYSIS: "google/gemma-3-4b",
            
            # Speed-Optimized Emergency Response
            TaskType.EMERGENCY_RESPONSE: "qwen/qwen3-1.7b"
        }
        
        # Agent-Task Mapping
        self.agent_task_mapping = {
            "grabfood": {
                "primary": TaskType.ROUTE_OPTIMIZATION,
                "customer_comm": TaskType.CUSTOMER_COMMUNICATION,
                "fallback": TaskType.EMERGENCY_RESPONSE
            },
            "grabexpress": {
                "primary": TaskType.STRATEGIC_PLANNING,
                "spatial": TaskType.ROUTE_OPTIMIZATION,
                "fallback": TaskType.EMERGENCY_RESPONSE
            },
            "customer_service": {
                "primary": TaskType.CUSTOMER_COMMUNICATION,
                "sentiment": TaskType.SENTIMENT_ANALYSIS,
                "fallback": TaskType.EMERGENCY_RESPONSE
            },
            "orchestrator": {
                "primary": TaskType.STRATEGIC_PLANNING,
                "coordination": TaskType.ROUTE_OPTIMIZATION
            }
        }
        
        # Urgency-based model selection
        self.urgency_model_map = {
            "urgent": "qwen/qwen3-1.7b",                    # Fastest
            "medium": "microsoft/phi-4-mini-reasoning",     # Balanced
            "complex": "deepseek/deepseek-r1-0528-qwen3-8b", # Most capable
            "customer": "microsoft/phi-4-mini-reasoning",   # Customer-focused
            "spatial": "qwen/qwen3-4b-thinking-2507"        # Spatial reasoning
        }

    def get_model_by_urgency(self, urgency_level: str) -> str:
        """Get model optimized for urgency level"""
        return self.urgency_model_map.get(urgency_level, "qwen/qwen3-4b")
    
    def get_model_for_agent(self, agent_type: str, task_type: str = "primary") -> str:
        """Get specialized model for agent task"""
        if agent_type in self.agent_task_mapping:
            task = self.agent_task_mapping[agent_type].get(task_type)
            if task and task in self.task_model_mapping:
                return self.task_model_mapping[task]
        return "qwen/qwen3-4b"
    
    def get_model_for_task(self, task: TaskType) -> str:
        """Get optimal model for specific task"""
        return self.task_model_mapping.get(task, "qwen/qwen3-4b")
    
    def get_all_models(self) -> set:
        """Get all unique models used"""
        all_models = set()
        all_models.update(self.task_model_mapping.values())
        all_models.update(self.urgency_model_map.values())
        return all_models
    
    def analyze_problem_requirements(self, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problem and recommend task-model pairs"""
        description = problem_context.get('description', '').lower()
        urgency = problem_context.get('urgency', 'medium')
        
        recommended_tasks = []
        
        # Route optimization needed?
        if any(word in description for word in ['traffic', 'route', 'location', 'delivery']):
            recommended_tasks.append({
                "task": TaskType.ROUTE_OPTIMIZATION,
                "model": self.get_model_for_task(TaskType.ROUTE_OPTIMIZATION),
                "priority": "high"
            })
        
        # Customer communication needed?
        if any(word in description for word in ['customer', 'notification', 'communication']):
            recommended_tasks.append({
                "task": TaskType.CUSTOMER_COMMUNICATION,
                "model": self.get_model_for_task(TaskType.CUSTOMER_COMMUNICATION),
                "priority": "high"
            })
        
        # Sentiment analysis needed?
        if any(word in description for word in ['angry', 'frustrated', 'complaint']):
            recommended_tasks.append({
                "task": TaskType.SENTIMENT_ANALYSIS,
                "model": self.get_model_for_task(TaskType.SENTIMENT_ANALYSIS),
                "priority": "medium"
            })
        
        # Strategic planning always needed for complex issues
        if len(recommended_tasks) > 1 or urgency in ['high', 'complex']:
            recommended_tasks.append({
                "task": TaskType.STRATEGIC_PLANNING,
                "model": self.get_model_for_task(TaskType.STRATEGIC_PLANNING),
                "priority": "high"
            })
        
        # Emergency response for urgent issues
        if urgency == 'high' or 'emergency' in description:
            recommended_tasks.append({
                "task": TaskType.EMERGENCY_RESPONSE,
                "model": self.get_model_for_task(TaskType.EMERGENCY_RESPONSE),
                "priority": "critical"
            })
        
        return {
            "recommended_tasks": recommended_tasks,
            "total_tasks": len(recommended_tasks),
            "models_needed": list(set(task["model"] for task in recommended_tasks))
        }
