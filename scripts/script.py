#!/usr/bin/env python3
"""
N8N Deployment Project - Main Script
====================================

This script orchestrates the entire deployment process including:
- Reading and processing project files
- Git repository management
- N8N deployment automation
- Configuration management

Author: N8N Deployment Team
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import our custom modules
from file_reader import FileReader
from git_deployer import GitDeployer
from setup_n8n import N8NSetup

class DeploymentOrchestrator:
    """Main orchestrator for the deployment process"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the deployment orchestrator"""
        self.config_path = config_path
        self.config = self._load_config()
        self.setup_logging()
        
        # Initialize components
        self.file_reader = FileReader(self.config)
        self.git_deployer = GitDeployer(self.config)
        self.n8n_setup = N8NSetup(self.config)
        
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'project': {
                'name': 'n8n-deployment',
                'version': '1.0.0',
                'description': 'Automated N8N deployment project'
            },
            'git': {
                'auto_commit': True,
                'commit_message_template': 'Auto-deploy: {timestamp}',
                'branch': 'main'
            },
            'n8n': {
                'port': 5678,
                'webhook_url': 'http://localhost:5678',
                'timezone': 'UTC'
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/deployment.log'
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'deployment.log')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def read_project_files(self) -> Dict:
        """Read and process all project files"""
        self.logger.info("Starting file reading process...")
        
        files_to_read = [
            'README.md',
            'prd-document.md',
            'scripts/script.py',
            'scripts/file_reader.py',
            'scripts/git_deployer.py',
            'scripts/setup_n8n.py'
        ]
        
        file_contents = {}
        
        for file_path in files_to_read:
            try:
                content = self.file_reader.read_file(file_path)
                if content:
                    file_contents[file_path] = content
                    self.logger.info(f"Successfully read: {file_path}")
                else:
                    self.logger.warning(f"Empty or missing file: {file_path}")
            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")
        
        return file_contents
    
    def analyze_project_structure(self) -> Dict:
        """Analyze the project structure and generate metadata"""
        self.logger.info("Analyzing project structure...")
        
        structure = {
            'directories': [],
            'files': [],
            'total_files': 0,
            'total_size': 0,
            'last_modified': None
        }
        
        project_root = Path('.')
        
        for item in project_root.rglob('*'):
            if item.is_file():
                structure['files'].append(str(item))
                structure['total_files'] += 1
                structure['total_size'] += item.stat().st_size
                
                # Update last modified time
                mod_time = datetime.fromtimestamp(item.stat().st_mtime)
                if not structure['last_modified'] or mod_time > structure['last_modified']:
                    structure['last_modified'] = mod_time
            elif item.is_dir():
                structure['directories'].append(str(item))
        
        return structure
    
    def prepare_git_deployment(self, file_contents: Dict) -> bool:
        """Prepare files for Git deployment"""
        self.logger.info("Preparing Git deployment...")
        
        try:
            # Initialize Git repository if needed
            if not self.git_deployer.is_git_repo():
                self.git_deployer.init_repository()
            
            # Add all files to Git
            self.git_deployer.add_files(['.'])
            
            # Generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = self.config['git']['commit_message_template'].format(
                timestamp=timestamp
            )
            
            # Commit changes
            self.git_deployer.commit_changes(commit_message)
            
            self.logger.info("Git deployment prepared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing Git deployment: {e}")
            return False
    
    def deploy_to_git(self, remote_url: Optional[str] = None) -> bool:
        """Deploy project to Git repository"""
        self.logger.info("Deploying to Git repository...")
        
        try:
            if remote_url:
                self.git_deployer.add_remote('origin', remote_url)
            
            # Push to remote repository
            branch = self.config['git']['branch']
            success = self.git_deployer.push_to_remote('origin', branch)
            
            if success:
                self.logger.info("Successfully deployed to Git repository")
            else:
                self.logger.error("Failed to deploy to Git repository")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deploying to Git: {e}")
            return False
    
    def setup_n8n_environment(self) -> bool:
        """Setup N8N environment"""
        self.logger.info("Setting up N8N environment...")
        
        try:
            # Create N8N configuration
            n8n_config = self.n8n_setup.generate_config()
            
            # Deploy N8N using Docker
            success = self.n8n_setup.deploy_with_docker()
            
            if success:
                self.logger.info("N8N environment setup completed")
            else:
                self.logger.error("Failed to setup N8N environment")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error setting up N8N: {e}")
            return False
    
    def generate_deployment_report(self, file_contents: Dict, structure: Dict) -> str:
        """Generate a deployment report"""
        report = f"""
# Deployment Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Project Information
- Name: {self.config['project']['name']}
- Version: {self.config['project']['version']}
- Description: {self.config['project']['description']}

## Files Processed
Total files read: {len(file_contents)}

### File List:
"""
        
        for file_path in file_contents.keys():
            report += f"- {file_path}\n"
        
        report += f"""
## Project Structure
- Total directories: {len(structure['directories'])}
- Total files: {structure['total_files']}
- Total size: {structure['total_size']} bytes
- Last modified: {structure['last_modified']}

## Configuration
```yaml
{yaml.dump(self.config, default_flow_style=False)}
```

## Status
✅ File reading completed
✅ Project analysis completed
✅ Git preparation completed
✅ Deployment report generated
"""
        
        return report
    
    def run_full_deployment(self, git_remote_url: Optional[str] = None) -> bool:
        """Run the complete deployment process"""
        self.logger.info("Starting full deployment process...")
        
        try:
            # Step 1: Read project files
            file_contents = self.read_project_files()
            
            # Step 2: Analyze project structure
            structure = self.analyze_project_structure()
            
            # Step 3: Prepare Git deployment
            git_prepared = self.prepare_git_deployment(file_contents)
            
            # Step 4: Deploy to Git (if remote URL provided)
            if git_remote_url and git_prepared:
                git_deployed = self.deploy_to_git(git_remote_url)
            else:
                git_deployed = git_prepared
            
            # Step 5: Setup N8N environment
            n8n_deployed = self.setup_n8n_environment()
            
            # Step 6: Generate deployment report
            report = self.generate_deployment_report(file_contents, structure)
            
            # Save report
            with open('deployment_report.md', 'w') as f:
                f.write(report)
            
            # Final status
            success = git_deployed and n8n_deployed
            
            if success:
                self.logger.info("🎉 Full deployment completed successfully!")
                print("\n" + "="*50)
                print("🎉 DEPLOYMENT SUCCESSFUL!")
                print("="*50)
                print(f"📁 Project files processed: {len(file_contents)}")
                print(f"📊 Deployment report: deployment_report.md")
                print(f"🌐 N8N URL: http://localhost:{self.config['n8n']['port']}")
                print("="*50)
            else:
                self.logger.error("❌ Deployment failed")
                print("\n" + "="*50)
                print("❌ DEPLOYMENT FAILED!")
                print("="*50)
                print("Check the logs for more details.")
                print("="*50)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Critical error during deployment: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='N8N Deployment Project')
    parser.add_argument('--config', default='config/config.yaml', 
                       help='Configuration file path')
    parser.add_argument('--git-remote', 
                       help='Git remote repository URL')
    parser.add_argument('--read-only', action='store_true',
                       help='Only read files, do not deploy')
    parser.add_argument('--setup-n8n', action='store_true',
                       help='Only setup N8N environment')
    parser.add_argument('--git-only', action='store_true',
                       help='Only perform Git operations')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DeploymentOrchestrator(args.config)
    
    try:
        if args.read_only:
            # Only read and analyze files
            file_contents = orchestrator.read_project_files()
            structure = orchestrator.analyze_project_structure()
            report = orchestrator.generate_deployment_report(file_contents, structure)
            print(report)
            
        elif args.setup_n8n:
            # Only setup N8N
            success = orchestrator.setup_n8n_environment()
            sys.exit(0 if success else 1)
            
        elif args.git_only:
            # Only Git operations
            file_contents = orchestrator.read_project_files()
            git_success = orchestrator.prepare_git_deployment(file_contents)
            if args.git_remote:
                git_success = orchestrator.deploy_to_git(args.git_remote)
            sys.exit(0 if git_success else 1)
            
        else:
            # Full deployment
            success = orchestrator.run_full_deployment(args.git_remote)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()