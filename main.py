# main.py - Enhanced Multi-Model Integration
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from orchestrator.langgraph_orchestrator import LogisticsOrchestrator
from orchestrator.crew_integration import CrewAIIntegration
from core.llm_manager import LMStudioManager, ModelCapability
from core.model_capability import LogisticsModelManager
from core.multi_model_orchestrator import MultiModelOrchestrator
from config.settings import Config

class LogisticsAI:
    def __init__(self):
        self.config = Config()
        # Initialize LM Studio Manager
        self.llm_manager = LMStudioManager(self.config)
        
        # Initialize multi-model components
        self.model_manager = LogisticsModelManager()
        self.multi_model_orchestrator = MultiModelOrchestrator(self.model_manager, self.llm_manager)
        
        # Existing orchestrators
        self.orchestrator = LogisticsOrchestrator(self.config, self.llm_manager)
        self.crew_integration = CrewAIIntegration(self.llm_manager)
    
    async def handle_disruption(self, disruption_data: Dict[str, Any]):
        """Enhanced multi-model disruption handling"""
        print(f"🚨 NEW DISRUPTION RECEIVED: {disruption_data['description']}")
        print(f"🤖 Multi-Model Analysis Starting...")
        
        # Use multi-model orchestrator for intelligent analysis
        multi_model_result = await self.enhanced_multi_model_processing(disruption_data)
        
        # Integrate with existing workflow if needed
        if self._requires_crew_approach(disruption_data):
            print("🤖 Deploying specialized CrewAI team...")
            crew_type = self._determine_crew_type(disruption_data)
            crew_result = await self.crew_integration.execute_crew_task(crew_type, disruption_data)
            multi_model_result["crew_analysis"] = crew_result
        
        return multi_model_result
    
    async def enhanced_multi_model_processing(self, disruption_data: Dict[str, Any]):
        """Process disruption using true multi-model specialization"""
        
        print(f"🚀 MULTI-MODEL LOGISTICS ANALYSIS STARTING")
        print(f"📋 Problem: {disruption_data.get('description')}")
        
        # Execute multi-model analysis
        result = await self.multi_model_orchestrator.execute_multi_model_analysis(disruption_data)
        
        # Display comprehensive results
        print(f"\n🧠 MULTI-MODEL ANALYSIS COMPLETE")
        print(f"🎯 Models Used: {len(result['models_used'])}")
        print(f"⚡ Model Switches: {result['model_switches']}")
        print(f"📊 Overall Confidence: {result['overall_confidence']:.2f}")
        
        print(f"\n💡 UNIFIED SOLUTION PLAN:")
        print(result['final_solution']['unified_plan'])
        
        return result
    
    def _requires_crew_approach(self, disruption: Dict[str, Any]) -> bool:
        """Determine if situation requires specialized crew approach"""
        complexity_indicators = [
            "multiple" in disruption["description"].lower(),
            "citywide" in disruption["description"].lower(),
            disruption.get("severity") == "high",
            len(disruption.get("affected_areas", [])) > 3
        ]
        return sum(complexity_indicators) >= 2
    
    def _determine_crew_type(self, disruption: Dict[str, Any]) -> str:
        """Determine which type of specialized crew to deploy"""
        if "traffic" in disruption["description"].lower():
            return "traffic_crisis"
        elif "restaurant" in disruption["description"].lower():
            return "merchant_coordination"
        elif "customer" in disruption["description"].lower():
            return "customer_retention"
        else:
            return "traffic_crisis"

async def main():
    """Enhanced demo with multi-model processing"""
    print("🚀 Starting Multi-Agent Logistics System with Multi-Model Intelligence...")
    print("📡 Connecting to LM Studio server at http://localhost:1234")
    
    try:
        logistics_ai = LogisticsAI()
        print("✅ Multi-Model System Initialized!")
        print(f"🧠 Available Models: {len(logistics_ai.model_manager.get_all_models())}")
        
    except Exception as e:
        print(f"❌ Failed to initialize system: {str(e)}")
        print("💡 Make sure LM Studio is running with a model loaded!")
        return
    
    # Enhanced sample disruptions for multi-model testing
    sample_disruptions = [
        {
            "id": "MM_DISR_001",
            "description": "Heavy traffic jam on Highway 101 affecting 25 food deliveries, multiple angry customers calling, restaurant coordination needed urgently",
            "service_type": "grabfood",
            "location": "Highway 101, San Francisco",
            "urgency": "high",
            "affected_orders": 25,
            "severity": "high"
        },
        {
            "id": "MM_DISR_002",
            "description": "Restaurant equipment failure causing 30-minute delays, frustrated customers, merchant needs immediate coordination support",
            "service_type": "grabfood",
            "location": "Pizza Palace, Downtown",
            "urgency": "medium",
            "affected_orders": 12,
            "merchant_coordination": True
        },
        {
            "id": "MM_DISR_003",
            "description": "Package delivery to wrong address, customer unreachable, high-value fragile electronics, emergency rerouting needed",
            "service_type": "grabexpress",
            "location": "Financial District",
            "urgency": "high",
            "package_value": 75000,
            "fragile": True
        }
    ]
    
    # Process each disruption with multi-model intelligence
    for i, disruption in enumerate(sample_disruptions, 1):
        print(f"\n{'='*80}")
        print(f"🧪 MULTI-MODEL TEST {i}/{len(sample_disruptions)}")
        print(f"📋 ID: {disruption['id']}")
        print(f"📝 Description: {disruption['description']}")
        print(f"{'='*80}")
        
        try:
            start_time = datetime.now()
            result = await logistics_ai.handle_disruption(disruption)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print(f"\n✅ MULTI-MODEL PROCESSING COMPLETE")
            print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
            print(f"🎯 Overall Confidence: {result.get('overall_confidence', 'N/A')}")
            print(f"🤖 Models Used: {result.get('models_used', [])}")
            
            # Show execution details
            if 'task_results' in result:
                print(f"📊 EXECUTION SUMMARY:")
                for task_result in result['task_results']:
                    print(f"  • {task_result['task']}: {task_result['model']} (confidence: {task_result['confidence']:.2f})")
            
        except Exception as e:
            print(f"❌ ERROR PROCESSING DISRUPTION: {str(e)}")
            print(f"🔧 Check system configuration and model availability")
        
        # Brief pause between disruptions
        if i < len(sample_disruptions):
            print("⏳ Waiting 5 seconds before next disruption...")
            await asyncio.sleep(5)
    
    print(f"\n🎉 Multi-Model Logistics System Demo Complete!")
    print("📊 Summary:")
    print(f"   • Multi-Model Architecture: ✅ Active")
    print(f"   • Disruptions Processed: {len(sample_disruptions)}")
    print(f"   • Models Available: {len(logistics_ai.model_manager.get_all_models())}")
    print(f"   • Server: http://localhost:1234")

async def test_lm_studio_connection():
    """Enhanced connection test"""
    print("🧪 Testing LM Studio Connection...")
    
    try:
        config = Config()
        lm_manager = LMStudioManager(config)
        
        # Simple test
        response = await lm_manager.generate_response(
            "Test message: Are you working correctly?", 
            ModelCapability.GENERAL
        )
        
        print("✅ LM Studio Test Successful!")
        print(f"🤖 Model: {response.get('active_model', 'qwen/qwen3-4b')}")
        print(f"🎯 Confidence: {response['confidence']}")
        print(f"💬 Response: {response['content'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LM Studio Test Failed: {str(e)}")
        print("💡 Solutions:")
        print("   1. Make sure LM Studio is running")
        print("   2. Load a model in LM Studio")
        print("   3. Start the server in LM Studio")
        print("   4. Check server is running on http://localhost:1234")
        return False

if __name__ == "__main__":
    print("🚀 Multi-Model Multi-Agent Logistics System - LM Studio Edition")
    print("=" * 80)
    
    # Test connection first
    connection_ok = asyncio.run(test_lm_studio_connection())
    
    if connection_ok:
        print("\n🎯 Connection verified! Running multi-model system...")
        asyncio.run(main())
    else:
        print("\n⚠️  Please fix LM Studio connection before running the system.")
