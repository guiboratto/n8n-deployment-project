#!/usr/bin/env python3
"""
AI DevOps Orchestrator - Main Entry Point
=========================================

Complete AI-powered DevOps team orchestrator based on the sophisticated
system described in the video analysis.

This is the main entry point that creates and coordinates the entire
8-agent DevOps team with AI-powered decision making.

Usage:
    python ai_devops_orchestrator.py --config config.json
    python ai_devops_orchestrator.py --deploy --domain example.com --email admin@example.com
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import DevOpsOrchestrator
from agents.server_setup_agent import ServerSetupAgent
from core.ai_integration import AIIntegration

class AIDevOpsTeam:
    """
    Complete AI DevOps Team
    
    Manages the entire 8-agent DevOps team with AI-powered coordination:
    1. DevOps Chain Orchestrator - Main coordinator
    2. Base Server Setup Agent - Infrastructure setup
    3. Cloudflare DNS Manager Agent - DNS management
    4. Nginx Proxy Configurator Agent - Proxy configuration
    5. N8N Deployment Agent - N8N installation
    6. Supabase Deployment Agent - Supabase setup
    7. System Validator Agent - Quality assurance
    8. Final Report Agent - Comprehensive reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.setup_logging()
        
        # Initialize AI integration
        self.ai_integration = AIIntegration(config.get('ai', {}))
        
        # Initialize orchestrator
        self.orchestrator = DevOpsOrchestrator(config.get('orchestrator', {}))
        
        # Initialize agents
        self.agents = {}
        self.initialize_agents()
        
        self.logger.info("AI DevOps Team initialized")

    def setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Setup main logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_devops_team.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("ai_devops_team")

    def initialize_agents(self):
        """Initialize all DevOps agents"""
        try:
            # 1. Base Server Setup Agent
            server_agent = ServerSetupAgent()
            self.agents['server_setup'] = server_agent
            self.orchestrator.register_agent(server_agent)
            
            # TODO: Initialize other agents
            # 2. DNS Manager Agent
            # 3. N8N Deployment Agent  
            # 4. Supabase Deployment Agent
            # 5. Proxy Configurator Agent
            # 6. System Validator Agent
            # 7. Final Report Agent
            
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise e

    async def deploy_infrastructure(self, deployment_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy complete infrastructure using the AI DevOps team
        
        This is the main function that orchestrates the entire deployment
        process, equivalent to the one-command deployment from the video.
        """
        try:
            self.logger.info("Starting AI-powered infrastructure deployment")
            
            # Validate deployment request
            validated_request = await self.validate_deployment_request(deployment_request)
            
            # Use AI to optimize deployment strategy
            optimized_request = await self.ai_integration.optimize_execution_plan(
                validated_request, 
                self.config.get('constraints', {})
            )
            
            # Execute deployment through orchestrator
            result = await self.orchestrator.deploy_infrastructure(
                optimized_request.get('optimized_plan', validated_request)
            )
            
            # Generate final client report
            client_report = await self.generate_client_report(result)
            
            self.logger.info("Infrastructure deployment completed successfully")
            
            return {
                'success': True,
                'deployment_result': result,
                'client_report': client_report,
                'ai_metrics': self.ai_integration.get_performance_metrics()
            }
            
        except Exception as e:
            self.logger.error(f"Infrastructure deployment failed: {str(e)}")
            
            # Use AI to analyze the failure
            error_analysis = await self.ai_integration.analyze_error(
                'orchestrator',
                {
                    'error': str(e),
                    'deployment_request': deployment_request,
                    'system_state': await self.get_system_state()
                }
            )
            
            return {
                'success': False,
                'error': str(e),
                'error_analysis': error_analysis,
                'recovery_suggestions': error_analysis.get('recovery_actions', [])
            }

    async def validate_deployment_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance deployment request"""
        # Required fields
        required_fields = ['domain', 'email', 'server_ip']
        missing_fields = [field for field in required_fields if not request.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Set defaults
        validated_request = {
            'domain': request['domain'],
            'email': request['email'],
            'server_ip': request['server_ip'],
            'project_name': request.get('project_name', f"project_{datetime.now().strftime('%Y%m%d')}"),
            'client_name': request.get('client_name', 'Default Client'),
            'services': request.get('services', ['n8n', 'supabase']),
            'ssh_credentials': request.get('ssh_credentials', {}),
            'cloudflare_token': request.get('cloudflare_token'),
            'configuration': request.get('configuration', {}),
            'deployment_id': request.get('deployment_id', f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        }
        
        return validated_request

    async def generate_client_report(self, deployment_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive client report"""
        try:
            final_report = deployment_result.get('final_report', {})
            
            # Enhance report with AI insights
            ai_insights = await self.ai_integration.make_decision(
                'reporter',
                {
                    'deployment_result': deployment_result,
                    'final_report': final_report
                },
                'report_enhancement'
            )
            
            client_report = {
                'report_id': final_report.get('deployment_id'),
                'generation_time': datetime.now().isoformat(),
                'deployment_summary': final_report.get('execution_summary', {}),
                'services_deployed': self.extract_deployed_services(final_report),
                'access_information': final_report.get('access_information', {}),
                'credentials': final_report.get('service_credentials', {}),
                'maintenance_guide': final_report.get('maintenance_guide', []),
                'troubleshooting_guide': final_report.get('troubleshooting_guide', {}),
                'ai_insights': ai_insights.get('decision', {}),
                'next_steps': self.generate_next_steps(final_report)
            }
            
            # Save client report
            report_file = f"reports/client_report_{client_report['report_id']}.json"
            with open(report_file, 'w') as f:
                json.dump(client_report, f, indent=2, default=str)
            
            return client_report
            
        except Exception as e:
            self.logger.error(f"Failed to generate client report: {str(e)}")
            return {
                'error': 'Failed to generate client report',
                'details': str(e)
            }

    def extract_deployed_services(self, final_report: Dict[str, Any]) -> List[str]:
        """Extract list of successfully deployed services"""
        deployed_services = []
        
        phase_results = final_report.get('phase_results', {})
        for phase_name, phase_result in phase_results.items():
            if phase_result.get('success'):
                task_results = phase_result.get('task_results', {})
                for task_id, task_result in task_results.items():
                    if task_result.get('success'):
                        if 'n8n' in task_id:
                            deployed_services.append('N8N Workflow Automation')
                        elif 'supabase' in task_id:
                            deployed_services.append('Supabase Backend Platform')
                        elif 'portainer' in task_id:
                            deployed_services.append('Portainer Container Management')
                        elif 'nginx' in task_id or 'proxy' in task_id:
                            deployed_services.append('Nginx Proxy Manager')
        
        return list(set(deployed_services))

    def generate_next_steps(self, final_report: Dict[str, Any]) -> List[str]:
        """Generate next steps for the client"""
        return [
            "Access your services using the provided URLs and credentials",
            "Change default passwords for all services",
            "Configure your first N8N workflow",
            "Set up your Supabase database schema",
            "Configure SSL certificates for your domains",
            "Set up regular backups for your data",
            "Review the maintenance guide for ongoing care"
        ]

    async def get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return {
            'timestamp': datetime.now().isoformat(),
            'orchestrator_status': self.orchestrator.get_orchestrator_status(),
            'agent_count': len(self.agents),
            'ai_metrics': self.ai_integration.get_performance_metrics()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            'overall_health': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check orchestrator
            orchestrator_status = self.orchestrator.get_orchestrator_status()
            health_status['components']['orchestrator'] = {
                'status': 'healthy',
                'active_deployments': orchestrator_status.get('active_deployments', 0),
                'registered_agents': orchestrator_status.get('registered_agents', 0)
            }
            
            # Check AI integration
            ai_metrics = self.ai_integration.get_performance_metrics()
            health_status['components']['ai_integration'] = {
                'status': 'healthy',
                'total_decisions': ai_metrics.get('total_decisions', 0),
                'provider': ai_metrics.get('provider', 'unknown')
            }
            
            # Check agents
            for agent_id, agent in self.agents.items():
                agent_status = agent.get_status_report()
                health_status['components'][agent_id] = {
                    'status': agent_status.get('status', 'unknown'),
                    'performance': agent_status.get('performance_metrics', {})
                }
            
        except Exception as e:
            health_status['overall_health'] = 'degraded'
            health_status['error'] = str(e)
        
        return health_status

def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default configuration
        return {
            'ai': {
                'provider': 'anthropic',
                'model': 'claude-3-sonnet-20240229'
            },
            'orchestrator': {
                'strategy': 'hybrid',
                'parallel_execution': True
            },
            'constraints': {
                'max_deployment_time': 3600,
                'max_parallel_tasks': 4
            }
        }

def create_sample_config():
    """Create sample configuration file"""
    sample_config = {
        "ai": {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "anthropic_api_key": "your_anthropic_api_key_here",
            "openai_api_key": "your_openai_api_key_here"
        },
        "orchestrator": {
            "strategy": "hybrid",
            "parallel_execution": True,
            "max_retries": 3,
            "timeout": 3600
        },
        "constraints": {
            "max_deployment_time": 3600,
            "max_parallel_tasks": 4,
            "resource_limits": {
                "cpu": "80%",
                "memory": "80%"
            }
        },
        "logging": {
            "level": "INFO",
            "file_rotation": True,
            "max_file_size": "10MB"
        }
    }
    
    with open('config_sample.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration created: config_sample.json")
    print("Please update with your API keys and settings.")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI DevOps Team Orchestrator')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--deploy', action='store_true', help='Start deployment')
    parser.add_argument('--domain', help='Domain name for deployment')
    parser.add_argument('--email', help='Email address for deployment')
    parser.add_argument('--server-ip', help='Server IP address')
    parser.add_argument('--ssh-user', default='root', help='SSH username')
    parser.add_argument('--ssh-password', help='SSH password')
    parser.add_argument('--ssh-key', help='SSH private key file')
    parser.add_argument('--cloudflare-token', help='Cloudflare API token')
    parser.add_argument('--services', nargs='+', default=['n8n', 'supabase'], help='Services to deploy')
    parser.add_argument('--health-check', action='store_true', help='Perform health check')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize AI DevOps Team
    devops_team = AIDevOpsTeam(config)
    
    if args.health_check:
        # Perform health check
        health_status = await devops_team.health_check()
        print(json.dumps(health_status, indent=2))
        return
    
    if args.deploy:
        # Validate required arguments
        if not all([args.domain, args.email, args.server_ip]):
            print("Error: --domain, --email, and --server-ip are required for deployment")
            return
        
        # Prepare SSH credentials
        ssh_credentials = {'username': args.ssh_user}
        if args.ssh_password:
            ssh_credentials['password'] = args.ssh_password
        elif args.ssh_key:
            ssh_credentials['key_file'] = args.ssh_key
        else:
            print("Error: Either --ssh-password or --ssh-key must be provided")
            return
        
        # Create deployment request
        deployment_request = {
            'domain': args.domain,
            'email': args.email,
            'server_ip': args.server_ip,
            'ssh_credentials': ssh_credentials,
            'cloudflare_token': args.cloudflare_token,
            'services': args.services,
            'project_name': f"ai_devops_{datetime.now().strftime('%Y%m%d')}",
            'client_name': 'AI DevOps Client'
        }
        
        print("🚀 Starting AI-powered infrastructure deployment...")
        print(f"📋 Domain: {args.domain}")
        print(f"📧 Email: {args.email}")
        print(f"🖥️  Server: {args.server_ip}")
        print(f"🔧 Services: {', '.join(args.services)}")
        print()
        
        # Execute deployment
        result = await devops_team.deploy_infrastructure(deployment_request)
        
        if result['success']:
            print("✅ Deployment completed successfully!")
            print()
            print("📊 Deployment Summary:")
            deployment_result = result['deployment_result']
            print(f"   ⏱️  Total time: {deployment_result.get('execution_time', 0):.2f} seconds")
            print(f"   🎯 Success: {deployment_result.get('success', False)}")
            
            if 'client_report' in result:
                client_report = result['client_report']
                print()
                print("🔗 Access Information:")
                access_info = client_report.get('access_information', {})
                for service, url in access_info.get('main_services', {}).items():
                    print(f"   {service}: {url}")
                
                print()
                print("📋 Next Steps:")
                for step in client_report.get('next_steps', []):
                    print(f"   • {step}")
            
            print()
            print(f"📄 Detailed report saved to: reports/client_report_{deployment_request.get('deployment_id', 'unknown')}.json")
            
        else:
            print("❌ Deployment failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
            if 'error_analysis' in result:
                error_analysis = result['error_analysis']
                print()
                print("🔍 Error Analysis:")
                print(f"   Category: {error_analysis.get('category', 'unknown')}")
                print(f"   Severity: {error_analysis.get('severity', 'unknown')}")
                print(f"   Root Cause: {error_analysis.get('root_cause', 'undetermined')}")
                
                recovery_actions = error_analysis.get('recovery_actions', [])
                if recovery_actions:
                    print()
                    print("🔧 Recovery Suggestions:")
                    for action in recovery_actions:
                        print(f"   • {action}")
    
    else:
        print("AI DevOps Team initialized successfully!")
        print("Use --deploy to start a deployment or --health-check to check system status")
        print("Use --create-config to generate a sample configuration file")

if __name__ == "__main__":
    asyncio.run(main())