# 🚀 N8N Deployment Project

A comprehensive automated deployment system for N8N workflow automation with integrated Git management, file processing capabilities, and complete migration tools.

## 📋 Project Overview

This project provides automated scripts to:
- Read and process project files (script.py, README.md, PRD files)
- Deploy to Git repositories automatically
- Set up N8N self-hosting environment with multiple deployment options
- Migrate existing N8N installations between systems
- Manage project documentation and requirements

## 🏗️ Project Structure

```
n8n-deployment-project/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── prd-document.md                    # Product Requirements Document
├── scripts/
│   ├── script.py                      # Main automation script
│   ├── file_reader.py                 # File reading utilities
│   ├── git_deployer.py                # Git deployment automation
│   ├── setup_n8n.py                   # N8N setup automation
│   ├── n8n-migration-tool.sh          # 🆕 Complete N8N migration tool
│   ├── ubuntu-n8n-auto-install.sh     # 🆕 Automated Ubuntu N8N installer
│   └── prepare-virtualbox-server.sh   # 🆕 VirtualBox server preparation
├── config/
│   ├── config.yaml                    # Main configuration
│   └── git_config.yaml               # Git repository settings
├── docs/
│   ├── installation.md               # Installation guide
│   ├── deployment.md                 # Deployment instructions
│   ├── troubleshooting.md            # Common issues and solutions
│   ├── AUTOMATED_UBUNTU_N8N_SETUP.md # 🆕 Automated Ubuntu setup guide
│   ├── N8N_MIGRATION_GUIDE.md        # 🆕 Complete migration guide
│   └── VIRTUALBOX_SETUP_GUIDE.md     # 🆕 VirtualBox configuration guide
├── templates/
│   ├── docker-compose.yml            # N8N Docker setup
│   └── nginx.conf                    # Nginx configuration
└── deploy.sh                         # Main deployment script
```

## 🚀 Quick Start

### 1. **Standard Deployment**
```bash
git clone https://github.com/guiboratto/n8n-deployment-project.git
cd n8n-deployment-project
chmod +x deploy.sh
./deploy.sh
```

### 2. **🆕 Automated Ubuntu N8N Setup**
```bash
# For VirtualBox Ubuntu Server with Supabase + Cloudflare
chmod +x scripts/ubuntu-n8n-auto-install.sh
sudo ./scripts/ubuntu-n8n-auto-install.sh
```

### 3. **🆕 N8N Migration Between Systems**
```bash
# On source system (create backup)
chmod +x scripts/n8n-migration-tool.sh
./scripts/n8n-migration-tool.sh --source backup

# On target system (restore backup)
./scripts/n8n-migration-tool.sh --target restore
```

## 🎯 Key Features

### 📖 **Automated File Processing**
- **script.py**: Main orchestrator that reads all project files
- **file_reader.py**: Advanced file processing with metadata extraction
- Supports Python, Markdown, YAML, JSON files
- Automatic encoding detection and content parsing

### 🔄 **Git Integration**
- **git_deployer.py**: Complete Git automation
- Automated commits with meaningful messages
- Push to remote repositories
- Branch management and conflict resolution

### 🐳 **N8N Deployment Options**
- **Docker-based deployment** with configuration management
- **Multiple database support** (SQLite, PostgreSQL, MySQL)
- **SSL/TLS setup** with automatic certificate management
- **Backup and restore** capabilities
- **Health checks** and monitoring

### 🆕 **Migration & Setup Tools**
- **Complete N8N migration** between different systems
- **Automated Ubuntu server setup** with Supabase + Cloudflare
- **VirtualBox server preparation** for development
- **Cross-platform migration** support (Docker ↔ npm ↔ snap)

## 🌟 New Migration Features

### 🔄 **N8N Migration Tool**
Automatically transfer N8N data between systems:
- ✅ **All workflows** and configurations
- ✅ **Database** with execution history
- ✅ **Credentials** and authentication
- ✅ **Docker volumes** and containers
- ✅ **Custom nodes** and packages
- ✅ **Logs** and execution records

**Supported Migration Paths:**
- Ubuntu 22.04 PC → VirtualBox Ubuntu Server
- Docker → Docker Compose
- npm → Docker
- Any installation type to any other

### 🖥️ **Automated Ubuntu Setup**
Complete automation for Ubuntu Server:
- ✅ **Docker installation** and configuration
- ✅ **N8N deployment** with Supabase database
- ✅ **Cloudflare Tunnel** for secure access
- ✅ **SSL/TLS encryption** automatically configured
- ✅ **No port forwarding** or VPN required

### 🛠️ **VirtualBox Server Preparation**
One-command VirtualBox Ubuntu Server setup:
- ✅ **System updates** and essential packages
- ✅ **SSH server** configuration with security
- ✅ **Firewall setup** with proper rules
- ✅ **Migration tools** pre-installation

## 📚 Documentation

### **Installation & Deployment**
- [Installation Guide](docs/installation.md) - Detailed installation instructions
- [Deployment Guide](docs/deployment.md) - Advanced deployment options
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

### **🆕 Migration & Setup Guides**
- [Automated Ubuntu N8N Setup](docs/AUTOMATED_UBUNTU_N8N_SETUP.md) - Complete automation guide
- [N8N Migration Guide](docs/N8N_MIGRATION_GUIDE.md) - Transfer N8N between systems
- [VirtualBox Setup Guide](docs/VIRTUALBOX_SETUP_GUIDE.md) - VirtualBox configuration

## 🔧 Usage Examples

### **Basic Deployment**
```bash
# Deploy with default settings
./deploy.sh

# Deploy with custom configuration
./deploy.sh --config config/custom.yaml

# Deploy with verbose output
./deploy.sh --verbose
```

### **🆕 Migration Examples**
```bash
# Create complete backup of N8N installation
./scripts/n8n-migration-tool.sh --source backup

# Export workflows only (lightweight)
./scripts/n8n-migration-tool.sh --source export

# Restore complete backup on new system
./scripts/n8n-migration-tool.sh --target restore

# Import workflows only
./scripts/n8n-migration-tool.sh --target import
```

### **🆕 Automated Setup Examples**
```bash
# Prepare VirtualBox Ubuntu Server
./scripts/prepare-virtualbox-server.sh

# Install N8N with Supabase + Cloudflare
sudo ./scripts/ubuntu-n8n-auto-install.sh

# Setup with specific database
./scripts/ubuntu-n8n-auto-install.sh --database postgres --ssl
```

## 🎯 Use Cases

### **Development & Testing**
- Set up N8N in VirtualBox for safe testing
- Migrate workflows between development and production
- Create isolated environments for different projects

### **Production Deployment**
- Deploy N8N with enterprise-grade security (Cloudflare Tunnel)
- Use Supabase for managed PostgreSQL database
- Automatic SSL/TLS with no manual configuration

### **System Migration**
- Move N8N from local installation to cloud server
- Upgrade from npm to Docker-based installation
- Transfer between different Ubuntu versions

### **Backup & Recovery**
- Create complete backups of N8N installations
- Restore workflows and data after system failures
- Clone N8N setups across multiple servers

## 🔧 Requirements

### **Basic Requirements**
- Python 3.8+
- Git 2.20+
- Ubuntu 18.04+ (for automated scripts)

### **For Docker Deployment**
- Docker 20.10+
- Docker Compose 1.29+

### **For Migration**
- SSH access between systems (for remote migration)
- Sufficient disk space for backups

### **For Automated Setup**
- Cloudflare account with API token
- Supabase account with database URL
- Domain name (optional, can use auto-generated)

## 🚨 Security Features

- ✅ **HTTPS-only access** via Cloudflare Tunnel
- ✅ **No open ports** or VPN requirements
- ✅ **Encrypted database** connections
- ✅ **Secure credential** management
- ✅ **SSH hardening** for server access
- ✅ **Firewall configuration** with minimal attack surface

## 📊 Performance

### **Migration Performance**
- **Complete backup**: 5-15 minutes
- **Workflows only**: 1-5 minutes
- **Cross-platform migration**: 10-20 minutes

### **Deployment Performance**
- **Standard deployment**: 5-10 minutes
- **Automated Ubuntu setup**: 10-15 minutes
- **VirtualBox preparation**: 5-10 minutes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆕 What's New in This Version

### **Version 2.0 - Migration & Automation Update**

#### **New Features:**
- 🔄 **Complete N8N Migration Tool** - Transfer N8N between any systems
- 🖥️ **Automated Ubuntu Setup** - One-command N8N deployment with Supabase + Cloudflare
- 🛠️ **VirtualBox Server Preparation** - Automated server setup for development
- 📚 **Comprehensive Documentation** - Detailed guides for all new features

#### **Enhanced Capabilities:**
- ✅ **Cross-platform migration** support (Docker ↔ npm ↔ snap)
- ✅ **Automated SSL/TLS** configuration via Cloudflare
- ✅ **Zero-configuration** deployment with sensible defaults
- ✅ **Production-ready** security and monitoring

#### **Migration Support:**
- ✅ **Ubuntu 22.04 PC** → **VirtualBox Ubuntu Server**
- ✅ **Any N8N installation** → **Any other installation type**
- ✅ **Complete data transfer** including workflows, credentials, logs
- ✅ **Automatic backup verification** and integrity checks

---

**🎉 Ready for automated N8N deployment and migration!**

Get started with the [Quick Start](#-quick-start) section or dive into the [Migration Guide](docs/N8N_MIGRATION_GUIDE.md) for transferring existing N8N installations.