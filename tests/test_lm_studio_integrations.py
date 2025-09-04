# test_lm_studio_integration.py
import asyncio
from core.llm_manager import LMStudioManager, ModelCapability
from config.settings import Config

async def test_lm_studio_models():
    """Test your downloaded LM Studio models"""
    config = Config()
    lm_manager = LMStudioManager(config)
    
    # Test scenarios
    test_cases = [
        {
            "prompt": "A traffic jam is blocking food deliveries on MG Road. 15 orders affected. What should we do?",
            "capability": ModelCapability.REASONING,
            "expected_model": "qwen3-4b-thinking-2507"
        },
        {
            "prompt": "Write a message to customers about their delayed food delivery due to traffic.",
            "capability": ModelCapability.EMPATHY,
            "expected_model": "phi-4-mini-reasoning"
        },
        {
            "prompt": "URGENT: Driver needs immediate route alternative for express delivery.",
            "capability": ModelCapability.URGENT,
            "expected_model": "qwen3-1.7b"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['capability']}")
        print(f"Expected Model: {test['expected_model']}")
        
        response = await lm_manager.generate_response(
            test["prompt"], 
            test["capability"]
        )
        
        print(f"✅ Model Used: {response['model']}")
        print(f"📊 Confidence: {response['confidence']}")
        print(f"💬 Response: {response['content'][:150]}...")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_lm_studio_models())
