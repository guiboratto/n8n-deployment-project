# 🔄 N8N Migration Guide

**Automatically transfer N8N configuration, workflows, logs, and data from Ubuntu 22.04 PC to VirtualBox Ubuntu Server**

## 🎯 What Gets Migrated

### ✅ **Complete Data Transfer:**
- 🔄 **All workflows** and their configurations
- 🔐 **Credentials** and authentication data
- 🗄️ **Database** (SQLite/PostgreSQL) with execution history
- 📊 **Logs** and execution records
- 🐳 **Docker volumes** and container configurations
- ⚙️ **Environment variables** and settings
- 📦 **Custom nodes** and installed packages
- 🔒 **SSL certificates** and security keys
- 💾 **Backup files** and scripts

### 🔍 **Supported N8N Installations:**
- ✅ **Docker** (single container)
- ✅ **Docker Compose** (multi-container setup)
- ✅ **npm** (global installation)
- ✅ **snap** (Ubuntu snap package)

## 🚀 Quick Migration Process

### **Step 1: On Source Ubuntu 22.04 PC**
```bash
# Download migration tool
curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/n8n-migration-tool.sh -o n8n-migration-tool.sh
chmod +x n8n-migration-tool.sh

# Create complete backup
./n8n-migration-tool.sh --source backup
```

### **Step 2: Transfer to VirtualBox Server**
```bash
# Option A: SCP transfer
scp ~/n8n-migration/n8n-complete-backup-*.tar.gz user@virtualbox-server:~/

# Option B: Use built-in transfer helper
./n8n-migration-tool.sh --transfer
```

### **Step 3: On VirtualBox Ubuntu Server**
```bash
# Download migration tool
curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/n8n-migration-tool.sh -o n8n-migration-tool.sh
chmod +x n8n-migration-tool.sh

# Restore complete backup
./n8n-migration-tool.sh --target restore
```

## 📋 Detailed Migration Steps

### 🔍 **Pre-Migration Checklist**

#### On Source Ubuntu 22.04 PC:
- [ ] **N8N is running** and accessible
- [ ] **All workflows saved** and tested
- [ ] **Credentials backed up** (if using external storage)
- [ ] **Custom nodes documented** (if any)
- [ ] **Sufficient disk space** for backup (check with `df -h`)

#### On Target VirtualBox Server:
- [ ] **Ubuntu Server installed** and updated
- [ ] **Docker installed** (if using Docker-based migration)
- [ ] **Network connectivity** between source and target
- [ ] **SSH access configured** (for remote transfer)
- [ ] **Sufficient disk space** for restoration

### 🔧 **Source System: Create Backup**

#### **Option A: Complete Backup (Recommended)**
```bash
# Navigate to your home directory
cd ~

# Download migration tool
curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/n8n-migration-tool.sh -o n8n-migration-tool.sh
chmod +x n8n-migration-tool.sh

# Create complete backup
./n8n-migration-tool.sh --source backup

# Check backup location
ls -la ~/n8n-migration/
```

**What this creates:**
- Complete backup file: `n8n-complete-backup-YYYYMMDD_HHMMSS.tar.gz`
- Includes: workflows, database, Docker volumes, configurations, logs
- Size: Typically 10MB - 1GB depending on your data

#### **Option B: Workflows Only (Lightweight)**
```bash
# Export only workflows and configurations
./n8n-migration-tool.sh --source export

# Check export location
ls -la ~/n8n-migration/
```

**What this creates:**
- Lightweight export: `n8n-workflows-export-YYYYMMDD_HHMMSS.tar.gz`
- Includes: workflows, credentials, basic configurations
- Size: Typically 1-10MB

### 📤 **Transfer Backup to VirtualBox Server**

#### **Method 1: SCP (Secure Copy)**
```bash
# From source Ubuntu 22.04 PC
scp ~/n8n-migration/n8n-complete-backup-*.tar.gz username@virtualbox-ip:~/

# Example:
scp ~/n8n-migration/n8n-complete-backup-20250101_120000.tar.gz ubuntu@192.168.1.100:~/
```

#### **Method 2: rsync (Recommended for large files)**
```bash
# From source Ubuntu 22.04 PC
rsync -avz ~/n8n-migration/ username@virtualbox-ip:~/n8n-migration/

# Example:
rsync -avz ~/n8n-migration/ ubuntu@192.168.1.100:~/n8n-migration/
```

#### **Method 3: USB/External Drive**
```bash
# Copy to USB drive
cp ~/n8n-migration/n8n-complete-backup-*.tar.gz /media/usb-drive/

# On VirtualBox server, mount USB and copy
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
cp /mnt/usb/n8n-complete-backup-*.tar.gz ~/
```

#### **Method 4: Cloud Storage**
```bash
# Upload to cloud (Google Drive, Dropbox, etc.)
# Then download on VirtualBox server
wget "https://drive.google.com/your-backup-file" -O n8n-backup.tar.gz
```

### 🔧 **Target System: Restore Backup**

#### **Prepare VirtualBox Ubuntu Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required tools
sudo apt install -y curl wget git

# If restoring Docker-based N8N, install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Logout and login again
```

#### **Download Migration Tool**
```bash
# Download migration tool
curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/n8n-migration-tool.sh -o n8n-migration-tool.sh
chmod +x n8n-migration-tool.sh
```

#### **Restore Complete Backup**
```bash
# If backup file is in home directory
export BACKUP_FILE_PATH=~/n8n-complete-backup-*.tar.gz

# Restore backup
./n8n-migration-tool.sh --target restore
```

#### **Import Workflows Only**
```bash
# If you have workflows export file
./n8n-migration-tool.sh --target import
```

## 🔍 **Migration Scenarios**

### **Scenario 1: Docker to Docker**
```bash
# Source: Docker N8N on Ubuntu 22.04
./n8n-migration-tool.sh --source backup

# Target: Docker N8N on VirtualBox Ubuntu
./n8n-migration-tool.sh --target restore
```

### **Scenario 2: npm to Docker Compose**
```bash
# Source: npm N8N installation
./n8n-migration-tool.sh --source backup

# Target: Install Docker Compose N8N first, then restore
./n8n-migration-tool.sh --target restore
```

### **Scenario 3: Any to Fresh Installation**
```bash
# Source: Any N8N installation
./n8n-migration-tool.sh --source export

# Target: Fresh N8N installation
./n8n-migration-tool.sh --target import
```

## 🛠️ **Advanced Migration Options**

### **Custom Backup Location**
```bash
# Set custom migration directory
export MIGRATION_DIR="/path/to/custom/location"
./n8n-migration-tool.sh --source backup
```

### **Selective Migration**
```bash
# Backup only workflows (no logs/history)
./n8n-migration-tool.sh --source export

# Restore to different N8N installation type
./n8n-migration-tool.sh --target import
```

### **Cross-Platform Migration**
```bash
# Works between different installation types:
# npm → Docker
# Docker → Docker Compose
# snap → npm
# Any combination supported
```

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **Migration Tool Not Found**
```bash
# Ensure script is executable
chmod +x n8n-migration-tool.sh

# Check if downloaded correctly
ls -la n8n-migration-tool.sh
```

#### **N8N Not Detected**
```bash
# Check if N8N is running
docker ps | grep n8n          # For Docker
ps aux | grep n8n             # For npm/snap
systemctl status n8n          # For service

# Manually specify N8N type
export N8N_TYPE="docker"      # or "npm", "snap", "docker-compose"
```

#### **Permission Denied**
```bash
# Fix file permissions
sudo chown -R $USER:$USER ~/n8n-migration/
chmod -R 755 ~/n8n-migration/

# For Docker volumes
sudo chown -R 1000:1000 /var/lib/docker/volumes/n8n_data/
```

#### **Backup File Too Large**
```bash
# Use workflows-only export instead
./n8n-migration-tool.sh --source export

# Or compress backup further
gzip -9 n8n-complete-backup-*.tar.gz
```

#### **Network Transfer Issues**
```bash
# Test SSH connectivity
ssh username@virtualbox-ip

# Use alternative transfer methods
# USB drive, cloud storage, etc.
```

#### **Docker Volume Issues**
```bash
# List Docker volumes
docker volume ls

# Inspect volume
docker volume inspect n8n_data

# Manually backup volume
docker run --rm -v n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_data.tar.gz /data
```

#### **Database Connection Issues**
```bash
# Check database file permissions
ls -la ~/.n8n/database.sqlite

# For PostgreSQL/MySQL
docker-compose logs postgres
docker-compose logs mysql
```

### **Verification Steps**

#### **After Migration, Verify:**
```bash
# Check N8N is running
docker ps | grep n8n
curl http://localhost:5678/healthz

# Check workflows imported
# Access N8N web interface and verify workflows

# Check logs
docker-compose logs n8n
tail -f ~/.n8n/logs/n8n.log

# Test workflow execution
# Run a simple workflow to ensure everything works
```

## 📊 **Migration Performance**

### **Typical Migration Times:**
- **Workflows only**: 1-5 minutes
- **Complete backup**: 5-15 minutes
- **Large installations**: 15-30 minutes

### **Backup Sizes:**
- **Workflows only**: 1-10 MB
- **Small installation**: 10-100 MB
- **Large installation**: 100MB - 1GB

### **Network Transfer:**
- **Local network**: 1-10 minutes
- **Internet upload**: Depends on bandwidth
- **USB transfer**: 2-5 minutes

## 🎯 **Post-Migration Checklist**

### **Verify Migration Success:**
- [ ] **N8N web interface** accessible
- [ ] **All workflows** present and functional
- [ ] **Credentials** working correctly
- [ ] **Execution history** preserved (if full backup)
- [ ] **Custom nodes** installed and working
- [ ] **Webhooks** updated with new URLs
- [ ] **Scheduled workflows** running correctly
- [ ] **Database connections** working
- [ ] **File permissions** correct

### **Update Configuration:**
- [ ] **Webhook URLs** updated for new server
- [ ] **Environment variables** adjusted if needed
- [ ] **SSL certificates** configured for new domain
- [ ] **Firewall rules** updated
- [ ] **Backup scripts** configured for new location

### **Test Workflows:**
- [ ] **Run test workflows** to verify functionality
- [ ] **Check external integrations** (APIs, databases)
- [ ] **Verify scheduled executions**
- [ ] **Test webhook endpoints**

## 🔄 **Rollback Plan**

If migration fails, you can rollback:

### **On Source System:**
```bash
# Your original N8N is still intact
# Simply continue using it

# If you stopped it during migration:
docker start n8n                    # For Docker
systemctl start n8n                 # For service
```

### **On Target System:**
```bash
# Remove failed migration
docker-compose down
docker volume rm n8n_data
rm -rf ~/n8n-deployment/

# Start fresh installation
# Re-run installation scripts
```

## 🎉 **Success!**

After successful migration, your VirtualBox Ubuntu Server will have:

- ✅ **Complete N8N installation** with all your data
- ✅ **All workflows** and configurations preserved
- ✅ **Execution history** and logs (if full backup)
- ✅ **Credentials** and authentication working
- ✅ **Custom nodes** and packages installed
- ✅ **Same functionality** as original installation

Your N8N instance is now running on the VirtualBox Ubuntu Server with all your previous work intact! 🚀

## 📞 **Support**

If you encounter issues:
1. **Check the troubleshooting section** above
2. **Review migration logs** in `~/n8n-migration/`
3. **Verify system requirements** are met
4. **Test with workflows-only migration** first
5. **Check N8N community forums** for specific issues

The migration tool automatically detects your N8N installation type and handles the complexity of transferring between different setups!