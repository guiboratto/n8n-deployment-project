#!/usr/bin/env python3
"""
N8N Setup Module
================

Handles N8N installation and configuration including:
- Docker-based deployment
- Configuration file generation
- SSL/TLS setup
- Database configuration
- Backup and restore operations

Features:
- Multiple deployment methods
- Environment configuration
- Health checks
- Monitoring setup
"""

import os
import sys
import subprocess
import logging
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class N8NSetup:
    """N8N installation and configuration utility"""
    
    def __init__(self, config: Dict):
        """Initialize N8N setup with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.n8n_config = config.get('n8n', {})
        
        # Default N8N configuration
        self.default_config = {
            'port': 5678,
            'webhook_url': 'http://localhost:5678',
            'timezone': 'UTC',
            'protocol': 'http',
            'host': '0.0.0.0',
            'secure_cookie': False,
            'database_type': 'sqlite'
        }
        
        # Merge with user config
        self.n8n_config = {**self.default_config, **self.n8n_config}
    
    def run_command(self, command: List[str], cwd: str = '.', timeout: int = 60) -> Tuple[bool, str, str]:
        """Run a system command"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            if success:
                self.logger.debug(f"Command succeeded: {' '.join(command)}")
            else:
                self.logger.error(f"Command failed: {' '.join(command)}")
                self.logger.error(f"Error: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(command)}")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Error running command: {e}")
            return False, "", str(e)
    
    def check_docker_installed(self) -> bool:
        """Check if Docker is installed and running"""
        self.logger.info("Checking Docker installation...")
        
        # Check if docker command exists
        success, stdout, stderr = self.run_command(['which', 'docker'])
        if not success:
            self.logger.error("Docker is not installed")
            return False
        
        # Check if Docker daemon is running
        success, stdout, stderr = self.run_command(['docker', 'info'])
        if not success:
            self.logger.error("Docker daemon is not running")
            return False
        
        self.logger.info("Docker is installed and running")
        return True
    
    def check_docker_compose_installed(self) -> bool:
        """Check if Docker Compose is installed"""
        self.logger.info("Checking Docker Compose installation...")
        
        # Try docker-compose command
        success, stdout, stderr = self.run_command(['docker-compose', '--version'])
        if success:
            self.logger.info("Docker Compose is installed")
            return True
        
        # Try docker compose command (newer version)
        success, stdout, stderr = self.run_command(['docker', 'compose', 'version'])
        if success:
            self.logger.info("Docker Compose (plugin) is installed")
            return True
        
        self.logger.error("Docker Compose is not installed")
        return False
    
    def generate_docker_compose(self) -> str:
        """Generate Docker Compose configuration for N8N"""
        self.logger.info("Generating Docker Compose configuration...")
        
        # Base configuration
        compose_config = {
            'version': '3.8',
            'services': {
                'n8n': {
                    'image': 'docker.n8n.io/n8nio/n8n',
                    'container_name': 'n8n',
                    'restart': 'unless-stopped',
                    'ports': [f"{self.n8n_config['port']}:5678"],
                    'environment': [
                        f"GENERIC_TIMEZONE={self.n8n_config['timezone']}",
                        f"TZ={self.n8n_config['timezone']}",
                        f"WEBHOOK_URL={self.n8n_config['webhook_url']}",
                        f"N8N_HOST={self.n8n_config['host']}",
                        f"N8N_PORT=5678",
                        f"N8N_PROTOCOL={self.n8n_config['protocol']}",
                        f"N8N_SECURE_COOKIE={str(self.n8n_config['secure_cookie']).lower()}"
                    ],
                    'volumes': [
                        'n8n_data:/home/node/.n8n',
                        './local-files:/files'
                    ]
                }
            },
            'volumes': {
                'n8n_data': None
            }
        }
        
        # Add database configuration if specified
        if self.n8n_config.get('database_type') == 'postgres':
            self._add_postgres_config(compose_config)
        elif self.n8n_config.get('database_type') == 'mysql':
            self._add_mysql_config(compose_config)
        
        # Add SSL configuration if specified
        if self.n8n_config.get('ssl_enabled'):
            self._add_ssl_config(compose_config)
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def _add_postgres_config(self, compose_config: Dict):
        """Add PostgreSQL configuration to Docker Compose"""
        postgres_config = self.n8n_config.get('postgres', {})
        
        # Add PostgreSQL service
        compose_config['services']['postgres'] = {
            'image': 'postgres:13',
            'container_name': 'n8n_postgres',
            'restart': 'unless-stopped',
            'environment': [
                f"POSTGRES_DB={postgres_config.get('database', 'n8n')}",
                f"POSTGRES_USER={postgres_config.get('user', 'n8n')}",
                f"POSTGRES_PASSWORD={postgres_config.get('password', 'n8n_password')}"
            ],
            'volumes': [
                'postgres_data:/var/lib/postgresql/data'
            ]
        }
        
        # Update N8N service to use PostgreSQL
        compose_config['services']['n8n']['depends_on'] = ['postgres']
        compose_config['services']['n8n']['environment'].extend([
            'DB_TYPE=postgresdb',
            'DB_POSTGRESDB_HOST=postgres',
            f"DB_POSTGRESDB_DATABASE={postgres_config.get('database', 'n8n')}",
            f"DB_POSTGRESDB_USER={postgres_config.get('user', 'n8n')}",
            f"DB_POSTGRESDB_PASSWORD={postgres_config.get('password', 'n8n_password')}"
        ])
        
        # Add PostgreSQL volume
        compose_config['volumes']['postgres_data'] = None
    
    def _add_mysql_config(self, compose_config: Dict):
        """Add MySQL configuration to Docker Compose"""
        mysql_config = self.n8n_config.get('mysql', {})
        
        # Add MySQL service
        compose_config['services']['mysql'] = {
            'image': 'mysql:8.0',
            'container_name': 'n8n_mysql',
            'restart': 'unless-stopped',
            'environment': [
                f"MYSQL_DATABASE={mysql_config.get('database', 'n8n')}",
                f"MYSQL_USER={mysql_config.get('user', 'n8n')}",
                f"MYSQL_PASSWORD={mysql_config.get('password', 'n8n_password')}",
                f"MYSQL_ROOT_PASSWORD={mysql_config.get('root_password', 'root_password')}"
            ],
            'volumes': [
                'mysql_data:/var/lib/mysql'
            ]
        }
        
        # Update N8N service to use MySQL
        compose_config['services']['n8n']['depends_on'] = ['mysql']
        compose_config['services']['n8n']['environment'].extend([
            'DB_TYPE=mysqldb',
            'DB_MYSQLDB_HOST=mysql',
            f"DB_MYSQLDB_DATABASE={mysql_config.get('database', 'n8n')}",
            f"DB_MYSQLDB_USER={mysql_config.get('user', 'n8n')}",
            f"DB_MYSQLDB_PASSWORD={mysql_config.get('password', 'n8n_password')}"
        ])
        
        # Add MySQL volume
        compose_config['volumes']['mysql_data'] = None
    
    def _add_ssl_config(self, compose_config: Dict):
        """Add SSL configuration to Docker Compose"""
        ssl_config = self.n8n_config.get('ssl', {})
        
        # Update N8N environment for SSL
        compose_config['services']['n8n']['environment'].extend([
            'N8N_PROTOCOL=https',
            f"N8N_SSL_KEY={ssl_config.get('key_path', '/certs/key.pem')}",
            f"N8N_SSL_CERT={ssl_config.get('cert_path', '/certs/cert.pem')}"
        ])
        
        # Add SSL certificate volume
        compose_config['services']['n8n']['volumes'].append('./certs:/certs')
    
    def create_directories(self):
        """Create necessary directories for N8N"""
        directories = [
            'n8n-data',
            'local-files',
            'logs',
            'backups'
        ]
        
        if self.n8n_config.get('ssl_enabled'):
            directories.append('certs')
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
    
    def generate_ssl_certificates(self) -> bool:
        """Generate self-signed SSL certificates"""
        if not self.n8n_config.get('ssl_enabled'):
            return True
        
        self.logger.info("Generating SSL certificates...")
        
        cert_dir = Path('certs')
        cert_dir.mkdir(exist_ok=True)
        
        # Generate private key and certificate
        command = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', 'certs/key.pem',
            '-out', 'certs/cert.pem',
            '-days', '365',
            '-nodes',
            '-subj', '/C=US/ST=State/L=City/O=Organization/CN=localhost'
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success:
            self.logger.info("SSL certificates generated successfully")
        else:
            self.logger.error("Failed to generate SSL certificates")
        
        return success
    
    def write_docker_compose_file(self) -> bool:
        """Write Docker Compose file to disk"""
        try:
            compose_content = self.generate_docker_compose()
            
            with open('docker-compose.yml', 'w') as f:
                f.write(compose_content)
            
            self.logger.info("Docker Compose file created: docker-compose.yml")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing Docker Compose file: {e}")
            return False
    
    def deploy_with_docker(self) -> bool:
        """Deploy N8N using Docker Compose"""
        self.logger.info("Deploying N8N with Docker...")
        
        # Check prerequisites
        if not self.check_docker_installed():
            return False
        
        if not self.check_docker_compose_installed():
            return False
        
        # Create necessary directories
        self.create_directories()
        
        # Generate SSL certificates if needed
        if self.n8n_config.get('ssl_enabled'):
            if not self.generate_ssl_certificates():
                return False
        
        # Write Docker Compose file
        if not self.write_docker_compose_file():
            return False
        
        # Start services
        self.logger.info("Starting N8N services...")
        success, stdout, stderr = self.run_command(['docker-compose', 'up', '-d'], timeout=120)
        
        if not success:
            # Try with docker compose (newer syntax)
            success, stdout, stderr = self.run_command(['docker', 'compose', 'up', '-d'], timeout=120)
        
        if success:
            self.logger.info("N8N services started successfully")
            
            # Wait for N8N to be ready
            if self.wait_for_n8n_ready():
                self.logger.info("N8N is ready and accessible")
                return True
            else:
                self.logger.warning("N8N started but may not be fully ready")
                return True
        else:
            self.logger.error("Failed to start N8N services")
            return False
    
    def wait_for_n8n_ready(self, timeout: int = 60) -> bool:
        """Wait for N8N to be ready"""
        import requests
        
        url = f"{self.n8n_config['protocol']}://localhost:{self.n8n_config['port']}"
        
        self.logger.info(f"Waiting for N8N to be ready at {url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            time.sleep(2)
        
        return False
    
    def stop_n8n(self) -> bool:
        """Stop N8N services"""
        self.logger.info("Stopping N8N services...")
        
        success, stdout, stderr = self.run_command(['docker-compose', 'down'])
        
        if not success:
            # Try with docker compose (newer syntax)
            success, stdout, stderr = self.run_command(['docker', 'compose', 'down'])
        
        return success
    
    def restart_n8n(self) -> bool:
        """Restart N8N services"""
        self.logger.info("Restarting N8N services...")
        
        if self.stop_n8n():
            return self.deploy_with_docker()
        
        return False
    
    def get_n8n_status(self) -> Dict:
        """Get N8N service status"""
        success, stdout, stderr = self.run_command(['docker-compose', 'ps'])
        
        if not success:
            # Try with docker compose (newer syntax)
            success, stdout, stderr = self.run_command(['docker', 'compose', 'ps'])
        
        status = {
            'running': False,
            'containers': [],
            'error': None
        }
        
        if success:
            lines = stdout.splitlines()
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        container_name = parts[0]
                        state = parts[3] if len(parts) > 3 else 'unknown'
                        status['containers'].append({
                            'name': container_name,
                            'state': state
                        })
                        
                        if 'n8n' in container_name and 'Up' in state:
                            status['running'] = True
        else:
            status['error'] = stderr
        
        return status
    
    def backup_n8n_data(self) -> bool:
        """Create backup of N8N data"""
        self.logger.info("Creating N8N data backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"n8n-backup-{timestamp}.tar.gz"
        
        # Create backup using docker
        command = [
            'docker', 'run', '--rm',
            '-v', 'n8n_data:/data',
            '-v', f"{os.getcwd()}/backups:/backup",
            'alpine',
            'tar', 'czf', f'/backup/{backup_filename}', '/data'
        ]
        
        success, stdout, stderr = self.run_command(command, timeout=300)
        
        if success:
            self.logger.info(f"Backup created: backups/{backup_filename}")
        else:
            self.logger.error("Failed to create backup")
        
        return success
    
    def restore_n8n_data(self, backup_filename: str) -> bool:
        """Restore N8N data from backup"""
        self.logger.info(f"Restoring N8N data from {backup_filename}...")
        
        backup_path = f"backups/{backup_filename}"
        if not os.path.exists(backup_path):
            self.logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Stop N8N first
        self.stop_n8n()
        
        # Restore data using docker
        command = [
            'docker', 'run', '--rm',
            '-v', 'n8n_data:/data',
            '-v', f"{os.getcwd()}/backups:/backup",
            'alpine',
            'tar', 'xzf', f'/backup/{backup_filename}', '-C', '/'
        ]
        
        success, stdout, stderr = self.run_command(command, timeout=300)
        
        if success:
            self.logger.info("Data restored successfully")
            # Restart N8N
            return self.deploy_with_docker()
        else:
            self.logger.error("Failed to restore data")
            return False
    
    def generate_config(self) -> Dict:
        """Generate complete N8N configuration"""
        return {
            'n8n': self.n8n_config,
            'docker_compose': self.generate_docker_compose(),
            'directories': [
                'n8n-data',
                'local-files',
                'logs',
                'backups',
                'certs' if self.n8n_config.get('ssl_enabled') else None
            ],
            'urls': {
                'web_interface': f"{self.n8n_config['protocol']}://localhost:{self.n8n_config['port']}",
                'webhook_base': self.n8n_config['webhook_url']
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the N8N setup
    config = {
        'n8n': {
            'port': 5678,
            'webhook_url': 'http://localhost:5678',
            'timezone': 'UTC',
            'ssl_enabled': False,
            'database_type': 'sqlite'
        }
    }
    
    setup = N8NSetup(config)
    
    # Test configuration generation
    print("Generated configuration:")
    print(yaml.dump(setup.generate_config(), default_flow_style=False))
    
    # Test Docker checks
    print(f"Docker installed: {setup.check_docker_installed()}")
    print(f"Docker Compose installed: {setup.check_docker_compose_installed()}")
    
    # Test status
    print(f"N8N status: {setup.get_n8n_status()}")