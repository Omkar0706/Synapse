# test_model_manager.py
import asyncio
from core.llm_manager import LMStudioManager
from core.model_capability import LogisticsModelManager
from config.settings import Config

async def test_model_manager():
    """Test the LogisticsModelManager integration"""
    config = Config()
    lm_manager = LMStudioManager(config)
    
    print("🧪 Testing LogisticsModelManager Integration")
    print("=" * 50)
    
    # Test different agent types
    test_scenarios = [
        {
            "agent": "grabfood",
            "prompt": "Traffic jam affecting food deliveries. 5 orders getting cold.",
            "urgency": "urgent"
        },
        {
            "agent": "grabexpress", 
            "prompt": "Package delivery to wrong address. Customer complaints.",
            "urgency": "medium"
        },
        {
            "agent": "customer_service",
            "prompt": "Angry customer about delayed delivery. Need empathetic response.",
            "urgency": "medium"
        },
        {
            "agent": "orchestrator",
            "prompt": "Multiple disruptions across city. Need coordination strategy.",
            "urgency": "complex"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing {scenario['agent']} agent ({scenario['urgency']})")
        
        response = await lm_manager.generate_response_for_agent(
            scenario["agent"],
            scenario["prompt"],
            scenario["urgency"]
        )
        
        print(f"✅ Active Model: {response['active_model']}")
        print(f"🎯 Optimal Model: {response['optimal_model']}")
        print(f"📊 Confidence: {response['confidence']:.2f}")
        print(f"💬 Response: {response['content'][:150]}...")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_model_manager())
