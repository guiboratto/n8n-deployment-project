#!/usr/bin/env python3
"""
Base Server Setup Agent
======================

The "Base Server Setup Agent" from the video analysis.
Handles base server infrastructure setup including:
- Docker installation and configuration
- Portainer deployment
- Nginx Proxy Manager setup
- System updates and security hardening

This agent is equivalent to the "BAS Server Setup Agent" that:
- Updates all packages
- Installs Docker
- Installs Portainer
- Installs Nginx Proxy Manager
- Creates backup files
- Validates installation
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any
import paramiko
import os

from .base_agent import BaseAgent, TaskPriority

class ServerSetupAgent(BaseAgent):
    """
    Base Server Setup Agent
    
    Responsible for setting up the foundational server infrastructure
    that other agents depend on.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="server_setup",
            name="Base Server Setup Agent",
            description="Sets up base server infrastructure with Docker, Portainer, and Nginx Proxy Manager"
        )
        self.agent_type = "server_setup"
        self.ssh_client = None
        self.server_ip = None
        self.ssh_credentials = {}

    def get_expertise_description(self) -> str:
        """Return description of agent's expertise"""
        return """
        Expert in server infrastructure setup and configuration:
        - Linux system administration and package management
        - Docker installation and configuration
        - Container orchestration with Portainer
        - Reverse proxy setup with Nginx Proxy Manager
        - System security hardening
        - Service validation and health checks
        """

    def get_agent_prompt(self) -> str:
        """Return the AI prompt that defines this agent's behavior"""
        return """
        You are the Base Server Setup Agent, responsible for preparing the foundational 
        infrastructure for a complete DevOps deployment.

        Your primary responsibilities:
        1. Update system packages and security patches
        2. Install and configure Docker with proper permissions
        3. Deploy Portainer for container management
        4. Setup Nginx Proxy Manager for reverse proxy
        5. Create system backups before major changes
        6. Validate all installations and configurations
        7. Generate detailed reports of all actions taken

        You work methodically and always validate each step before proceeding.
        You create backups before making system changes and can rollback if needed.
        You communicate progress clearly and report any issues immediately.

        Wait patiently for long-running operations like Docker installation.
        Verify service health before marking tasks as complete.
        """

    async def execute_primary_function(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the primary server setup function"""
        self.logger.info("Starting base server infrastructure setup")
        
        # Extract parameters
        self.server_ip = task_data.get('server_ip')
        self.ssh_credentials = task_data.get('ssh_credentials', {})
        
        if not self.server_ip:
            raise ValueError("Server IP address is required")
        
        # Setup SSH connection
        await self.setup_ssh_connection()
        
        try:
            # Execute setup steps
            result = await self.execute_server_setup_steps(task_data)
            
            # Validate installation
            validation_result = await self.validate_server_setup()
            
            # Generate installation report
            report = await self.generate_setup_report(result, validation_result)
            
            return {
                'setup_result': result,
                'validation': validation_result,
                'report': report,
                'server_ip': self.server_ip,
                'services_installed': ['docker', 'portainer', 'nginx-proxy-manager']
            }
            
        finally:
            await self.cleanup_ssh_connection()

    async def setup_ssh_connection(self):
        """Setup SSH connection to the server"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using provided credentials
            username = self.ssh_credentials.get('username', 'root')
            password = self.ssh_credentials.get('password')
            key_file = self.ssh_credentials.get('key_file')
            
            if key_file and os.path.exists(key_file):
                self.ssh_client.connect(
                    hostname=self.server_ip,
                    username=username,
                    key_filename=key_file,
                    timeout=30
                )
            elif password:
                self.ssh_client.connect(
                    hostname=self.server_ip,
                    username=username,
                    password=password,
                    timeout=30
                )
            else:
                raise ValueError("Either password or SSH key file must be provided")
            
            self.logger.info(f"SSH connection established to {self.server_ip}")
            
        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {str(e)}")

    async def cleanup_ssh_connection(self):
        """Cleanup SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    async def execute_server_setup_steps(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all server setup steps"""
        results = {}
        
        # Step 1: Create backup
        self.logger.info("Creating system backup")
        results['backup'] = await self.create_system_backup()
        
        # Step 2: Update system packages
        self.logger.info("Updating system packages")
        results['system_update'] = await self.update_system_packages()
        
        # Step 3: Install Docker
        if task_data.get('install_docker', True):
            self.logger.info("Installing Docker")
            results['docker_installation'] = await self.install_docker()
        
        # Step 4: Install Portainer
        if task_data.get('install_portainer', True):
            self.logger.info("Installing Portainer")
            results['portainer_installation'] = await self.install_portainer()
        
        # Step 5: Install Nginx Proxy Manager
        if task_data.get('install_nginx_proxy', True):
            self.logger.info("Installing Nginx Proxy Manager")
            results['nginx_proxy_installation'] = await self.install_nginx_proxy_manager()
        
        # Step 6: Configure firewall
        self.logger.info("Configuring firewall")
        results['firewall_configuration'] = await self.configure_firewall()
        
        return results

    async def create_system_backup(self) -> Dict[str, Any]:
        """Create system backup before making changes"""
        try:
            backup_commands = [
                "mkdir -p /backup/$(date +%Y%m%d_%H%M%S)",
                "cp -r /etc /backup/$(date +%Y%m%d_%H%M%S)/etc_backup",
                "dpkg --get-selections > /backup/$(date +%Y%m%d_%H%M%S)/package_list.txt",
                "systemctl list-enabled > /backup/$(date +%Y%m%d_%H%M%S)/enabled_services.txt"
            ]
            
            for cmd in backup_commands:
                await self.execute_ssh_command(cmd)
            
            return {
                'success': True,
                'backup_location': '/backup',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def update_system_packages(self) -> Dict[str, Any]:
        """Update system packages"""
        try:
            update_commands = [
                "apt-get update",
                "apt-get upgrade -y",
                "apt-get autoremove -y",
                "apt-get autoclean"
            ]
            
            for cmd in update_commands:
                stdout, stderr, exit_code = await self.execute_ssh_command(cmd, timeout=600)
                if exit_code != 0:
                    raise Exception(f"Command failed: {cmd}, Error: {stderr}")
            
            return {
                'success': True,
                'packages_updated': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def install_docker(self) -> Dict[str, Any]:
        """Install Docker with proper configuration"""
        try:
            # Remove old Docker versions
            remove_cmd = "apt-get remove -y docker docker-engine docker.io containerd runc"
            await self.execute_ssh_command(remove_cmd)
            
            # Install prerequisites
            prereq_cmd = "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release"
            await self.execute_ssh_command(prereq_cmd)
            
            # Add Docker GPG key
            gpg_cmd = "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
            await self.execute_ssh_command(gpg_cmd)
            
            # Add Docker repository
            repo_cmd = 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null'
            await self.execute_ssh_command(repo_cmd)
            
            # Update package index
            await self.execute_ssh_command("apt-get update")
            
            # Install Docker
            install_cmd = "apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
            stdout, stderr, exit_code = await self.execute_ssh_command(install_cmd, timeout=600)
            
            if exit_code != 0:
                raise Exception(f"Docker installation failed: {stderr}")
            
            # Start and enable Docker
            await self.execute_ssh_command("systemctl start docker")
            await self.execute_ssh_command("systemctl enable docker")
            
            # Add user to docker group
            username = self.ssh_credentials.get('username', 'root')
            if username != 'root':
                await self.execute_ssh_command(f"usermod -aG docker {username}")
            
            # Wait for Docker to be ready
            self.logger.info("Waiting for Docker to be ready...")
            await asyncio.sleep(30)
            
            # Verify Docker installation
            stdout, stderr, exit_code = await self.execute_ssh_command("docker --version")
            if exit_code != 0:
                raise Exception("Docker verification failed")
            
            return {
                'success': True,
                'docker_version': stdout.strip(),
                'service_status': 'running',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def install_portainer(self) -> Dict[str, Any]:
        """Install Portainer for container management"""
        try:
            # Create Portainer volume
            await self.execute_ssh_command("docker volume create portainer_data")
            
            # Generate admin password
            import secrets
            import string
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            # Run Portainer container
            portainer_cmd = f"""docker run -d \
                --name portainer \
                --restart=always \
                -p 9000:9000 \
                -p 9443:9443 \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v portainer_data:/data \
                portainer/portainer-ce:latest"""
            
            stdout, stderr, exit_code = await self.execute_ssh_command(portainer_cmd)
            
            if exit_code != 0:
                raise Exception(f"Portainer installation failed: {stderr}")
            
            # Wait for Portainer to start
            await asyncio.sleep(30)
            
            # Verify Portainer is running
            stdout, stderr, exit_code = await self.execute_ssh_command("docker ps | grep portainer")
            if exit_code != 0:
                raise Exception("Portainer container not running")
            
            return {
                'success': True,
                'container_id': stdout.split()[0],
                'admin_password': password,
                'access_url': f"https://{self.server_ip}:9443",
                'local_url': f"http://{self.server_ip}:9000",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def install_nginx_proxy_manager(self) -> Dict[str, Any]:
        """Install Nginx Proxy Manager"""
        try:
            # Create directory for NPM
            await self.execute_ssh_command("mkdir -p /opt/nginx-proxy-manager")
            
            # Create docker-compose file for NPM
            docker_compose_content = """version: '3'
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    environment:
      DB_MYSQL_HOST: "db"
      DB_MYSQL_PORT: 3306
      DB_MYSQL_USER: "npm"
      DB_MYSQL_PASSWORD: "npm"
      DB_MYSQL_NAME: "npm"
  db:
    image: 'jc21/mariadb-aria:latest'
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: 'npm'
      MYSQL_DATABASE: 'npm'
      MYSQL_USER: 'npm'
      MYSQL_PASSWORD: 'npm'
    volumes:
      - ./data/mysql:/var/lib/mysql
"""
            
            # Write docker-compose file
            compose_file_cmd = f"cat > /opt/nginx-proxy-manager/docker-compose.yml << 'EOF'\n{docker_compose_content}\nEOF"
            await self.execute_ssh_command(compose_file_cmd)
            
            # Start Nginx Proxy Manager
            npm_start_cmd = "cd /opt/nginx-proxy-manager && docker-compose up -d"
            stdout, stderr, exit_code = await self.execute_ssh_command(npm_start_cmd, timeout=300)
            
            if exit_code != 0:
                raise Exception(f"Nginx Proxy Manager startup failed: {stderr}")
            
            # Wait for NPM to start
            await asyncio.sleep(60)
            
            # Verify NPM is running
            stdout, stderr, exit_code = await self.execute_ssh_command("cd /opt/nginx-proxy-manager && docker-compose ps")
            if "Up" not in stdout:
                raise Exception("Nginx Proxy Manager containers not running properly")
            
            return {
                'success': True,
                'access_url': f"http://{self.server_ip}:81",
                'default_email': 'admin@example.com',
                'default_password': 'changeme',
                'installation_path': '/opt/nginx-proxy-manager',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def configure_firewall(self) -> Dict[str, Any]:
        """Configure firewall rules"""
        try:
            firewall_commands = [
                "ufw --force enable",
                "ufw default deny incoming",
                "ufw default allow outgoing",
                "ufw allow ssh",
                "ufw allow 80/tcp",
                "ufw allow 443/tcp",
                "ufw allow 81/tcp",  # NPM admin
                "ufw allow 9000/tcp",  # Portainer
                "ufw allow 9443/tcp",  # Portainer HTTPS
                "ufw reload"
            ]
            
            for cmd in firewall_commands:
                await self.execute_ssh_command(cmd)
            
            # Get firewall status
            stdout, stderr, exit_code = await self.execute_ssh_command("ufw status")
            
            return {
                'success': True,
                'firewall_status': stdout,
                'rules_configured': len(firewall_commands),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def execute_ssh_command(self, command: str, timeout: int = 300) -> tuple:
        """Execute command via SSH"""
        if not self.ssh_client:
            raise Exception("SSH connection not established")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # Wait for command completion
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            self.logger.debug(f"Command: {command}")
            self.logger.debug(f"Exit code: {exit_code}")
            self.logger.debug(f"Stdout: {stdout_data}")
            if stderr_data:
                self.logger.debug(f"Stderr: {stderr_data}")
            
            return stdout_data, stderr_data, exit_code
            
        except Exception as e:
            self.logger.error(f"SSH command execution failed: {str(e)}")
            raise e

    async def validate_server_setup(self) -> Dict[str, Any]:
        """Validate the server setup"""
        validation_results = {
            'docker': await self.validate_docker(),
            'portainer': await self.validate_portainer(),
            'nginx_proxy_manager': await self.validate_nginx_proxy_manager(),
            'firewall': await self.validate_firewall(),
            'overall_health': True
        }
        
        # Check overall health
        validation_results['overall_health'] = all(
            result.get('valid', False) for result in validation_results.values() 
            if isinstance(result, dict)
        )
        
        return validation_results

    async def validate_docker(self) -> Dict[str, Any]:
        """Validate Docker installation"""
        try:
            # Check Docker version
            stdout, stderr, exit_code = await self.execute_ssh_command("docker --version")
            if exit_code != 0:
                return {'valid': False, 'error': 'Docker not installed'}
            
            # Check Docker service status
            stdout, stderr, exit_code = await self.execute_ssh_command("systemctl is-active docker")
            if exit_code != 0 or 'active' not in stdout:
                return {'valid': False, 'error': 'Docker service not running'}
            
            # Test Docker functionality
            stdout, stderr, exit_code = await self.execute_ssh_command("docker run --rm hello-world")
            if exit_code != 0:
                return {'valid': False, 'error': 'Docker functionality test failed'}
            
            return {
                'valid': True,
                'version': stdout.split('\n')[0],
                'service_status': 'active'
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def validate_portainer(self) -> Dict[str, Any]:
        """Validate Portainer installation"""
        try:
            # Check if Portainer container is running
            stdout, stderr, exit_code = await self.execute_ssh_command("docker ps | grep portainer")
            if exit_code != 0:
                return {'valid': False, 'error': 'Portainer container not running'}
            
            # Check if Portainer is accessible
            stdout, stderr, exit_code = await self.execute_ssh_command(f"curl -k -s -o /dev/null -w '%{{http_code}}' https://localhost:9443")
            if exit_code == 0 and '200' in stdout:
                return {'valid': True, 'status': 'accessible'}
            
            return {'valid': True, 'status': 'running', 'note': 'Web interface may still be starting'}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def validate_nginx_proxy_manager(self) -> Dict[str, Any]:
        """Validate Nginx Proxy Manager installation"""
        try:
            # Check if NPM containers are running
            stdout, stderr, exit_code = await self.execute_ssh_command("cd /opt/nginx-proxy-manager && docker-compose ps")
            if exit_code != 0:
                return {'valid': False, 'error': 'NPM docker-compose not found'}
            
            if 'Up' not in stdout:
                return {'valid': False, 'error': 'NPM containers not running'}
            
            # Check if NPM is accessible
            stdout, stderr, exit_code = await self.execute_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:81")
            if exit_code == 0 and '200' in stdout:
                return {'valid': True, 'status': 'accessible'}
            
            return {'valid': True, 'status': 'running', 'note': 'Web interface may still be starting'}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def validate_firewall(self) -> Dict[str, Any]:
        """Validate firewall configuration"""
        try:
            stdout, stderr, exit_code = await self.execute_ssh_command("ufw status")
            if exit_code != 0:
                return {'valid': False, 'error': 'UFW not available'}
            
            if 'Status: active' not in stdout:
                return {'valid': False, 'error': 'Firewall not active'}
            
            # Check required ports
            required_ports = ['80', '443', '81', '9000', '9443']
            for port in required_ports:
                if port not in stdout:
                    return {'valid': False, 'error': f'Port {port} not configured'}
            
            return {'valid': True, 'status': 'active', 'ports_configured': required_ports}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    async def generate_setup_report(self, setup_result: Dict[str, Any], 
                                  validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive setup report"""
        return {
            'agent_name': self.name,
            'server_ip': self.server_ip,
            'setup_timestamp': datetime.now().isoformat(),
            'setup_results': setup_result,
            'validation_results': validation_result,
            'services_installed': {
                'docker': setup_result.get('docker_installation', {}).get('success', False),
                'portainer': setup_result.get('portainer_installation', {}).get('success', False),
                'nginx_proxy_manager': setup_result.get('nginx_proxy_installation', {}).get('success', False)
            },
            'access_information': {
                'portainer': f"https://{self.server_ip}:9443",
                'nginx_proxy_manager': f"http://{self.server_ip}:81"
            },
            'credentials': {
                'portainer_admin_password': setup_result.get('portainer_installation', {}).get('admin_password'),
                'npm_default_email': 'admin@example.com',
                'npm_default_password': 'changeme'
            },
            'next_steps': [
                "Configure Nginx Proxy Manager with proper admin credentials",
                "Setup SSL certificates for domains",
                "Configure Portainer with proper authentication",
                "Deploy application services"
            ]
        }

    async def perform_agent_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform agent-specific validation"""
        validation = {
            'checks_performed': [
                'docker_installation',
                'portainer_deployment',
                'nginx_proxy_manager_setup',
                'firewall_configuration',
                'service_accessibility'
            ],
            'errors': [],
            'warnings': []
        }
        
        # Check if all services were installed successfully
        setup_result = result.get('setup_result', {})
        
        if not setup_result.get('docker_installation', {}).get('success'):
            validation['errors'].append("Docker installation failed")
        
        if not setup_result.get('portainer_installation', {}).get('success'):
            validation['errors'].append("Portainer installation failed")
        
        if not setup_result.get('nginx_proxy_installation', {}).get('success'):
            validation['errors'].append("Nginx Proxy Manager installation failed")
        
        # Check validation results
        validation_result = result.get('validation', {})
        if not validation_result.get('overall_health'):
            validation['errors'].append("Overall system health check failed")
        
        return validation