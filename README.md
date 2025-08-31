# 🚀 N8N Self-Hosting Deployment Project

A comprehensive project for deploying n8n automation workflows with automated Git deployment and file management.

## 📋 Project Overview

This project provides automated scripts to:
- Read and process project files (script.py, README.md, PRD files)
- Deploy to Git repositories automatically
- Set up n8n self-hosting environment
- Manage project documentation and requirements

## 🏗️ Project Structure

```
n8n-deployment-project/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── prd-document.md          # Product Requirements Document
├── scripts/
│   ├── script.py            # Main automation script
│   ├── file_reader.py       # File reading utilities
│   ├── git_deployer.py      # Git deployment automation
│   └── setup_n8n.py        # N8N setup automation
├── config/
│   ├── config.yaml          # Configuration settings
│   └── git_config.yaml     # Git repository settings
├── docs/
│   ├── installation.md     # Installation guide
│   ├── deployment.md       # Deployment instructions
│   └── troubleshooting.md  # Common issues and solutions
├── templates/
│   ├── docker-compose.yml  # N8N Docker setup
│   └── nginx.conf          # Nginx configuration
└── deploy.sh               # Main deployment script
```

## 🚀 Quick Start

1. **Clone and Setup:**
```bash
git clone <your-repo-url>
cd n8n-deployment-project
chmod +x deploy.sh
./deploy.sh
```

2. **Configure Git:**
```bash
python scripts/git_deployer.py --setup
```

3. **Deploy N8N:**
```bash
python scripts/setup_n8n.py --deploy
```

## 📖 Features

- ✅ Automated file reading and processing
- ✅ Git repository management
- ✅ N8N Docker deployment
- ✅ Configuration management
- ✅ Documentation generation
- ✅ Error handling and logging

## 🔧 Requirements

- Python 3.8+
- Git
- Docker & Docker Compose
- Ubuntu/Debian Linux

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Deployment Instructions](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Created for automated n8n deployment and project management**