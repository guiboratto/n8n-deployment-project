#!/usr/bin/env python3
"""
AI DevOps Orchestrator - Main Coordinator
=========================================

The DevOps Chain Orchestrator from the video analysis.
Coordinates the entire 8-agent DevOps team with AI-powered decision making.

This is the "руководитель отдела" (department head) that:
- Receives deployment requests
- Creates execution plans
- Coordinates agent activities
- Manages parallel processing
- Handles error recovery
- Generates final reports
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from .base_agent import BaseAgent, AgentStatus, TaskPriority, AgentMessage

class DeploymentPhase(Enum):
    """Deployment phases"""
    INITIALIZATION = "initialization"
    INFRASTRUCTURE = "infrastructure"
    SERVICES = "services"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"

class OrchestrationStrategy(Enum):
    """Orchestration strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"

class DevOpsOrchestrator:
    """
    Main DevOps Chain Orchestrator
    
    Manages the entire AI DevOps team with sophisticated coordination:
    - Task planning and dependency management
    - Parallel execution coordination
    - Error handling and recovery
    - Quality assurance and validation
    - Professional reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.orchestrator_id = str(uuid.uuid4())
        self.config = config
        self.agents = {}
        self.active_deployments = {}
        self.deployment_history = []
        
        # Orchestration state
        self.current_phase = DeploymentPhase.INITIALIZATION
        self.strategy = OrchestrationStrategy.HYBRID
        
        # Communication and coordination
        self.message_queue = []
        self.agent_status = {}
        self.task_dependencies = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_deployments': 0,
            'successful_deployments': 0,
            'failed_deployments': 0,
            'average_deployment_time': 0,
            'success_rate': 0.0
        }
        
        self.setup_logging()
        self.logger.info(f"DevOps Orchestrator {self.orchestrator_id} initialized")

    def setup_logging(self):
        """Setup orchestrator logging"""
        self.logger = logging.getLogger("orchestrator")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("logs/orchestrator.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.agent_status[agent.agent_id] = AgentStatus.IDLE
        
        # Set orchestrator callback for the agent
        agent.orchestrator_callback = self.handle_agent_callback
        
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    async def handle_agent_callback(self, event_type: str, data: Any):
        """Handle callbacks from agents"""
        if event_type == 'task_completed':
            await self.handle_task_completion(data)
        elif event_type == 'task_failed':
            await self.handle_task_failure(data)
        elif event_type == 'route_message':
            await self.route_message(data)
        elif event_type == 'status_update':
            await self.handle_status_update(data)

    async def deploy_infrastructure(self, deployment_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main deployment function - orchestrates the entire DevOps team
        
        This is the equivalent of the one-command deployment from the video.
        """
        deployment_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting deployment {deployment_id}")
            
            # Initialize deployment
            deployment = await self.initialize_deployment(deployment_id, deployment_request)
            self.active_deployments[deployment_id] = deployment
            
            # Create master execution plan
            execution_plan = await self.create_master_execution_plan(deployment_request)
            deployment['execution_plan'] = execution_plan
            
            # Execute deployment phases
            result = await self.execute_deployment_phases(deployment_id, execution_plan)
            
            # Generate final report
            final_report = await self.generate_final_report(deployment_id, result)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.update_performance_metrics(True, execution_time)
            
            self.logger.info(f"Deployment {deployment_id} completed successfully in {execution_time:.2f}s")
            
            return {
                'deployment_id': deployment_id,
                'success': True,
                'execution_time': execution_time,
                'result': result,
                'final_report': final_report
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_performance_metrics(False, execution_time)
            
            error_report = await self.handle_deployment_failure(deployment_id, str(e))
            
            self.logger.error(f"Deployment {deployment_id} failed: {str(e)}")
            
            return {
                'deployment_id': deployment_id,
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'error_report': error_report
            }

    async def initialize_deployment(self, deployment_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize deployment with client data and configuration"""
        deployment = {
            'id': deployment_id,
            'request': request,
            'start_time': datetime.now(),
            'phase': DeploymentPhase.INITIALIZATION,
            'client_data': await self.process_client_data(request),
            'agent_assignments': {},
            'task_results': {},
            'status': 'initializing'
        }
        
        # Create client data file (like in the video)
        await self.create_client_data_file(deployment_id, deployment['client_data'])
        
        return deployment

    async def process_client_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate client data"""
        client_data = {
            'domain': request.get('domain'),
            'email': request.get('email'),
            'project_name': request.get('project_name'),
            'client_name': request.get('client_name'),
            'server_ip': request.get('server_ip'),
            'ssh_credentials': request.get('ssh_credentials', {}),
            'cloudflare_token': request.get('cloudflare_token'),
            'services': request.get('services', ['n8n', 'supabase']),
            'configuration': request.get('configuration', {})
        }
        
        # Validate required fields
        required_fields = ['domain', 'email', 'project_name', 'server_ip']
        missing_fields = [field for field in required_fields if not client_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return client_data

    async def create_client_data_file(self, deployment_id: str, client_data: Dict[str, Any]):
        """Create client data file for agents to reference"""
        file_path = f"reports/client_data_{deployment_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(client_data, f, indent=2)
        
        self.logger.info(f"Created client data file: {file_path}")

    async def create_master_execution_plan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create master execution plan with AI-powered optimization
        
        This implements the sophisticated planning shown in the video where
        the orchestrator creates a detailed plan and assigns tasks to agents.
        """
        plan = {
            'deployment_id': request.get('deployment_id'),
            'strategy': self.determine_optimal_strategy(request),
            'phases': [],
            'agent_assignments': {},
            'dependencies': {},
            'estimated_duration': 0,
            'parallel_groups': []
        }
        
        # Phase 1: Infrastructure Setup
        infrastructure_phase = await self.plan_infrastructure_phase(request)
        plan['phases'].append(infrastructure_phase)
        
        # Phase 2: Service Deployment (Parallel)
        services_phase = await self.plan_services_phase(request)
        plan['phases'].append(services_phase)
        
        # Phase 3: Configuration and DNS
        config_phase = await self.plan_configuration_phase(request)
        plan['phases'].append(config_phase)
        
        # Phase 4: Validation
        validation_phase = await self.plan_validation_phase(request)
        plan['phases'].append(validation_phase)
        
        # Phase 5: Reporting
        reporting_phase = await self.plan_reporting_phase(request)
        plan['phases'].append(reporting_phase)
        
        # Calculate dependencies and parallel execution groups
        plan['dependencies'] = await self.calculate_task_dependencies(plan['phases'])
        plan['parallel_groups'] = await self.identify_parallel_groups(plan['phases'])
        plan['estimated_duration'] = await self.estimate_total_duration(plan)
        
        return plan

    async def plan_infrastructure_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan infrastructure setup phase"""
        return {
            'phase': DeploymentPhase.INFRASTRUCTURE,
            'description': 'Setup base server infrastructure',
            'tasks': [
                {
                    'id': 'base_server_setup',
                    'agent': 'server_setup_agent',
                    'description': 'Setup Docker, Portainer, and Nginx Proxy Manager',
                    'priority': TaskPriority.CRITICAL,
                    'estimated_duration': 300,
                    'parameters': {
                        'server_ip': request.get('server_ip'),
                        'ssh_credentials': request.get('ssh_credentials'),
                        'install_docker': True,
                        'install_portainer': True,
                        'install_nginx_proxy': True
                    }
                }
            ],
            'parallel_execution': False
        }

    async def plan_services_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan services deployment phase (parallel execution)"""
        tasks = []
        
        if 'n8n' in request.get('services', []):
            tasks.append({
                'id': 'n8n_deployment',
                'agent': 'n8n_agent',
                'description': 'Deploy N8N workflow automation platform',
                'priority': TaskPriority.HIGH,
                'estimated_duration': 600,
                'parameters': {
                    'domain': request.get('domain'),
                    'email': request.get('email'),
                    'database_type': 'postgres',
                    'async_execution': True
                }
            })
        
        if 'supabase' in request.get('services', []):
            tasks.append({
                'id': 'supabase_deployment',
                'agent': 'supabase_agent',
                'description': 'Deploy Supabase backend platform',
                'priority': TaskPriority.HIGH,
                'estimated_duration': 600,
                'parameters': {
                    'domain': request.get('domain'),
                    'email': request.get('email'),
                    'generate_keys': True,
                    'async_execution': True
                }
            })
        
        return {
            'phase': DeploymentPhase.SERVICES,
            'description': 'Deploy core services in parallel',
            'tasks': tasks,
            'parallel_execution': True
        }

    async def plan_configuration_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan configuration phase (DNS and proxy setup)"""
        return {
            'phase': DeploymentPhase.CONFIGURATION,
            'description': 'Configure DNS and proxy settings',
            'tasks': [
                {
                    'id': 'dns_configuration',
                    'agent': 'dns_agent',
                    'description': 'Create DNS records and subdomains',
                    'priority': TaskPriority.HIGH,
                    'estimated_duration': 180,
                    'parameters': {
                        'domain': request.get('domain'),
                        'server_ip': request.get('server_ip'),
                        'cloudflare_token': request.get('cloudflare_token'),
                        'services': request.get('services', [])
                    }
                },
                {
                    'id': 'proxy_configuration',
                    'agent': 'proxy_agent',
                    'description': 'Configure Nginx proxy hosts and SSL',
                    'priority': TaskPriority.HIGH,
                    'estimated_duration': 240,
                    'parameters': {
                        'domain': request.get('domain'),
                        'services': request.get('services', []),
                        'ssl_enabled': True
                    },
                    'dependencies': ['dns_configuration']
                }
            ],
            'parallel_execution': False
        }

    async def plan_validation_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan validation phase"""
        return {
            'phase': DeploymentPhase.VALIDATION,
            'description': 'Validate all services and configurations',
            'tasks': [
                {
                    'id': 'system_validation',
                    'agent': 'validator_agent',
                    'description': 'Comprehensive system validation',
                    'priority': TaskPriority.CRITICAL,
                    'estimated_duration': 300,
                    'parameters': {
                        'services': request.get('services', []),
                        'domain': request.get('domain'),
                        'validate_ssl': True,
                        'validate_dns': True,
                        'validate_services': True
                    }
                }
            ],
            'parallel_execution': False
        }

    async def plan_reporting_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Plan reporting phase"""
        return {
            'phase': DeploymentPhase.REPORTING,
            'description': 'Generate comprehensive deployment report',
            'tasks': [
                {
                    'id': 'final_report',
                    'agent': 'reporter_agent',
                    'description': 'Create final client report',
                    'priority': TaskPriority.MEDIUM,
                    'estimated_duration': 120,
                    'parameters': {
                        'client_data': request,
                        'include_credentials': True,
                        'include_maintenance_guide': True,
                        'format': 'markdown'
                    }
                }
            ],
            'parallel_execution': False
        }

    def determine_optimal_strategy(self, request: Dict[str, Any]) -> OrchestrationStrategy:
        """Determine optimal orchestration strategy based on request complexity"""
        service_count = len(request.get('services', []))
        complexity_score = service_count + len(request.get('configuration', {}))
        
        if complexity_score > 10:
            return OrchestrationStrategy.ADAPTIVE
        elif complexity_score > 5:
            return OrchestrationStrategy.HYBRID
        else:
            return OrchestrationStrategy.PARALLEL

    async def execute_deployment_phases(self, deployment_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all deployment phases according to the plan"""
        deployment = self.active_deployments[deployment_id]
        results = {}
        
        for phase_config in plan['phases']:
            phase = phase_config['phase']
            self.current_phase = phase
            deployment['phase'] = phase
            
            self.logger.info(f"Starting phase: {phase.value}")
            
            try:
                if phase_config.get('parallel_execution', False):
                    phase_result = await self.execute_parallel_phase(deployment_id, phase_config)
                else:
                    phase_result = await self.execute_sequential_phase(deployment_id, phase_config)
                
                results[phase.value] = phase_result
                
                # Update deployment status
                deployment['task_results'][phase.value] = phase_result
                
                self.logger.info(f"Phase {phase.value} completed successfully")
                
            except Exception as e:
                self.logger.error(f"Phase {phase.value} failed: {str(e)}")
                raise Exception(f"Deployment failed in phase {phase.value}: {str(e)}")
        
        return results

    async def execute_parallel_phase(self, deployment_id: str, phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute phase tasks in parallel"""
        tasks = phase_config['tasks']
        
        # Create coroutines for all tasks
        task_coroutines = []
        for task in tasks:
            agent_id = self.find_agent_by_type(task['agent'])
            if agent_id:
                coroutine = self.execute_agent_task(agent_id, task)
                task_coroutines.append(coroutine)
        
        # Execute all tasks in parallel
        task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        results = {}
        for i, result in enumerate(task_results):
            task_id = tasks[i]['id']
            if isinstance(result, Exception):
                results[task_id] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                results[task_id] = result
        
        return {
            'phase': phase_config['phase'].value,
            'parallel_execution': True,
            'task_results': results,
            'success': all(r.get('success', False) for r in results.values())
        }

    async def execute_sequential_phase(self, deployment_id: str, phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute phase tasks sequentially"""
        tasks = phase_config['tasks']
        results = {}
        
        for task in tasks:
            # Check dependencies
            if not await self.check_task_dependencies(task, results):
                raise Exception(f"Dependencies not met for task {task['id']}")
            
            agent_id = self.find_agent_by_type(task['agent'])
            if not agent_id:
                raise Exception(f"No agent found for type {task['agent']}")
            
            task_result = await self.execute_agent_task(agent_id, task)
            results[task['id']] = task_result
            
            if not task_result.get('success', False):
                raise Exception(f"Task {task['id']} failed: {task_result.get('error', 'Unknown error')}")
        
        return {
            'phase': phase_config['phase'].value,
            'parallel_execution': False,
            'task_results': results,
            'success': True
        }

    async def execute_agent_task(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise Exception(f"Agent {agent_id} not found")
        
        self.logger.info(f"Assigning task {task['id']} to agent {agent.name}")
        
        # Update agent status
        self.agent_status[agent_id] = AgentStatus.EXECUTING
        
        try:
            result = await agent.process_task(task)
            self.agent_status[agent_id] = AgentStatus.IDLE
            return result
            
        except Exception as e:
            self.agent_status[agent_id] = AgentStatus.FAILED
            raise e

    def find_agent_by_type(self, agent_type: str) -> Optional[str]:
        """Find agent ID by agent type"""
        type_mapping = {
            'server_setup_agent': 'server_setup',
            'n8n_agent': 'n8n_deployment',
            'supabase_agent': 'supabase_deployment',
            'dns_agent': 'dns_manager',
            'proxy_agent': 'proxy_configurator',
            'validator_agent': 'system_validator',
            'reporter_agent': 'final_reporter'
        }
        
        target_type = type_mapping.get(agent_type, agent_type)
        
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'agent_type') and agent.agent_type == target_type:
                return agent_id
            elif target_type in agent.name.lower():
                return agent_id
        
        return None

    async def check_task_dependencies(self, task: Dict[str, Any], completed_tasks: Dict[str, Any]) -> bool:
        """Check if task dependencies are satisfied"""
        dependencies = task.get('dependencies', [])
        
        for dep in dependencies:
            if dep not in completed_tasks:
                return False
            if not completed_tasks[dep].get('success', False):
                return False
        
        return True

    async def calculate_task_dependencies(self, phases: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Calculate task dependencies across phases"""
        dependencies = {}
        
        for phase in phases:
            for task in phase['tasks']:
                task_deps = task.get('dependencies', [])
                dependencies[task['id']] = task_deps
        
        return dependencies

    async def identify_parallel_groups(self, phases: List[Dict[str, Any]]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        parallel_groups = []
        
        for phase in phases:
            if phase.get('parallel_execution', False):
                group = [task['id'] for task in phase['tasks']]
                parallel_groups.append(group)
        
        return parallel_groups

    async def estimate_total_duration(self, plan: Dict[str, Any]) -> int:
        """Estimate total deployment duration"""
        total_duration = 0
        
        for phase in plan['phases']:
            if phase.get('parallel_execution', False):
                # For parallel phases, take the maximum duration
                phase_duration = max(task.get('estimated_duration', 0) for task in phase['tasks'])
            else:
                # For sequential phases, sum all durations
                phase_duration = sum(task.get('estimated_duration', 0) for task in phase['tasks'])
            
            total_duration += phase_duration
        
        return total_duration

    async def handle_task_completion(self, data: Dict[str, Any]):
        """Handle task completion from agents"""
        agent_id = data['agent_id']
        task_id = data['task_id']
        
        self.logger.info(f"Task {task_id} completed by agent {agent_id}")
        self.agent_status[agent_id] = AgentStatus.IDLE

    async def handle_task_failure(self, data: Dict[str, Any]):
        """Handle task failure from agents"""
        agent_id = data['agent_id']
        task_id = data['task_id']
        error = data['error']
        
        self.logger.error(f"Task {task_id} failed on agent {agent_id}: {error}")
        self.agent_status[agent_id] = AgentStatus.FAILED
        
        # Attempt recovery or escalation
        await self.handle_task_recovery(data)

    async def handle_task_recovery(self, failure_data: Dict[str, Any]):
        """Handle task recovery and error escalation"""
        # Implement intelligent recovery strategies
        recovery_strategies = [
            'retry_with_different_agent',
            'modify_task_parameters',
            'skip_non_critical_task',
            'escalate_to_human'
        ]
        
        # For now, log the failure for manual intervention
        self.logger.warning(f"Task recovery needed: {failure_data}")

    async def route_message(self, message: AgentMessage):
        """Route messages between agents"""
        recipient_agent = self.agents.get(message.recipient)
        if recipient_agent:
            await recipient_agent.receive_message(message)
        else:
            self.logger.warning(f"Message recipient not found: {message.recipient}")

    async def handle_status_update(self, data: Dict[str, Any]):
        """Handle status updates from agents"""
        agent_id = data.get('agent_id')
        status = data.get('status')
        
        if agent_id and status:
            self.agent_status[agent_id] = AgentStatus(status)

    async def generate_final_report(self, deployment_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final deployment report"""
        deployment = self.active_deployments[deployment_id]
        
        # Collect all agent reports
        agent_reports = {}
        for phase_name, phase_result in results.items():
            if 'task_results' in phase_result:
                for task_id, task_result in phase_result['task_results'].items():
                    if 'report' in task_result:
                        agent_reports[task_id] = task_result['report']
        
        # Generate comprehensive report
        final_report = {
            'deployment_id': deployment_id,
            'client_data': deployment['client_data'],
            'execution_summary': {
                'start_time': deployment['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_duration': (datetime.now() - deployment['start_time']).total_seconds(),
                'phases_completed': len(results),
                'success': all(r.get('success', False) for r in results.values())
            },
            'phase_results': results,
            'agent_reports': agent_reports,
            'service_credentials': await self.collect_service_credentials(deployment_id),
            'access_information': await self.generate_access_information(deployment),
            'maintenance_guide': await self.generate_maintenance_guide(deployment),
            'troubleshooting_guide': await self.generate_troubleshooting_guide(deployment)
        }
        
        # Save report to file
        report_file = f"reports/final_report_{deployment_id}.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        return final_report

    async def collect_service_credentials(self, deployment_id: str) -> Dict[str, Any]:
        """Collect all service credentials from agent reports"""
        # This would collect credentials from various agents
        return {
            'portainer': {
                'url': f"https://portainer.{self.active_deployments[deployment_id]['client_data']['domain']}",
                'username': 'admin',
                'password': '[Generated during deployment]'
            },
            'n8n': {
                'url': f"https://n8n.{self.active_deployments[deployment_id]['client_data']['domain']}",
                'email': self.active_deployments[deployment_id]['client_data']['email'],
                'password': '[Generated during deployment]'
            },
            'supabase': {
                'url': f"https://supabase.{self.active_deployments[deployment_id]['client_data']['domain']}",
                'email': self.active_deployments[deployment_id]['client_data']['email'],
                'password': '[Generated during deployment]',
                'api_key': '[Generated during deployment]'
            }
        }

    async def generate_access_information(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate access information for all services"""
        domain = deployment['client_data']['domain']
        
        return {
            'main_services': {
                'n8n': f"https://n8n.{domain}",
                'supabase': f"https://supabase.{domain}",
                'portainer': f"https://portainer.{domain}",
                'nginx_proxy': f"https://npm.{domain}"
            },
            'api_endpoints': {
                'n8n_api': f"https://n8n.{domain}/api",
                'n8n_webhooks': f"https://n8n.{domain}/webhook",
                'supabase_api': f"https://supabase.{domain}/rest/v1"
            },
            'ssl_certificates': 'Automatically managed by Let\'s Encrypt',
            'dns_records': f"All subdomains configured in Cloudflare for {domain}"
        }

    async def generate_maintenance_guide(self, deployment: Dict[str, Any]) -> List[str]:
        """Generate maintenance guide"""
        return [
            "Regular backup of N8N workflows and Supabase data",
            "Monitor SSL certificate renewal (automatic)",
            "Update Docker containers monthly",
            "Monitor server resources and disk space",
            "Review security logs weekly",
            "Test backup restoration quarterly"
        ]

    async def generate_troubleshooting_guide(self, deployment: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate troubleshooting guide"""
        return {
            'service_not_accessible': [
                "Check DNS propagation",
                "Verify SSL certificate status",
                "Check Docker container status",
                "Review Nginx proxy configuration"
            ],
            'performance_issues': [
                "Monitor server resources",
                "Check Docker container logs",
                "Verify database connections",
                "Review network connectivity"
            ],
            'ssl_certificate_issues': [
                "Check Let's Encrypt rate limits",
                "Verify domain ownership",
                "Review Nginx proxy manager logs",
                "Manually renew certificates if needed"
            ]
        }

    async def handle_deployment_failure(self, deployment_id: str, error: str) -> Dict[str, Any]:
        """Handle deployment failure with comprehensive error reporting"""
        deployment = self.active_deployments.get(deployment_id, {})
        
        return {
            'deployment_id': deployment_id,
            'failure_time': datetime.now().isoformat(),
            'error': error,
            'phase_at_failure': self.current_phase.value,
            'completed_phases': list(deployment.get('task_results', {}).keys()),
            'agent_status': dict(self.agent_status),
            'recovery_suggestions': await self.generate_recovery_suggestions(error),
            'rollback_plan': await self.generate_rollback_plan(deployment_id)
        }

    async def generate_recovery_suggestions(self, error: str) -> List[str]:
        """Generate recovery suggestions based on error analysis"""
        return [
            "Review error logs for specific failure points",
            "Verify server connectivity and credentials",
            "Check service dependencies and prerequisites",
            "Retry deployment with corrected parameters",
            "Contact support with deployment ID and error details"
        ]

    async def generate_rollback_plan(self, deployment_id: str) -> List[str]:
        """Generate rollback plan for failed deployment"""
        return [
            "Stop all running Docker containers",
            "Remove created DNS records",
            "Clean up temporary files and configurations",
            "Restore server to pre-deployment state",
            "Document lessons learned for future deployments"
        ]

    def update_performance_metrics(self, success: bool, execution_time: float):
        """Update orchestrator performance metrics"""
        self.performance_metrics['total_deployments'] += 1
        
        if success:
            self.performance_metrics['successful_deployments'] += 1
        else:
            self.performance_metrics['failed_deployments'] += 1
        
        # Update average deployment time
        total_deployments = self.performance_metrics['total_deployments']
        current_avg = self.performance_metrics['average_deployment_time']
        self.performance_metrics['average_deployment_time'] = (
            (current_avg * (total_deployments - 1) + execution_time) / total_deployments
        )
        
        # Update success rate
        self.performance_metrics['success_rate'] = (
            self.performance_metrics['successful_deployments'] / total_deployments
        )

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            'orchestrator_id': self.orchestrator_id,
            'current_phase': self.current_phase.value,
            'active_deployments': len(self.active_deployments),
            'registered_agents': len(self.agents),
            'agent_status': {agent_id: status.value for agent_id, status in self.agent_status.items()},
            'performance_metrics': self.performance_metrics,
            'last_activity': datetime.now().isoformat()
        }