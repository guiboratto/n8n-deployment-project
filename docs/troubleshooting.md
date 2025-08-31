# 🔧 Troubleshooting Guide

Common issues and solutions for the N8N Deployment Project.

## 🚨 Quick Diagnostics

### Run Diagnostic Commands
```bash
# Check system status
./deploy.sh --dry-run --verbose

# Check Docker status
docker info
docker-compose ps

# Check logs
tail -f logs/deployment.log
docker-compose logs n8n
```

### Health Check
```bash
# Test N8N accessibility
curl -f http://localhost:5678

# Check with verbose output
curl -v http://localhost:5678/healthz
```

## 🐳 Docker Issues

### Docker Not Running
**Symptoms:**
- `Cannot connect to the Docker daemon`
- `docker: command not found`

**Solutions:**
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker

# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again

# Test Docker
docker run hello-world
```

### Docker Compose Issues
**Symptoms:**
- `docker-compose: command not found`
- `Compose file version not supported`

**Solutions:**
```bash
# Install Docker Compose
sudo apt install docker-compose -y

# Or install latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Check version
docker-compose --version

# Try newer syntax
docker compose version
```

### Container Won't Start
**Symptoms:**
- Container exits immediately
- `Exited (1)` status

**Diagnosis:**
```bash
# Check container logs
docker-compose logs n8n

# Check container status
docker-compose ps

# Inspect container
docker inspect n8n_container_name
```

**Common Solutions:**
```bash
# Remove and recreate containers
docker-compose down
docker-compose up -d

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check for port conflicts
sudo lsof -i :5678
```

### Volume Mount Issues
**Symptoms:**
- Data not persisting
- Permission denied errors

**Solutions:**
```bash
# Check volume permissions
ls -la n8n-data/

# Fix permissions
sudo chown -R 1000:1000 n8n-data/
sudo chmod -R 755 n8n-data/

# Recreate volumes
docker-compose down -v
docker-compose up -d
```

## 🌐 Network Issues

### Port Already in Use
**Symptoms:**
- `Port 5678 is already in use`
- `Address already in use`

**Solutions:**
```bash
# Find process using port
sudo lsof -i :5678
sudo netstat -tulpn | grep :5678

# Kill process
sudo kill -9 <PID>

# Or change port in config
nano config/config.yaml
# Change n8n.port to different value
```

### Cannot Access N8N Web Interface
**Symptoms:**
- Browser shows "This site can't be reached"
- Connection timeout

**Diagnosis:**
```bash
# Check if N8N is running
docker-compose ps

# Check port binding
docker port n8n_container_name

# Test local connection
curl http://localhost:5678
telnet localhost 5678
```

**Solutions:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 5678

# Check Docker network
docker network ls
docker network inspect n8n_default

# Restart containers
docker-compose restart
```

### SSL/TLS Issues
**Symptoms:**
- "Your connection is not private"
- SSL certificate errors

**Solutions:**
```bash
# Check certificate validity
openssl x509 -in certs/cert.pem -text -noout

# Regenerate self-signed certificates
rm -rf certs/
./deploy.sh --ssl

# Check certificate permissions
ls -la certs/
sudo chown -R 1000:1000 certs/
```

## 🐍 Python Issues

### Python Module Not Found
**Symptoms:**
- `ModuleNotFoundError: No module named 'xyz'`
- Import errors

**Solutions:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt

# Update pip
pip install --upgrade pip

# Install specific module
pip install module_name
```

### Python Version Issues
**Symptoms:**
- `Python 3.8+ required`
- Syntax errors

**Solutions:**
```bash
# Check Python version
python3 --version

# Install Python 3.8+
sudo apt update
sudo apt install python3.8 python3.8-pip

# Use specific Python version
python3.8 -m pip install -r requirements.txt
python3.8 scripts/script.py
```

### Permission Issues
**Symptoms:**
- `Permission denied` when running scripts
- Cannot write to directories

**Solutions:**
```bash
# Make scripts executable
chmod +x deploy.sh
chmod +x scripts/*.py

# Fix directory permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Create directories with correct permissions
mkdir -p logs backups local-files
chmod 755 logs backups local-files
```

## 📁 File System Issues

### Disk Space Issues
**Symptoms:**
- `No space left on device`
- Deployment fails with disk errors

**Diagnosis:**
```bash
# Check disk usage
df -h
du -sh *

# Check Docker disk usage
docker system df
```

**Solutions:**
```bash
# Clean Docker system
docker system prune -a
docker volume prune

# Remove old backups
find backups/ -name "*.tar.gz" -mtime +30 -delete

# Clean logs
truncate -s 0 logs/*.log
```

### File Permission Issues
**Symptoms:**
- Cannot read/write files
- Permission denied errors

**Solutions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod +x deploy.sh scripts/*.py

# SELinux issues (CentOS/RHEL)
sudo setsebool -P container_manage_cgroup on
```

## 🔐 Git Issues

### Git Authentication Failed
**Symptoms:**
- `Authentication failed`
- `Permission denied (publickey)`

**Solutions:**
```bash
# Setup SSH key
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
cat ~/.ssh/id_rsa.pub
# Add to GitHub/GitLab

# Test SSH connection
ssh -T git@github.com

# Use HTTPS with token
git remote set-url origin https://username:token@github.com/user/repo.git

# Configure Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Git Repository Issues
**Symptoms:**
- `Not a git repository`
- `Remote origin already exists`

**Solutions:**
```bash
# Initialize Git repository
git init
git remote add origin <repository-url>

# Fix remote URL
git remote set-url origin <new-url>

# Reset Git repository
rm -rf .git
git init
git remote add origin <repository-url>
```

### Merge Conflicts
**Symptoms:**
- `Automatic merge failed`
- Conflict markers in files

**Solutions:**
```bash
# Check status
git status

# Resolve conflicts manually
nano conflicted_file.txt

# Mark as resolved
git add conflicted_file.txt
git commit -m "Resolve merge conflict"

# Abort merge
git merge --abort
```

## ⚙️ Configuration Issues

### Invalid Configuration
**Symptoms:**
- `YAML parsing error`
- `Configuration validation failed`

**Solutions:**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Check configuration
./deploy.sh --dry-run --verbose

# Reset to default configuration
cp config/config.yaml.example config/config.yaml
```

### Environment Variables
**Symptoms:**
- Configuration not applied
- Default values used

**Solutions:**
```bash
# Check environment variables
env | grep N8N

# Set environment variables
export N8N_PORT=5678
export N8N_WEBHOOK_URL=http://localhost:5678

# Use .env file
echo "N8N_PORT=5678" > .env
echo "N8N_WEBHOOK_URL=http://localhost:5678" >> .env
```

## 🗄️ Database Issues

### Database Connection Failed
**Symptoms:**
- `Connection refused`
- `Database does not exist`

**Solutions:**
```bash
# Check database container
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait for database to start
docker-compose up -d n8n
```

### Database Migration Issues
**Symptoms:**
- `Migration failed`
- Schema errors

**Solutions:**
```bash
# Reset N8N database
docker-compose down
docker volume rm n8n_postgres_data
docker-compose up -d

# Manual database reset
docker-compose exec postgres psql -U n8n -d n8n -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

## 🔍 Performance Issues

### Slow Performance
**Symptoms:**
- Long response times
- High CPU/memory usage

**Diagnosis:**
```bash
# Check system resources
htop
docker stats

# Check N8N logs for errors
docker-compose logs n8n | grep ERROR

# Monitor disk I/O
iotop
```

**Solutions:**
```bash
# Increase container resources
# Edit docker-compose.yml
services:
  n8n:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

# Optimize database
docker-compose exec postgres psql -U n8n -d n8n -c "VACUUM ANALYZE;"

# Clean up old executions
# Access N8N web interface > Settings > Executions
```

### Memory Issues
**Symptoms:**
- Out of memory errors
- Container killed by OOM killer

**Solutions:**
```bash
# Check memory usage
free -h
docker stats

# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🔧 Advanced Troubleshooting

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
./deploy.sh --verbose

# Run with Python debugger
python3 -m pdb scripts/script.py
```

### Container Debugging
```bash
# Access container shell
docker-compose exec n8n /bin/bash

# Check container processes
docker-compose exec n8n ps aux

# Check container network
docker-compose exec n8n netstat -tulpn
```

### System Debugging
```bash
# Check system logs
journalctl -u docker -f
dmesg | tail

# Check system resources
vmstat 1
iostat 1
```

## 📋 Diagnostic Information Collection

### Collect System Information
```bash
# Create diagnostic report
cat > diagnostic_report.txt << EOF
=== System Information ===
$(uname -a)
$(lsb_release -a 2>/dev/null || cat /etc/os-release)

=== Docker Information ===
$(docker --version)
$(docker-compose --version)
$(docker info)

=== Python Information ===
$(python3 --version)
$(pip3 list | grep -E "(yaml|requests|docker)")

=== Git Information ===
$(git --version)
$(git status 2>/dev/null || echo "Not a git repository")

=== Network Information ===
$(netstat -tulpn | grep :5678)

=== Disk Space ===
$(df -h)

=== Memory Usage ===
$(free -h)

=== Container Status ===
$(docker-compose ps)

=== Recent Logs ===
$(tail -n 50 logs/deployment.log 2>/dev/null || echo "No deployment log found")
EOF

echo "Diagnostic report saved to diagnostic_report.txt"
```

## 🆘 Getting Help

### Before Asking for Help
1. **Check this troubleshooting guide**
2. **Review log files** (`logs/deployment.log`, `docker-compose logs`)
3. **Run diagnostic commands** (`--dry-run --verbose`)
4. **Search existing issues** in the repository

### When Reporting Issues
Include:
- **System information** (OS, Docker version, Python version)
- **Error messages** (exact error text)
- **Log files** (relevant portions)
- **Configuration** (sanitized config files)
- **Steps to reproduce** the issue

### Useful Commands for Support
```bash
# Generate support bundle
./deploy.sh --dry-run --verbose > support_info.txt 2>&1
docker-compose logs >> support_info.txt 2>&1
cat logs/deployment.log >> support_info.txt 2>&1
```

## 🔄 Recovery Procedures

### Complete Reset
```bash
# Stop all services
docker-compose down -v

# Remove all data (WARNING: This deletes everything!)
sudo rm -rf n8n-data/ postgres-data/ logs/ backups/

# Redeploy from scratch
./deploy.sh --force
```

### Backup Recovery
```bash
# Stop services
docker-compose down

# Restore from backup
tar -xzf backups/n8n-backup-YYYYMMDD_HHMMSS.tar.gz

# Restart services
docker-compose up -d
```

### Configuration Recovery
```bash
# Reset configuration to defaults
cp config/config.yaml.example config/config.yaml

# Redeploy with default config
./deploy.sh --config config/config.yaml --force
```

Remember: When in doubt, check the logs first! Most issues can be diagnosed by carefully reading the error messages in the log files.