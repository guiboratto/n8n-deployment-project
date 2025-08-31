#!/usr/bin/env python3
"""
AI DevOps Agent Framework - Base Agent Class
============================================

Based on the sophisticated AI DevOps team architecture from the video analysis.
This implements the core agent functionality with AI decision-making capabilities.

Inspired by the 8-agent DevOps team:
- DevOps Chain Orchestrator
- Base Server Setup Agent  
- Cloudflare DNS Manager Agent
- Nginx Proxy Configurator Agent
- N8N Deployment Agent
- Supabase Deployment Agent
- System Validator Agent
- Final Report Agent
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class AgentMessage:
    """Inter-agent communication message"""
    def __init__(self, sender: str, recipient: str, message_type: str, 
                 content: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now()
        self.processed = False

class BaseAgent(ABC):
    """
    Base class for all AI DevOps agents.
    
    Provides core functionality for:
    - Task planning and execution
    - Inter-agent communication
    - Self-validation and reporting
    - Error handling and recovery
    - AI-powered decision making
    """
    
    def __init__(self, agent_id: str, name: str, description: str, 
                 orchestrator_callback=None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.orchestrator_callback = orchestrator_callback
        
        # Task management
        self.current_task = None
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Communication
        self.message_queue = []
        self.sent_messages = []
        
        # Logging and reporting
        self.setup_logging()
        self.execution_log = []
        self.performance_metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0,
            'average_task_time': 0,
            'success_rate': 0.0
        }
        
        # AI integration
        self.ai_context = {
            'agent_expertise': self.get_expertise_description(),
            'current_context': {},
            'decision_history': [],
            'learned_patterns': []
        }
        
        self.logger.info(f"Agent {self.name} ({self.agent_id}) initialized")

    def setup_logging(self):
        """Setup agent-specific logging"""
        self.logger = logging.getLogger(f"agent.{self.agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler for agent logs
        handler = logging.FileHandler(f"logs/agent_{self.agent_id}.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @abstractmethod
    def get_expertise_description(self) -> str:
        """Return description of agent's expertise and capabilities"""
        pass

    @abstractmethod
    def get_agent_prompt(self) -> str:
        """Return the AI prompt that defines this agent's behavior"""
        pass

    @abstractmethod
    async def execute_primary_function(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task with full AI-powered workflow:
        1. Plan execution
        2. Execute with validation
        3. Self-validate results
        4. Report to orchestrator
        """
        task_id = task.get('id', str(uuid.uuid4()))
        self.current_task = task
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting task: {task.get('description', 'Unknown task')}")
            self.status = AgentStatus.PLANNING
            
            # 1. AI-powered task planning
            execution_plan = await self.create_execution_plan(task)
            self.log_execution_step("Task planning completed", execution_plan)
            
            # 2. Execute the plan
            self.status = AgentStatus.EXECUTING
            result = await self.execute_with_monitoring(execution_plan)
            
            # 3. Self-validation
            self.status = AgentStatus.VALIDATING
            validation_result = await self.validate_execution(result)
            
            if not validation_result['valid']:
                raise Exception(f"Validation failed: {validation_result['errors']}")
            
            # 4. Generate report
            self.status = AgentStatus.REPORTING
            report = await self.generate_task_report(task, result, validation_result)
            
            # 5. Update metrics and notify orchestrator
            execution_time = time.time() - start_time
            self.update_performance_metrics(True, execution_time)
            
            self.status = AgentStatus.COMPLETED
            self.completed_tasks.append(task)
            
            # Notify orchestrator of completion
            if self.orchestrator_callback:
                await self.orchestrator_callback(
                    'task_completed', 
                    {
                        'agent_id': self.agent_id,
                        'task_id': task_id,
                        'result': result,
                        'report': report,
                        'execution_time': execution_time
                    }
                )
            
            self.logger.info(f"Task completed successfully in {execution_time:.2f}s")
            return {
                'success': True,
                'result': result,
                'report': report,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_performance_metrics(False, execution_time)
            
            self.status = AgentStatus.FAILED
            self.failed_tasks.append(task)
            
            error_report = await self.handle_task_failure(task, str(e))
            
            self.logger.error(f"Task failed: {str(e)}")
            
            # Notify orchestrator of failure
            if self.orchestrator_callback:
                await self.orchestrator_callback(
                    'task_failed',
                    {
                        'agent_id': self.agent_id,
                        'task_id': task_id,
                        'error': str(e),
                        'error_report': error_report,
                        'execution_time': execution_time
                    }
                )
            
            return {
                'success': False,
                'error': str(e),
                'error_report': error_report,
                'execution_time': execution_time
            }
        
        finally:
            self.current_task = None
            if self.status != AgentStatus.FAILED:
                self.status = AgentStatus.IDLE

    async def create_execution_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AI-powered execution plan for the task.
        This simulates the intelligent planning shown in the video.
        """
        plan = {
            'task_id': task.get('id'),
            'agent_id': self.agent_id,
            'steps': [],
            'dependencies': task.get('dependencies', []),
            'estimated_duration': 0,
            'risk_assessment': 'low',
            'rollback_plan': []
        }
        
        # AI-powered step generation (simplified)
        steps = await self.generate_execution_steps(task)
        plan['steps'] = steps
        plan['estimated_duration'] = len(steps) * 30  # 30 seconds per step estimate
        
        # Risk assessment
        plan['risk_assessment'] = await self.assess_task_risk(task)
        
        # Rollback plan
        plan['rollback_plan'] = await self.create_rollback_plan(steps)
        
        return plan

    async def generate_execution_steps(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed execution steps for the task"""
        # This would integrate with AI for intelligent step generation
        # For now, we'll use the agent's primary function
        return [
            {
                'step_id': 1,
                'description': f"Execute {self.name} primary function",
                'function': 'execute_primary_function',
                'parameters': task.get('parameters', {}),
                'validation': f"Validate {self.name} execution",
                'timeout': 300
            }
        ]

    async def execute_with_monitoring(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plan with real-time monitoring and error recovery"""
        results = []
        
        for step in plan['steps']:
            step_start = time.time()
            
            try:
                self.logger.info(f"Executing step: {step['description']}")
                
                # Execute the step
                if step['function'] == 'execute_primary_function':
                    step_result = await self.execute_primary_function(step['parameters'])
                else:
                    # Handle other function types
                    step_result = await self.execute_custom_function(
                        step['function'], 
                        step['parameters']
                    )
                
                step_duration = time.time() - step_start
                
                results.append({
                    'step_id': step['step_id'],
                    'success': True,
                    'result': step_result,
                    'duration': step_duration
                })
                
                self.log_execution_step(f"Step {step['step_id']} completed", step_result)
                
            except Exception as e:
                step_duration = time.time() - step_start
                
                self.logger.error(f"Step {step['step_id']} failed: {str(e)}")
                
                # Attempt recovery
                recovery_result = await self.attempt_step_recovery(step, str(e))
                
                if recovery_result['recovered']:
                    results.append({
                        'step_id': step['step_id'],
                        'success': True,
                        'result': recovery_result['result'],
                        'duration': step_duration,
                        'recovered': True
                    })
                else:
                    results.append({
                        'step_id': step['step_id'],
                        'success': False,
                        'error': str(e),
                        'duration': step_duration
                    })
                    raise Exception(f"Step {step['step_id']} failed and could not be recovered: {str(e)}")
        
        return {
            'plan_id': plan.get('task_id'),
            'steps_executed': len(results),
            'steps_successful': len([r for r in results if r['success']]),
            'total_duration': sum(r['duration'] for r in results),
            'step_results': results
        }

    async def validate_execution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the execution results"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checks_performed': []
        }
        
        # Basic validation
        if not result.get('steps_successful', 0):
            validation['valid'] = False
            validation['errors'].append("No steps were executed successfully")
        
        # Agent-specific validation (to be overridden)
        agent_validation = await self.perform_agent_validation(result)
        validation.update(agent_validation)
        
        return validation

    async def perform_agent_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform agent-specific validation (to be overridden by subclasses)"""
        return {
            'checks_performed': ['basic_validation'],
            'errors': [],
            'warnings': []
        }

    async def generate_task_report(self, task: Dict[str, Any], result: Dict[str, Any], 
                                 validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive task report"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'task_id': task.get('id'),
            'task_description': task.get('description'),
            'execution_time': result.get('total_duration', 0),
            'success': validation['valid'],
            'steps_completed': result.get('steps_successful', 0),
            'validation_results': validation,
            'timestamp': datetime.now().isoformat(),
            'performance_impact': self.calculate_performance_impact(result)
        }

    async def handle_task_failure(self, task: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Handle task failure with AI-powered error analysis"""
        return {
            'agent_id': self.agent_id,
            'task_id': task.get('id'),
            'error': error,
            'failure_analysis': await self.analyze_failure(error),
            'recovery_suggestions': await self.suggest_recovery_actions(error),
            'timestamp': datetime.now().isoformat()
        }

    async def analyze_failure(self, error: str) -> Dict[str, Any]:
        """AI-powered failure analysis"""
        # This would integrate with AI for intelligent error analysis
        return {
            'error_category': 'execution_error',
            'likely_causes': ['configuration_issue', 'network_timeout', 'permission_error'],
            'severity': 'medium',
            'impact_assessment': 'task_specific'
        }

    async def suggest_recovery_actions(self, error: str) -> List[str]:
        """Suggest recovery actions based on error analysis"""
        return [
            "Retry with increased timeout",
            "Verify configuration parameters",
            "Check network connectivity",
            "Validate permissions"
        ]

    async def attempt_step_recovery(self, step: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Attempt to recover from step failure"""
        # Simple retry logic (can be enhanced with AI)
        try:
            self.logger.info(f"Attempting recovery for step {step['step_id']}")
            
            # Wait a bit before retry
            await asyncio.sleep(5)
            
            # Retry the step
            if step['function'] == 'execute_primary_function':
                result = await self.execute_primary_function(step['parameters'])
            else:
                result = await self.execute_custom_function(
                    step['function'], 
                    step['parameters']
                )
            
            return {
                'recovered': True,
                'result': result,
                'recovery_method': 'retry_after_delay'
            }
            
        except Exception as e:
            return {
                'recovered': False,
                'error': str(e),
                'recovery_method': 'retry_after_delay'
            }

    async def execute_custom_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom function (to be overridden by subclasses)"""
        raise NotImplementedError(f"Custom function {function_name} not implemented")

    def log_execution_step(self, description: str, data: Any):
        """Log execution step with structured data"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'description': description,
            'data': data
        }
        self.execution_log.append(log_entry)
        self.logger.info(f"{description}: {json.dumps(data, default=str)}")

    def update_performance_metrics(self, success: bool, execution_time: float):
        """Update agent performance metrics"""
        if success:
            self.performance_metrics['tasks_completed'] += 1
        else:
            self.performance_metrics['tasks_failed'] += 1
        
        self.performance_metrics['total_execution_time'] += execution_time
        
        total_tasks = (self.performance_metrics['tasks_completed'] + 
                      self.performance_metrics['tasks_failed'])
        
        if total_tasks > 0:
            self.performance_metrics['average_task_time'] = (
                self.performance_metrics['total_execution_time'] / total_tasks
            )
            self.performance_metrics['success_rate'] = (
                self.performance_metrics['tasks_completed'] / total_tasks
            )

    def calculate_performance_impact(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance impact of the task"""
        return {
            'execution_efficiency': min(1.0, 300 / result.get('total_duration', 300)),
            'resource_usage': 'normal',
            'quality_score': 1.0 if result.get('steps_successful', 0) > 0 else 0.0
        }

    async def assess_task_risk(self, task: Dict[str, Any]) -> str:
        """Assess risk level of the task"""
        # Simple risk assessment (can be enhanced with AI)
        complexity = len(task.get('parameters', {}))
        dependencies = len(task.get('dependencies', []))
        
        if complexity > 10 or dependencies > 5:
            return 'high'
        elif complexity > 5 or dependencies > 2:
            return 'medium'
        else:
            return 'low'

    async def create_rollback_plan(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create rollback plan for the execution steps"""
        rollback_steps = []
        
        for step in reversed(steps):
            rollback_steps.append({
                'step_id': f"rollback_{step['step_id']}",
                'description': f"Rollback {step['description']}",
                'function': f"rollback_{step['function']}",
                'parameters': step.get('parameters', {})
            })
        
        return rollback_steps

    def get_status_report(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status.value,
            'current_task': self.current_task.get('id') if self.current_task else None,
            'queue_length': len(self.task_queue),
            'performance_metrics': self.performance_metrics,
            'last_activity': datetime.now().isoformat()
        }

    async def send_message(self, recipient: str, message_type: str, 
                          content: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM):
        """Send message to another agent or orchestrator"""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            content=content,
            priority=priority
        )
        
        self.sent_messages.append(message)
        
        # Send to orchestrator for routing
        if self.orchestrator_callback:
            await self.orchestrator_callback('route_message', message)

    async def receive_message(self, message: AgentMessage):
        """Receive and process message from another agent"""
        self.message_queue.append(message)
        await self.process_message(message)

    async def process_message(self, message: AgentMessage):
        """Process received message"""
        self.logger.info(f"Received message from {message.sender}: {message.message_type}")
        
        # Handle different message types
        if message.message_type == 'task_assignment':
            await self.process_task(message.content)
        elif message.message_type == 'status_request':
            status = self.get_status_report()
            await self.send_message(message.sender, 'status_response', status)
        elif message.message_type == 'validation_request':
            # Handle validation requests from other agents
            validation_result = await self.validate_external_work(message.content)
            await self.send_message(message.sender, 'validation_response', validation_result)
        
        message.processed = True

    async def validate_external_work(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate work done by other agents (for cross-validation)"""
        return {
            'validator_agent': self.agent_id,
            'valid': True,
            'checks_performed': ['basic_validation'],
            'errors': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }