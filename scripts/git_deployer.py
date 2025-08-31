#!/usr/bin/env python3
"""
Git Deployer Module
===================

Handles all Git operations including:
- Repository initialization
- File staging and commits
- Remote repository management
- Branch operations
- Push/pull operations

Features:
- Automated commit messages
- Error handling and recovery
- Multiple remote support
- Branch management
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class GitDeployer:
    """Git repository management and deployment utility"""
    
    def __init__(self, config: Dict):
        """Initialize Git deployer with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.git_config = config.get('git', {})
        
    def run_git_command(self, command: List[str], cwd: str = '.') -> Tuple[bool, str, str]:
        """Run a git command and return success status, stdout, stderr"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            if success:
                self.logger.debug(f"Git command succeeded: git {' '.join(command)}")
            else:
                self.logger.error(f"Git command failed: git {' '.join(command)}")
                self.logger.error(f"Error: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Git command timed out: git {' '.join(command)}")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return False, "", str(e)
    
    def is_git_repo(self, path: str = '.') -> bool:
        """Check if directory is a Git repository"""
        git_dir = Path(path) / '.git'
        return git_dir.exists()
    
    def init_repository(self, path: str = '.') -> bool:
        """Initialize a new Git repository"""
        self.logger.info(f"Initializing Git repository in {path}")
        
        success, stdout, stderr = self.run_git_command(['init'], cwd=path)
        
        if success:
            self.logger.info("Git repository initialized successfully")
            
            # Set initial configuration
            self.configure_git_user()
            
            # Create initial .gitignore if it doesn't exist
            self.create_gitignore()
            
        return success
    
    def configure_git_user(self) -> bool:
        """Configure Git user information"""
        git_user = self.git_config.get('user', {})
        name = git_user.get('name', 'N8N Deployer')
        email = git_user.get('email', 'deployer@n8n-project.local')
        
        # Set user name
        success1, _, _ = self.run_git_command(['config', 'user.name', name])
        
        # Set user email
        success2, _, _ = self.run_git_command(['config', 'user.email', email])
        
        if success1 and success2:
            self.logger.info(f"Git user configured: {name} <{email}>")
        
        return success1 and success2
    
    def create_gitignore(self, path: str = '.') -> bool:
        """Create a comprehensive .gitignore file"""
        gitignore_content = """# N8N Deployment Project .gitignore

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test
.env.local
.env.production

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# next.js build output
.next

# nuxt.js build output
.nuxt

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# N8N specific
n8n_data/
.n8n/
n8n-backup-*.tar.gz

# Docker
docker-compose.override.yml

# Temporary files
tmp/
temp/
*.tmp

# Secrets and credentials
secrets/
credentials/
*.key
*.pem
*.p12
*.pfx

# Backup files
*.backup
*.bak
"""
        
        gitignore_path = Path(path) / '.gitignore'
        
        try:
            if not gitignore_path.exists():
                with open(gitignore_path, 'w') as f:
                    f.write(gitignore_content)
                self.logger.info("Created .gitignore file")
                return True
            else:
                self.logger.info(".gitignore already exists")
                return True
        except Exception as e:
            self.logger.error(f"Error creating .gitignore: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get Git repository status"""
        success, stdout, stderr = self.run_git_command(['status', '--porcelain'])
        
        if not success:
            return {'error': stderr}
        
        status = {
            'clean': len(stdout) == 0,
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }
        
        for line in stdout.splitlines():
            if len(line) >= 3:
                status_code = line[:2]
                filename = line[3:]
                
                if status_code == '??':
                    status['untracked'].append(filename)
                elif 'M' in status_code:
                    status['modified'].append(filename)
                elif 'A' in status_code:
                    status['added'].append(filename)
                elif 'D' in status_code:
                    status['deleted'].append(filename)
        
        return status
    
    def add_files(self, files: List[str]) -> bool:
        """Add files to Git staging area"""
        self.logger.info(f"Adding files to Git: {files}")
        
        success, stdout, stderr = self.run_git_command(['add'] + files)
        
        if success:
            self.logger.info("Files added to staging area successfully")
        
        return success
    
    def commit_changes(self, message: str, allow_empty: bool = False) -> bool:
        """Commit staged changes"""
        self.logger.info(f"Committing changes: {message}")
        
        command = ['commit', '-m', message]
        if allow_empty:
            command.append('--allow-empty')
        
        success, stdout, stderr = self.run_git_command(command)
        
        if success:
            self.logger.info("Changes committed successfully")
        elif "nothing to commit" in stderr:
            self.logger.info("No changes to commit")
            return True
        
        return success
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch"""
        self.logger.info(f"Creating branch: {branch_name}")
        
        # Create branch
        success, stdout, stderr = self.run_git_command(['branch', branch_name])
        
        if success and checkout:
            # Checkout the new branch
            success, stdout, stderr = self.run_git_command(['checkout', branch_name])
        
        return success
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout an existing branch"""
        self.logger.info(f"Checking out branch: {branch_name}")
        
        success, stdout, stderr = self.run_git_command(['checkout', branch_name])
        
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name"""
        success, stdout, stderr = self.run_git_command(['branch', '--show-current'])
        
        if success:
            return stdout.strip()
        
        return None
    
    def list_branches(self) -> List[str]:
        """List all branches"""
        success, stdout, stderr = self.run_git_command(['branch'])
        
        if success:
            branches = []
            for line in stdout.splitlines():
                branch = line.strip().lstrip('* ')
                if branch:
                    branches.append(branch)
            return branches
        
        return []
    
    def add_remote(self, name: str, url: str) -> bool:
        """Add a remote repository"""
        self.logger.info(f"Adding remote {name}: {url}")
        
        # Check if remote already exists
        success, stdout, stderr = self.run_git_command(['remote', 'get-url', name])
        
        if success:
            # Remote exists, update URL
            success, stdout, stderr = self.run_git_command(['remote', 'set-url', name, url])
        else:
            # Add new remote
            success, stdout, stderr = self.run_git_command(['remote', 'add', name, url])
        
        return success
    
    def list_remotes(self) -> Dict[str, str]:
        """List all remotes"""
        success, stdout, stderr = self.run_git_command(['remote', '-v'])
        
        remotes = {}
        if success:
            for line in stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    if '(fetch)' in line:
                        remotes[name] = url
        
        return remotes
    
    def push_to_remote(self, remote: str = 'origin', branch: str = None) -> bool:
        """Push changes to remote repository"""
        if not branch:
            branch = self.get_current_branch() or 'main'
        
        self.logger.info(f"Pushing to {remote}/{branch}")
        
        # First, try to push
        success, stdout, stderr = self.run_git_command(['push', remote, branch])
        
        if not success and 'upstream' in stderr:
            # Set upstream and push
            success, stdout, stderr = self.run_git_command([
                'push', '--set-upstream', remote, branch
            ])
        
        if success:
            self.logger.info(f"Successfully pushed to {remote}/{branch}")
        
        return success
    
    def pull_from_remote(self, remote: str = 'origin', branch: str = None) -> bool:
        """Pull changes from remote repository"""
        if not branch:
            branch = self.get_current_branch() or 'main'
        
        self.logger.info(f"Pulling from {remote}/{branch}")
        
        success, stdout, stderr = self.run_git_command(['pull', remote, branch])
        
        return success
    
    def get_commit_history(self, limit: int = 10) -> List[Dict]:
        """Get commit history"""
        command = ['log', f'--max-count={limit}', '--pretty=format:%H|%an|%ae|%ad|%s']
        success, stdout, stderr = self.run_git_command(command)
        
        commits = []
        if success:
            for line in stdout.splitlines():
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        'hash': parts[0],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
        
        return commits
    
    def create_tag(self, tag_name: str, message: str = None) -> bool:
        """Create a Git tag"""
        self.logger.info(f"Creating tag: {tag_name}")
        
        command = ['tag']
        if message:
            command.extend(['-a', tag_name, '-m', message])
        else:
            command.append(tag_name)
        
        success, stdout, stderr = self.run_git_command(command)
        
        return success
    
    def generate_commit_message(self, file_changes: Dict = None) -> str:
        """Generate an automated commit message"""
        template = self.git_config.get('commit_message_template', 
                                      'Auto-deploy: {timestamp}')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Basic template substitution
        message = template.format(
            timestamp=timestamp,
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S")
        )
        
        # Add file change information if available
        if file_changes:
            status = self.get_status()
            if not status.get('clean', True):
                changes = []
                if status.get('modified'):
                    changes.append(f"Modified: {len(status['modified'])} files")
                if status.get('added'):
                    changes.append(f"Added: {len(status['added'])} files")
                if status.get('deleted'):
                    changes.append(f"Deleted: {len(status['deleted'])} files")
                
                if changes:
                    message += f" ({', '.join(changes)})"
        
        return message
    
    def auto_deploy(self, remote_url: str = None, branch: str = None) -> bool:
        """Perform automated deployment to Git"""
        self.logger.info("Starting automated Git deployment...")
        
        try:
            # Initialize repo if needed
            if not self.is_git_repo():
                if not self.init_repository():
                    return False
            
            # Add all files
            if not self.add_files(['.']):
                return False
            
            # Generate commit message
            commit_message = self.generate_commit_message()
            
            # Commit changes
            if not self.commit_changes(commit_message):
                return False
            
            # Add remote if provided
            if remote_url:
                if not self.add_remote('origin', remote_url):
                    self.logger.warning("Could not add remote, continuing...")
            
            # Push to remote if we have one
            remotes = self.list_remotes()
            if remotes:
                remote_name = 'origin' if 'origin' in remotes else list(remotes.keys())[0]
                if not self.push_to_remote(remote_name, branch):
                    self.logger.warning("Could not push to remote")
                    return False
            
            self.logger.info("Automated Git deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during automated deployment: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Test the Git deployer
    config = {
        'git': {
            'user': {
                'name': 'Test User',
                'email': 'test@example.com'
            },
            'commit_message_template': 'Test commit: {timestamp}'
        }
    }
    
    deployer = GitDeployer(config)
    
    # Test basic operations
    print(f"Is Git repo: {deployer.is_git_repo()}")
    print(f"Current branch: {deployer.get_current_branch()}")
    print(f"Status: {deployer.get_status()}")
    print(f"Remotes: {deployer.list_remotes()}")