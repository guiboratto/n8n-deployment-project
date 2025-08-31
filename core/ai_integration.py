#!/usr/bin/env python3
"""
AI Integration Module
====================

Provides AI-powered decision making capabilities for the DevOps agents.
This module integrates with various AI providers to enable intelligent
automation, error analysis, and adaptive behavior.

Based on the video analysis showing Claude Sonnet 4 integration with
sophisticated prompt engineering and context management.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import openai
import anthropic
import os

class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class AIModel(Enum):
    """AI model configurations"""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    CLAUDE_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"

class AIIntegration:
    """
    AI Integration for DevOps Agents
    
    Provides intelligent decision making, error analysis, and adaptive
    behavior for the entire DevOps team.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = AIProvider(config.get('provider', 'anthropic'))
        self.model = AIModel(config.get('model', 'claude-3-sonnet-20240229'))
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        
        # Context management
        self.conversation_history = {}
        self.agent_contexts = {}
        self.decision_history = []
        
        # Performance tracking
        self.token_usage = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_requests': 0,
            'average_response_time': 0
        }
        
        self.setup_logging()
        self.initialize_clients()

    def setup_logging(self):
        """Setup AI integration logging"""
        self.logger = logging.getLogger("ai_integration")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("logs/ai_integration.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def initialize_clients(self):
        """Initialize AI provider clients"""
        try:
            if self.provider == AIProvider.OPENAI:
                api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                    self.logger.info("OpenAI client initialized")
                else:
                    raise ValueError("OpenAI API key not provided")
            
            elif self.provider == AIProvider.ANTHROPIC:
                api_key = self.config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                    self.logger.info("Anthropic client initialized")
                else:
                    raise ValueError("Anthropic API key not provided")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI client: {str(e)}")
            raise e

    async def make_decision(self, agent_id: str, context: Dict[str, Any], 
                          decision_type: str) -> Dict[str, Any]:
        """
        Make AI-powered decision for an agent
        
        This is the core function that provides intelligent decision making
        capabilities to all agents in the DevOps team.
        """
        start_time = time.time()
        
        try:
            # Prepare decision context
            decision_context = await self.prepare_decision_context(
                agent_id, context, decision_type
            )
            
            # Generate AI prompt
            prompt = await self.generate_decision_prompt(
                agent_id, decision_context, decision_type
            )
            
            # Get AI response
            ai_response = await self.get_ai_response(prompt, agent_id)
            
            # Process and validate response
            decision = await self.process_ai_decision(ai_response, decision_type)
            
            # Update context and history
            await self.update_decision_history(agent_id, decision_context, decision)
            
            response_time = time.time() - start_time
            self.update_performance_metrics(ai_response, response_time)
            
            self.logger.info(f"AI decision made for {agent_id}: {decision_type}")
            
            return {
                'decision': decision,
                'confidence': decision.get('confidence', 0.8),
                'reasoning': decision.get('reasoning', ''),
                'response_time': response_time,
                'token_usage': ai_response.get('token_usage', {})
            }
            
        except Exception as e:
            self.logger.error(f"AI decision failed for {agent_id}: {str(e)}")
            return {
                'decision': {'action': 'fallback', 'parameters': {}},
                'confidence': 0.0,
                'reasoning': f"AI decision failed: {str(e)}",
                'error': str(e)
            }

    async def analyze_error(self, agent_id: str, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze errors with AI to provide intelligent recovery suggestions
        """
        try:
            analysis_prompt = await self.generate_error_analysis_prompt(agent_id, error_context)
            ai_response = await self.get_ai_response(analysis_prompt, agent_id)
            
            analysis = await self.process_error_analysis(ai_response)
            
            return {
                'error_category': analysis.get('category', 'unknown'),
                'root_cause': analysis.get('root_cause', 'undetermined'),
                'severity': analysis.get('severity', 'medium'),
                'recovery_actions': analysis.get('recovery_actions', []),
                'prevention_measures': analysis.get('prevention_measures', []),
                'confidence': analysis.get('confidence', 0.7)
            }
            
        except Exception as e:
            self.logger.error(f"Error analysis failed: {str(e)}")
            return {
                'error_category': 'analysis_failed',
                'root_cause': 'AI analysis unavailable',
                'severity': 'unknown',
                'recovery_actions': ['Manual intervention required'],
                'prevention_measures': [],
                'confidence': 0.0
            }

    async def optimize_execution_plan(self, plan: Dict[str, Any], 
                                    constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize execution plans using AI
        """
        try:
            optimization_prompt = await self.generate_optimization_prompt(plan, constraints)
            ai_response = await self.get_ai_response(optimization_prompt, "orchestrator")
            
            optimized_plan = await self.process_optimization_response(ai_response, plan)
            
            return {
                'optimized_plan': optimized_plan,
                'optimization_applied': True,
                'improvements': optimized_plan.get('improvements', []),
                'estimated_time_savings': optimized_plan.get('time_savings', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Plan optimization failed: {str(e)}")
            return {
                'optimized_plan': plan,
                'optimization_applied': False,
                'error': str(e)
            }

    async def prepare_decision_context(self, agent_id: str, context: Dict[str, Any], 
                                     decision_type: str) -> Dict[str, Any]:
        """Prepare comprehensive context for AI decision making"""
        decision_context = {
            'agent_id': agent_id,
            'decision_type': decision_type,
            'timestamp': datetime.now().isoformat(),
            'current_context': context,
            'agent_history': self.agent_contexts.get(agent_id, {}),
            'recent_decisions': self.get_recent_decisions(agent_id),
            'system_state': await self.get_system_state(),
            'constraints': self.config.get('constraints', {})
        }
        
        return decision_context

    async def generate_decision_prompt(self, agent_id: str, context: Dict[str, Any], 
                                     decision_type: str) -> str:
        """Generate AI prompt for decision making"""
        base_prompt = f"""
You are an AI assistant helping a DevOps agent make intelligent decisions.

Agent: {agent_id}
Decision Type: {decision_type}
Context: {json.dumps(context, indent=2)}

Based on the context provided, analyze the situation and provide a decision with:
1. The recommended action
2. Parameters for the action
3. Confidence level (0.0 to 1.0)
4. Reasoning for the decision
5. Alternative options if applicable
6. Risk assessment

Respond in JSON format:
{{
    "action": "recommended_action",
    "parameters": {{}},
    "confidence": 0.8,
    "reasoning": "explanation of decision",
    "alternatives": [],
    "risk_level": "low|medium|high",
    "expected_outcome": "description"
}}
"""
        
        # Add decision-type specific prompts
        if decision_type == "error_recovery":
            base_prompt += """
Focus on error recovery strategies:
- Analyze the error type and context
- Suggest immediate recovery actions
- Provide fallback options
- Consider system stability
"""
        elif decision_type == "task_planning":
            base_prompt += """
Focus on task planning optimization:
- Analyze task dependencies
- Optimize execution order
- Consider resource constraints
- Minimize execution time
"""
        elif decision_type == "resource_allocation":
            base_prompt += """
Focus on resource allocation:
- Analyze current resource usage
- Optimize resource distribution
- Consider performance requirements
- Prevent resource conflicts
"""
        
        return base_prompt

    async def generate_error_analysis_prompt(self, agent_id: str, 
                                           error_context: Dict[str, Any]) -> str:
        """Generate prompt for error analysis"""
        return f"""
You are an expert DevOps troubleshooter analyzing a system error.

Agent: {agent_id}
Error Context: {json.dumps(error_context, indent=2)}

Analyze this error and provide:
1. Error category classification
2. Root cause analysis
3. Severity assessment
4. Step-by-step recovery actions
5. Prevention measures for the future
6. Confidence in your analysis

Respond in JSON format:
{{
    "category": "configuration|network|permission|resource|service|unknown",
    "root_cause": "detailed explanation",
    "severity": "low|medium|high|critical",
    "recovery_actions": ["step1", "step2", "step3"],
    "prevention_measures": ["measure1", "measure2"],
    "confidence": 0.8,
    "additional_investigation": ["area1", "area2"]
}}
"""

    async def generate_optimization_prompt(self, plan: Dict[str, Any], 
                                         constraints: Dict[str, Any]) -> str:
        """Generate prompt for plan optimization"""
        return f"""
You are an expert DevOps architect optimizing deployment plans.

Current Plan: {json.dumps(plan, indent=2)}
Constraints: {json.dumps(constraints, indent=2)}

Optimize this plan considering:
1. Parallel execution opportunities
2. Dependency optimization
3. Resource efficiency
4. Risk minimization
5. Time optimization

Provide an optimized plan with:
- Improved task ordering
- Parallel execution groups
- Resource allocation
- Risk mitigation
- Time estimates

Respond in JSON format with the optimized plan structure.
"""

    async def get_ai_response(self, prompt: str, agent_id: str) -> Dict[str, Any]:
        """Get response from AI provider"""
        try:
            if self.provider == AIProvider.ANTHROPIC:
                return await self.get_anthropic_response(prompt, agent_id)
            elif self.provider == AIProvider.OPENAI:
                return await self.get_openai_response(prompt, agent_id)
            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"AI response failed: {str(e)}")
            raise e

    async def get_anthropic_response(self, prompt: str, agent_id: str) -> Dict[str, Any]:
        """Get response from Anthropic Claude"""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=self.model.value,
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return {
                'content': response.content[0].text,
                'token_usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                },
                'model': self.model.value
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            raise e

    async def get_openai_response(self, prompt: str, agent_id: str) -> Dict[str, Any]:
        """Get response from OpenAI"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model.value,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DevOps AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return {
                'content': response.choices[0].message.content,
                'token_usage': {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens
                },
                'model': self.model.value
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise e

    async def process_ai_decision(self, ai_response: Dict[str, Any], 
                                decision_type: str) -> Dict[str, Any]:
        """Process and validate AI decision response"""
        try:
            content = ai_response['content']
            
            # Try to parse JSON response
            if content.strip().startswith('{'):
                decision = json.loads(content)
            else:
                # Fallback: extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    decision = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in AI response")
            
            # Validate decision structure
            required_fields = ['action', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in decision:
                    decision[field] = self.get_default_value(field)
            
            # Ensure confidence is within valid range
            decision['confidence'] = max(0.0, min(1.0, decision.get('confidence', 0.5)))
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Failed to process AI decision: {str(e)}")
            return {
                'action': 'fallback',
                'parameters': {},
                'confidence': 0.0,
                'reasoning': f"Failed to process AI response: {str(e)}"
            }

    async def process_error_analysis(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI error analysis response"""
        try:
            content = ai_response['content']
            
            if content.strip().startswith('{'):
                analysis = json.loads(content)
            else:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in error analysis")
            
            # Validate analysis structure
            default_analysis = {
                'category': 'unknown',
                'root_cause': 'undetermined',
                'severity': 'medium',
                'recovery_actions': [],
                'prevention_measures': [],
                'confidence': 0.5
            }
            
            for key, default_value in default_analysis.items():
                if key not in analysis:
                    analysis[key] = default_value
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to process error analysis: {str(e)}")
            return {
                'category': 'analysis_failed',
                'root_cause': 'AI processing error',
                'severity': 'unknown',
                'recovery_actions': ['Manual intervention required'],
                'prevention_measures': [],
                'confidence': 0.0
            }

    async def process_optimization_response(self, ai_response: Dict[str, Any], 
                                          original_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Process plan optimization response"""
        try:
            content = ai_response['content']
            
            if content.strip().startswith('{'):
                optimized = json.loads(content)
            else:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    optimized = json.loads(json_match.group())
                else:
                    # If no valid JSON, return original plan
                    return original_plan
            
            # Merge with original plan structure
            optimized_plan = original_plan.copy()
            optimized_plan.update(optimized)
            
            return optimized_plan
            
        except Exception as e:
            self.logger.error(f"Failed to process optimization: {str(e)}")
            return original_plan

    def get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'action': 'continue',
            'parameters': {},
            'confidence': 0.5,
            'reasoning': 'Default action selected',
            'alternatives': [],
            'risk_level': 'medium'
        }
        return defaults.get(field, None)

    async def get_system_state(self) -> Dict[str, Any]:
        """Get current system state for context"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self.agent_contexts),
            'recent_decisions': len(self.decision_history),
            'system_load': 'normal'  # This could be enhanced with real metrics
        }

    def get_recent_decisions(self, agent_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent decisions for an agent"""
        agent_decisions = [
            decision for decision in self.decision_history 
            if decision.get('agent_id') == agent_id
        ]
        return agent_decisions[-limit:]

    async def update_decision_history(self, agent_id: str, context: Dict[str, Any], 
                                    decision: Dict[str, Any]):
        """Update decision history"""
        decision_record = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'decision': decision
        }
        
        self.decision_history.append(decision_record)
        
        # Keep only recent history (last 100 decisions)
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
        
        # Update agent context
        if agent_id not in self.agent_contexts:
            self.agent_contexts[agent_id] = {'decisions': []}
        
        self.agent_contexts[agent_id]['decisions'].append(decision_record)
        
        # Keep only recent agent decisions
        if len(self.agent_contexts[agent_id]['decisions']) > 20:
            self.agent_contexts[agent_id]['decisions'] = self.agent_contexts[agent_id]['decisions'][-20:]

    def update_performance_metrics(self, ai_response: Dict[str, Any], response_time: float):
        """Update AI performance metrics"""
        token_usage = ai_response.get('token_usage', {})
        
        self.token_usage['total_input_tokens'] += token_usage.get('input_tokens', 0)
        self.token_usage['total_output_tokens'] += token_usage.get('output_tokens', 0)
        self.token_usage['total_requests'] += 1
        
        # Update average response time
        current_avg = self.token_usage['average_response_time']
        total_requests = self.token_usage['total_requests']
        
        self.token_usage['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get AI performance metrics"""
        return {
            'token_usage': self.token_usage.copy(),
            'provider': self.provider.value,
            'model': self.model.value,
            'total_decisions': len(self.decision_history),
            'active_agent_contexts': len(self.agent_contexts)
        }

    async def reset_context(self, agent_id: Optional[str] = None):
        """Reset AI context for an agent or all agents"""
        if agent_id:
            if agent_id in self.agent_contexts:
                del self.agent_contexts[agent_id]
                self.logger.info(f"Reset context for agent {agent_id}")
        else:
            self.agent_contexts.clear()
            self.decision_history.clear()
            self.logger.info("Reset all AI contexts")

    async def export_decision_history(self, file_path: str):
        """Export decision history for analysis"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'decision_history': self.decision_history,
                'agent_contexts': self.agent_contexts,
                'performance_metrics': self.get_performance_metrics()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Decision history exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export decision history: {str(e)}")
            raise e