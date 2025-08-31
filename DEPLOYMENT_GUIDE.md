# 🚀 Quick Deployment Guide for Linux PC

This guide will help you quickly deploy this N8N project on your Linux PC.

## 📋 Prerequisites

Make sure you have these installed on your Linux PC:
- **Git** (for cloning the repository)
- **Python 3.8+** (for running the deployment scripts)
- **Docker & Docker Compose** (for N8N deployment)

## 🔧 Quick Installation Commands

### 1. Install Prerequisites (Ubuntu/Debian)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Git and Python
sudo apt install git python3 python3-pip python3-venv -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login again to apply Docker group changes
```

### 2. Clone and Deploy
```bash
# Clone this repository
git clone <YOUR_REPOSITORY_URL>
cd n8n-deployment-project

# Make deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

## 🎯 What This Will Do

1. **📖 Read all project files** (script.py, README.md, PRD files)
2. **🔍 Analyze project structure** and generate metadata
3. **🐳 Deploy N8N** using Docker with optimized configuration
4. **🌐 Set up web interface** at http://localhost:5678
5. **📊 Generate deployment report** with all details
6. **💾 Create backup capabilities** for your workflows

## 🔧 Configuration Options

### Basic Deployment
```bash
# Default deployment (recommended for first time)
./deploy.sh
```

### Advanced Deployment Options
```bash
# Deploy with PostgreSQL database
./deploy.sh --database postgres

# Deploy with SSL enabled
./deploy.sh --ssl

# Deploy with custom configuration
./deploy.sh --config config/custom.yaml

# Only setup N8N (skip file processing)
./deploy.sh --setup-n8n

# Verbose output for troubleshooting
./deploy.sh --verbose
```

## 🌐 Accessing N8N

After successful deployment:
- **Web Interface**: http://localhost:5678
- **Webhook Base URL**: http://localhost:5678/webhook
- **API Endpoint**: http://localhost:5678/api

## 📁 Project Structure

```
n8n-deployment-project/
├── 📄 README.md              # Main documentation
├── 🚀 deploy.sh              # One-command deployment
├── 📋 prd-document.md        # Product requirements
├── 📦 requirements.txt       # Python dependencies
├── 📁 scripts/               # Automation scripts
│   ├── script.py            # Main orchestrator
│   ├── file_reader.py       # File processing
│   ├── git_deployer.py      # Git automation
│   └── setup_n8n.py        # N8N deployment
├── 📁 config/               # Configuration files
│   ├── config.yaml          # Main config
│   └── git_config.yaml     # Git settings
├── 📁 docs/                 # Documentation
│   ├── installation.md     # Detailed installation
│   ├── deployment.md       # Deployment guide
│   └── troubleshooting.md  # Problem solving
└── 📁 templates/            # Docker templates
    ├── docker-compose.yml  # N8N Docker setup
    └── nginx.conf          # Nginx configuration
```

## 🔧 Customization

### Edit Configuration
```bash
# Copy and edit main configuration
cp config/config.yaml config/local.yaml
nano config/local.yaml

# Deploy with custom config
./deploy.sh --config config/local.yaml
```

### Key Configuration Options
```yaml
# N8N Settings
n8n:
  port: 5678                    # Change port if needed
  timezone: "America/New_York"  # Set your timezone
  database_type: "postgres"    # sqlite, postgres, mysql

# Security Settings
security:
  basic_auth:
    enabled: true
    user: "admin"
    password: "your_secure_password"
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

#### Port 5678 Already in Use
```bash
# Find what's using the port
sudo lsof -i :5678
# Kill the process or change port in config
```

#### Python Module Not Found
```bash
# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Get Help
```bash
# Run with verbose output
./deploy.sh --verbose

# Check logs
tail -f logs/deployment.log

# Test configuration
./deploy.sh --dry-run
```

## 📚 Next Steps

1. **🌐 Access N8N**: Open http://localhost:5678
2. **📖 Read Documentation**: Check docs/ folder for detailed guides
3. **🔧 Create Workflows**: Start building your automation workflows
4. **💾 Setup Backups**: Configure automated backups in config.yaml
5. **🔒 Secure Installation**: Enable authentication and SSL for production

## 🤝 Support

- **📖 Documentation**: Check the docs/ folder
- **🔧 Troubleshooting**: See docs/troubleshooting.md
- **💬 Issues**: Report issues in the repository
- **📧 Community**: Join N8N community forums

---

**🎉 Happy Automating with N8N!**