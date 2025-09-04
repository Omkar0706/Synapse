# core/multi_instance_lm_manager.py - Fixed Version
import openai
import asyncio
from typing import Dict, Any, List

class MultiInstanceLMManager:
    def __init__(self):
        # Different LM Studio instances for different models
        self.model_endpoints = {
            "route_optimization": {
                "model": "qwen/qwen3-4b-thinking-2507",
                "endpoint": "http://localhost:1234",
                "client": openai.OpenAI(base_url="http://localhost:1234", api_key="lm-studio")
            },
            "customer_communication": {
                "model": "microsoft/phi-4-mini-reasoning", 
                "endpoint": "http://localhost:1235",
                "client": openai.OpenAI(base_url="http://localhost:1235", api_key="lm-studio")
            },
            "strategic_planning": {
                "model": "deepseek/deepseek-r1-0528-qwen3-8b",
                "endpoint": "http://localhost:1236", 
                "client": openai.OpenAI(base_url="http://localhost:1236", api_key="lm-studio")
            },
            "emergency_response": {
                "model": "qwen/qwen3-1.7b",
                "endpoint": "http://localhost:1237",
                "client": openai.OpenAI(base_url="http://localhost:1237", api_key="lm-studio")
            }
        }
    
    async def parallel_inference(self, tasks):
        """True parallel inference across multiple LM Studio instances"""
        async def call_model(task_name, prompt, endpoint_config):
            try:
                response = await asyncio.to_thread(
                    endpoint_config["client"].chat.completions.create,
                    model=endpoint_config["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return {
                    "task": task_name,
                    "model": endpoint_config["model"], 
                    "response": response.choices[0].message.content,  # ✅ Fixed
                    "endpoint": endpoint_config["endpoint"],
                    "confidence": 0.85  # Add confidence scoring
                }
            except Exception as e:
                return {"task": task_name, "error": str(e)}
        
        # Execute all tasks in parallel
        parallel_tasks = []
        for task_name, prompt in tasks.items():
            if task_name in self.model_endpoints:
                endpoint_config = self.model_endpoints[task_name]
                parallel_tasks.append(call_model(task_name, prompt, endpoint_config))
        
        # True parallel execution
        results = await asyncio.gather(*parallel_tasks)
        return results
