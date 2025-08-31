# 📦 Installation Guide

Complete installation guide for the N8N Deployment Project.

## 🎯 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd n8n-deployment-project
```

### 2. Run the Deployment Script
```bash
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will handle everything automatically.

## 🔧 Detailed Installation

### Prerequisites

#### System Requirements
- **Operating System**: Ubuntu 18.04+, Debian 10+, CentOS 7+, or macOS 10.15+
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet connection for downloading dependencies

#### Required Software
- **Python 3.8+**
- **Git 2.20+**
- **Docker 20.10+**
- **Docker Compose 1.29+**

### Step-by-Step Installation

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login again to apply Docker group changes
```

**CentOS/RHEL:**
```bash
# Install Python 3 and pip
sudo yum install python3 python3-pip -y

# Install Git
sudo yum install git -y

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 git docker docker-compose
```

#### 2. Verify Installation
```bash
# Check Python
python3 --version

# Check Git
git --version

# Check Docker
docker --version
docker-compose --version

# Test Docker (should not require sudo)
docker run hello-world
```

#### 3. Clone and Setup Project
```bash
# Clone the repository
git clone <your-repository-url>
cd n8n-deployment-project

# Create Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 4. Configure the Project
```bash
# Copy and edit configuration
cp config/config.yaml config/config.local.yaml
nano config/config.local.yaml  # Edit as needed

# Set up Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 5. Run Installation
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run full deployment
./deploy.sh --config config/config.local.yaml

# Or run specific components
./deploy.sh --setup-n8n  # Only setup N8N
./deploy.sh --git-only   # Only Git operations
```

## 🐳 Docker-Only Installation

If you prefer to run everything in Docker:

### 1. Create Docker Compose File
```yaml
version: '3.8'
services:
  n8n-deployer:
    build: .
    volumes:
      - .:/app
      - /var/run/docker.sock:/var/run/docker.sock
    working_dir: /app
    command: python3 scripts/script.py
```

### 2. Create Dockerfile
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "scripts/script.py"]
```

### 3. Run with Docker
```bash
docker-compose up --build
```

## 🔧 Configuration Options

### Basic Configuration
Edit `config/config.yaml`:

```yaml
# Project settings
project:
  name: "my-n8n-deployment"
  version: "1.0.0"

# N8N settings
n8n:
  port: 5678
  webhook_url: "http://localhost:5678"
  timezone: "America/New_York"

# Git settings
git:
  user:
    name: "Your Name"
    email: "your.email@example.com"
  remote:
    url: "https://github.com/yourusername/your-repo.git"
```

### Advanced Configuration

#### SSL/TLS Setup
```yaml
n8n:
  ssl_enabled: true
  ssl:
    generate_self_signed: true
    key_path: "/certs/key.pem"
    cert_path: "/certs/cert.pem"
```

#### Database Configuration
```yaml
n8n:
  database_type: "postgres"
  postgres:
    host: "localhost"
    port: 5432
    database: "n8n"
    user: "n8n_user"
    password: "secure_password"
```

#### Monitoring Setup
```yaml
monitoring:
  health_check:
    enabled: true
    interval: 30
  alerts:
    enabled: true
    webhook_url: "https://hooks.slack.com/your-webhook"
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Permission Denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

#### Python Module Not Found
```bash
# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Check what's using port 5678
sudo lsof -i :5678
# Kill the process or change port in config
```

#### Git Authentication Issues
```bash
# Setup SSH key
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
# Add to GitHub/GitLab

# Or use personal access token
git remote set-url origin https://username:token@github.com/user/repo.git
```

### Log Files
Check these files for detailed error information:
- `logs/deployment.log` - Main deployment log
- `logs/n8n.log` - N8N application log
- `docker-compose logs` - Docker container logs

### Getting Help
1. Check the [troubleshooting guide](troubleshooting.md)
2. Review log files for error messages
3. Run with verbose output: `./deploy.sh --verbose`
4. Use dry run to test: `./deploy.sh --dry-run`

## 🔄 Updating

### Update the Project
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Redeploy
./deploy.sh --force
```

### Update N8N
```bash
# Pull latest N8N image
docker-compose pull n8n

# Restart with new image
docker-compose up -d n8n
```

## 🗑️ Uninstallation

### Remove N8N Services
```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi docker.n8n.io/n8nio/n8n

# Remove volumes (WARNING: This deletes all data!)
docker volume rm n8n_data
```

### Remove Project Files
```bash
# Remove project directory
rm -rf n8n-deployment-project

# Remove Docker images and volumes
docker system prune -a --volumes
```

## 📚 Next Steps

After successful installation:

1. **Access N8N**: Open http://localhost:5678 in your browser
2. **Read the [Deployment Guide](deployment.md)** for advanced configuration
3. **Check the [Troubleshooting Guide](troubleshooting.md)** for common issues
4. **Explore N8N Documentation**: https://docs.n8n.io/

## 🤝 Support

If you encounter issues:
- Check the troubleshooting guide
- Review log files
- Open an issue in the repository
- Join the N8N community forum