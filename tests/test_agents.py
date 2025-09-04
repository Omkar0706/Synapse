import pytest
import asyncio
from core.llm_manager import MultiLLMManager
from agents.service_agents import GrabFoodAgent, GrabExpressAgent, CustomerServiceAgent
from config.settings import Config
from models.agent_message import AgentMessage

@pytest.fixture
async def llm_manager():
    config = Config()
    manager = MultiLLMManager(config)
    return manager

@pytest.mark.asyncio
async def test_grab_food_agent(llm_manager):
    agent = GrabFoodAgent(llm_manager)
    assert agent.service_type == "food_delivery"
    assert "food_delivery_optimization" in agent.capabilities
    
    # Test task processing
    test_task = {
        "task_id": "test-123",
        "disruption": "Restaurant delay",
        "restaurant": "Test Restaurant",
        "estimated_time": "30 mins",
        "food_type": "Hot food"
    }
    
    response = await agent.process_task(test_task)
    assert isinstance(response, AgentMessage)
    assert response.agent_id == agent.__class__.__name__

@pytest.mark.asyncio
async def test_grab_express_agent(llm_manager):
    agent = GrabExpressAgent(llm_manager)
    assert agent.service_type == "express_delivery"
    assert "package_delivery_optimization" in agent.capabilities

@pytest.mark.asyncio
async def test_customer_service_agent(llm_manager):
    agent = CustomerServiceAgent(llm_manager)
    assert agent.service_type == "customer_service"
    assert "customer_communication" in agent.capabilities