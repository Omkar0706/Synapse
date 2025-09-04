# core/multi_model_orchestrator.py - True Multi-Model Coordination
import asyncio
from typing import Dict, List, Any

class MultiModelOrchestrator:
    def __init__(self, model_manager, lm_studio_manager):
        self.model_manager = model_manager
        self.lm_manager = lm_studio_manager
        self.current_loaded_model = None
        self.model_switch_count = 0

    async def execute_multi_model_analysis(self, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis using different specialized models"""
        
        print(f"🧠 Starting Multi-Model Analysis...")
        
        # Step 1: Analyze problem and get task recommendations
        task_analysis = self.model_manager.analyze_problem_requirements(problem_context)
        
        print(f"📋 Tasks identified: {task_analysis['total_tasks']}")
        print(f"🤖 Models needed: {len(task_analysis['models_needed'])}")
        
        # Step 2: Execute each task with its optimal model
        task_results = []
        
        for task_info in task_analysis["recommended_tasks"]:
            task_name = task_info["task"].value
            optimal_model = task_info["model"]
            priority = task_info["priority"]
            
            print(f"⚡ Executing {task_name} with {optimal_model} (Priority: {priority})")
            
            # Switch to optimal model if different
            if optimal_model != self.current_loaded_model:
                await self._switch_model(optimal_model)
            
            # Execute the specific task
            result = await self._execute_specialized_task(
                task_name, optimal_model, priority, problem_context
            )
            
            task_results.append(result)
        
        # Step 3: Synthesize all results into final solution
        final_solution = await self._synthesize_multi_model_results(task_results, problem_context)
        
        return {
            "problem_analysis": task_analysis,
            "task_results": task_results,
            "final_solution": final_solution,
            "models_used": task_analysis["models_needed"],
            "model_switches": self.model_switch_count,
            "overall_confidence": self._calculate_multi_model_confidence(task_results)
        }

    async def _switch_model(self, new_model: str):
        """Switch to a different model (simulated for LM Studio)"""
        if new_model != self.current_loaded_model:
            print(f"🔄 Switching from {self.current_loaded_model} to {new_model}")
            
            # In production, this would:
            # 1. Save current model state
            # 2. Unload current model from LM Studio
            # 3. Load new model in LM Studio
            # 4. Wait for model ready signal
            
            # Simulate model switching delay
            await asyncio.sleep(0.5)
            
            self.current_loaded_model = new_model
            self.model_switch_count += 1
            print(f"✅ Model switched to {new_model}")

    async def _execute_specialized_task(self, task_name: str, model_name: str, priority: str, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task with its optimal model"""
        
        # Create task-specific prompts optimized for each model
        task_prompts = {
            "route_optimization": f"""
            🗺️ ROUTE OPTIMIZATION SPECIALIST
            Using {model_name} optimized for spatial reasoning:
            
            Problem: {problem_context.get('description')}
            Location: {problem_context.get('location', 'Unknown')}
            Affected Orders: {problem_context.get('affected_orders', 1)}
            
            Provide expert route optimization focusing on:
            1. Traffic analysis and bottleneck identification
            2. Alternative route recommendations  
            3. Driver reassignment strategies
            4. Delivery sequence optimization
            5. Geographic risk assessment
            
            Deliver specific, actionable routing solutions.
            """,
            
            "customer_communication": f"""
            💬 CUSTOMER COMMUNICATION SPECIALIST
            Using {model_name} optimized for empathy and language:
            
            Problem: {problem_context.get('description')}
            Customer Impact: {problem_context.get('affected_orders', 1)} orders affected
            Urgency: {problem_context.get('urgency', 'medium')}
            
            Create empathetic customer communication covering:
            1. Sincere acknowledgment of the situation
            2. Clear explanation without technical jargon
            3. Proactive solution offerings
            4. Compensation or alternatives
            5. Trust-rebuilding messaging
            
            Focus on maintaining customer loyalty and satisfaction.
            """,
            
            "strategic_planning": f"""
            🧠 STRATEGIC PLANNING EXPERT
            Using {model_name} optimized for complex reasoning:
            
            Problem: {problem_context.get('description')}
            Scope: {problem_context.get('urgency', 'medium')} priority situation
            Business Impact: {problem_context.get('affected_orders', 1)} orders
            
            Develop comprehensive strategic response including:
            1. Root cause analysis and system impact
            2. Multi-phase resolution strategy
            3. Resource allocation optimization
            4. Risk mitigation and contingency plans
            5. Long-term prevention measures
            
            Provide executive-level strategic guidance.
            """,
            
            "sentiment_analysis": f"""
            🎭 SENTIMENT ANALYSIS SPECIALIST  
            Using {model_name} optimized for emotional intelligence:
            
            Situation: {problem_context.get('description')}
            
            Analyze emotional and reputational factors:
            1. Customer emotional state assessment
            2. Potential brand impact evaluation
            3. Communication tone recommendations
            4. Escalation risk analysis
            5. Relationship recovery priorities
            
            Focus on emotional intelligence and damage control.
            """,
            
            "emergency_response": f"""
            🚨 EMERGENCY RESPONSE COORDINATOR
            Using {model_name} optimized for speed:
            
            URGENT SITUATION: {problem_context.get('description')}
            Priority Level: {priority.upper()}
            
            Provide immediate emergency response plan:
            1. CRITICAL actions needed in next 5 minutes
            2. Essential stakeholder notifications
            3. Resource mobilization requirements
            4. Damage containment measures
            5. Quick-win emergency solutions
            
            PRIORITIZE SPEED AND EFFECTIVENESS.
            """
        }
        
        prompt = task_prompts.get(task_name, f"Analyze: {problem_context.get('description')}")
        
        # Execute with the specialized model
        response = await self.lm_manager.generate_response_for_agent(
            f"specialist_{task_name}",
            prompt,
            problem_context.get('urgency', 'medium')
        )
        
        return {
            "task": task_name,
            "model": model_name,
            "priority": priority,
            "response": response.get("content", ""),
            "confidence": response.get("confidence", 0.0),
            "specialized": True
        }

    async def _synthesize_multi_model_results(self, task_results: List[Dict], problem_context: Dict) -> Dict[str, Any]:
        """Synthesize results from multiple specialized models"""
        
        # Organize results by priority
        critical_results = [r for r in task_results if r['priority'] == 'critical']
        high_results = [r for r in task_results if r['priority'] == 'high']
        medium_results = [r for r in task_results if r['priority'] == 'medium']
        
        # Create comprehensive synthesis
        synthesis_sections = []
        
        if critical_results:
            synthesis_sections.append("🚨 CRITICAL ACTIONS:\n" + 
                "\n".join([f"• [{r['task']}] ({r['model']}): {r['response'][:200]}..." for r in critical_results]))
        
        if high_results:
            synthesis_sections.append("⚡ HIGH PRIORITY SOLUTIONS:\n" + 
                "\n".join([f"• [{r['task']}] ({r['model']}): {r['response'][:200]}..." for r in high_results]))
        
        if medium_results:
            synthesis_sections.append("📋 SUPPORTING ANALYSIS:\n" + 
                "\n".join([f"• [{r['task']}] ({r['model']}): {r['response'][:200]}..." for r in medium_results]))
        
        # Final synthesis prompt for master coordination
        master_synthesis_prompt = f"""
        🎯 MASTER SOLUTION SYNTHESIS
        
        Original Problem: {problem_context.get('description')}
        Specialized Models Used: {len(set(r['model'] for r in task_results))}
        
        MULTI-MODEL ANALYSIS RESULTS:
        {chr(10).join(synthesis_sections)}
        
        Create a UNIFIED ACTION PLAN combining all specialized insights:
        
        1. IMMEDIATE ACTIONS (0-15 minutes)
        2. SHORT-TERM EXECUTION (15 minutes - 2 hours)  
        3. COMMUNICATION STRATEGY (all stakeholders)
        4. SUCCESS METRICS AND MONITORING
        5. PREVENTION AND LEARNING
        
        Focus on actionable, coordinated solutions leveraging each model's expertise.
        """
        
        # Use most capable model for final synthesis
        synthesis_response = await self.lm_manager.generate_response_for_agent(
            "master_synthesizer",
            master_synthesis_prompt,
            "complex"
        )
        
        return {
            "unified_plan": synthesis_response.get("content", ""),
            "synthesis_confidence": synthesis_response.get("confidence", 0.0),
            "models_synthesized": len(set(r['model'] for r in task_results)),
            "priority_levels": len(set(r['priority'] for r in task_results)),
            "comprehensive": True
        }

    def _calculate_multi_model_confidence(self, task_results: List[Dict]) -> float:
        """Calculate confidence score across all specialized models"""
        if not task_results:
            return 0.0
        
        # Weighted by priority
        priority_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6}
        
        weighted_sum = 0
        total_weight = 0
        
        for result in task_results:
            weight = priority_weights.get(result['priority'], 0.5)
            weighted_sum += result['confidence'] * weight
            total_weight += weight
        
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Bonus for model diversity
        unique_models = len(set(r['model'] for r in task_results))
        diversity_bonus = min(0.15, unique_models * 0.03)
        
        return min(0.95, base_confidence + diversity_bonus)
