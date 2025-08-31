# 🚀 Deployment Guide

Comprehensive guide for deploying the N8N project to various environments.

## 🎯 Deployment Overview

This project supports multiple deployment scenarios:
- **Local Development**: Run on your local machine
- **VPS/Cloud Server**: Deploy to a remote server
- **Docker Container**: Containerized deployment
- **Git Repository**: Automated Git-based deployment

## 🏠 Local Development Deployment

### Quick Local Setup
```bash
# Clone and deploy locally
git clone <repository-url>
cd n8n-deployment-project
./deploy.sh
```

### Custom Local Configuration
```bash
# Create local config
cp config/config.yaml config/local.yaml

# Edit configuration
nano config/local.yaml

# Deploy with custom config
./deploy.sh --config config/local.yaml
```

### Local Development Features
- **Hot Reload**: Automatic restart on file changes
- **Debug Mode**: Enhanced logging and error reporting
- **Local File Access**: Direct access to project files
- **No SSL Required**: HTTP access for development

## 🌐 VPS/Cloud Server Deployment

### Prerequisites
- Ubuntu 18.04+ or similar Linux distribution
- 2GB+ RAM, 10GB+ storage
- Root or sudo access
- Domain name (optional, for SSL)

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install curl wget git nano htop -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login to apply group changes
```

### 2. Deploy to Server
```bash
# Clone repository
git clone <repository-url>
cd n8n-deployment-project

# Configure for production
cp config/config.yaml config/production.yaml
nano config/production.yaml
```

**Production Configuration Example:**
```yaml
n8n:
  port: 5678
  host: "0.0.0.0"
  protocol: "https"
  webhook_url: "https://your-domain.com"
  ssl_enabled: true

deployment:
  environment: "production"
  
security:
  basic_auth:
    enabled: true
    user: "admin"
    password: "secure_password_here"
```

### 3. SSL/TLS Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot -y

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Update config to use certificates
```

#### Option B: Self-Signed Certificates
```bash
# Generate certificates
./deploy.sh --ssl --config config/production.yaml
```

### 4. Firewall Configuration
```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5678
sudo ufw enable
```

### 5. Deploy
```bash
# Deploy with production config
./deploy.sh --config config/production.yaml --ssl
```

## 🐳 Docker Deployment

### Standalone Docker
```bash
# Build and run
docker build -t n8n-deployer .
docker run -d \
  --name n8n-deployment \
  -p 5678:5678 \
  -v $(pwd):/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  n8n-deployer
```

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=UTC
      - WEBHOOK_URL=http://localhost:5678
      - N8N_SECURE_COOKIE=false
    volumes:
      - n8n_data:/home/node/.n8n
      - ./local-files:/files
    networks:
      - n8n_network

  postgres:
    image: postgres:13
    container_name: n8n_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n_network

volumes:
  n8n_data:
  postgres_data:

networks:
  n8n_network:
    driver: bridge
```

## 📦 Git Repository Deployment

### Automated Git Deployment
```bash
# Deploy and push to Git
./deploy.sh --git-remote https://github.com/user/repo.git

# Git-only operations
./deploy.sh --git-only --git-remote https://github.com/user/repo.git
```

### Git Configuration
```yaml
git:
  user:
    name: "Deployment Bot"
    email: "deploy@yourcompany.com"
  
  auto_commit: true
  commit_message_template: "🚀 Deploy: {timestamp}"
  
  remote:
    url: "https://github.com/user/repo.git"
    branch: "main"
```

### GitHub Actions Integration
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy N8N

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run deployment
      run: |
        chmod +x deploy.sh
        ./deploy.sh --setup-n8n
    
    - name: Test deployment
      run: |
        # Add your tests here
        curl -f http://localhost:5678 || exit 1
```

## ☁️ Cloud Platform Deployment

### AWS EC2
```bash
# Launch EC2 instance (Ubuntu 20.04)
# Configure security groups (ports 22, 80, 443, 5678)
# SSH to instance and run:

sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
git clone <repository-url>
cd n8n-deployment-project
./deploy.sh --config config/aws.yaml
```

### Google Cloud Platform
```bash
# Create Compute Engine instance
gcloud compute instances create n8n-server \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --tags=http-server,https-server

# SSH and deploy
gcloud compute ssh n8n-server
# ... follow standard deployment steps
```

### DigitalOcean
```bash
# Create droplet via web interface or CLI
doctl compute droplet create n8n-server \
  --image ubuntu-20-04-x64 \
  --size s-2vcpu-2gb \
  --region nyc1

# SSH and deploy
ssh root@your-droplet-ip
# ... follow standard deployment steps
```

### Heroku
Create `Procfile`:
```
web: python3 scripts/script.py --setup-n8n
```

Create `heroku.yml`:
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: python3 scripts/script.py --setup-n8n
```

## 🔧 Environment-Specific Configurations

### Development Environment
```yaml
deployment:
  environment: "development"
  
n8n:
  port: 5678
  protocol: "http"
  secure_cookie: false
  
logging:
  level: "DEBUG"
  console:
    enabled: true
    colored: true

development:
  debug: true
  hot_reload: true
  auto_restart: true
```

### Staging Environment
```yaml
deployment:
  environment: "staging"
  
n8n:
  port: 5678
  protocol: "https"
  ssl_enabled: true
  
security:
  basic_auth:
    enabled: true
    user: "staging"
    password: "staging_password"

monitoring:
  health_check:
    enabled: true
    interval: 60
```

### Production Environment
```yaml
deployment:
  environment: "production"
  
n8n:
  port: 5678
  protocol: "https"
  ssl_enabled: true
  database_type: "postgres"
  
security:
  basic_auth:
    enabled: true
    user: "admin"
    password: "strong_production_password"

monitoring:
  health_check:
    enabled: true
    interval: 30
  alerts:
    enabled: true
    
backup:
  enabled: true
  schedule: "daily"
  retention_days: 30

production:
  optimize_for_production: true
  enable_caching: true
  security_headers: true
  rate_limiting: true
```

## 🔄 Deployment Strategies

### Blue-Green Deployment
```bash
# Deploy to staging (green)
./deploy.sh --config config/staging.yaml

# Test staging environment
curl -f https://staging.yourdomain.com

# Switch to production (blue)
./deploy.sh --config config/production.yaml
```

### Rolling Deployment
```bash
# Deploy with zero downtime
docker-compose up -d --scale n8n=2
# Wait for health check
docker-compose up -d --scale n8n=1
```

### Canary Deployment
```bash
# Deploy to subset of users
./deploy.sh --config config/canary.yaml
# Monitor metrics
# Gradually increase traffic
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint
```bash
# Check N8N health
curl http://localhost:5678/healthz

# Check with authentication
curl -u admin:password http://localhost:5678/healthz
```

### Monitoring Setup
```yaml
monitoring:
  health_check:
    enabled: true
    interval: 30
    timeout: 10
    retries: 3
  
  metrics:
    enabled: true
    port: 9090
    endpoint: "/metrics"
  
  alerts:
    enabled: true
    webhook_url: "https://hooks.slack.com/your-webhook"
```

### Log Monitoring
```bash
# View deployment logs
tail -f logs/deployment.log

# View N8N logs
docker-compose logs -f n8n

# View system logs
journalctl -u docker -f
```

## 🔐 Security Considerations

### Basic Security Setup
```yaml
security:
  basic_auth:
    enabled: true
    user: "admin"
    password: "secure_random_password"
  
  ssl_enabled: true
  secure_cookie: true
  
  rate_limiting: true
  security_headers: true
```

### Advanced Security
```bash
# Setup fail2ban
sudo apt install fail2ban -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Regular security updates
sudo apt update && sudo apt upgrade -y
```

## 🔄 Backup and Recovery

### Automated Backups
```yaml
backup:
  enabled: true
  schedule: "daily"
  retention_days: 30
  directory: "./backups"
```

### Manual Backup
```bash
# Create backup
./deploy.sh --backup

# Restore from backup
python3 scripts/setup_n8n.py --restore backups/n8n-backup-20231201_120000.tar.gz
```

## 🚨 Troubleshooting Deployment

### Common Issues

#### Port Already in Use
```bash
# Find process using port
sudo lsof -i :5678
# Kill process or change port
```

#### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in certs/cert.pem -text -noout

# Regenerate certificates
./deploy.sh --ssl --force
```

#### Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Deployment Validation
```bash
# Run deployment validation
./deploy.sh --dry-run --verbose

# Test all endpoints
curl -f http://localhost:5678
curl -f http://localhost:5678/healthz
```

## 📚 Next Steps

After successful deployment:

1. **Configure N8N**: Set up your first workflows
2. **Setup Monitoring**: Configure alerts and health checks
3. **Backup Strategy**: Implement regular backups
4. **Security Hardening**: Review and enhance security settings
5. **Performance Tuning**: Optimize for your workload

## 🤝 Support

For deployment issues:
- Check the [troubleshooting guide](troubleshooting.md)
- Review deployment logs
- Test with `--dry-run` flag
- Use `--verbose` for detailed output