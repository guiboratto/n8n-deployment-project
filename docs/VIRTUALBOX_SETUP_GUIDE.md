# 🖥️ VirtualBox Ubuntu Server Setup for N8N

Quick reference guide for setting up Ubuntu Server in VirtualBox before running the N8N automation.

## 🎯 VirtualBox VM Configuration

### Recommended VM Settings:
```
Name: Ubuntu-N8N-Server
Type: Linux
Version: Ubuntu (64-bit)
Memory: 4096 MB (4GB) - minimum 2GB
Hard Disk: 25GB VDI (dynamically allocated)
```

### Detailed VM Setup:

#### 1. Create New VM
- **Name**: `Ubuntu-N8N-Server`
- **Machine Folder**: Default
- **Type**: Linux
- **Version**: Ubuntu (64-bit)
- **Memory**: 4096 MB (adjust based on your host)
- **Hard disk**: Create a virtual hard disk now

#### 2. Hard Disk Settings
- **File type**: VDI (VirtualBox Disk Image)
- **Storage**: Dynamically allocated
- **Size**: 25.00 GB (minimum 20GB)

#### 3. VM Settings Configuration
```bash
# Right-click VM → Settings

# System Tab
├── Motherboard
│   ├── Base Memory: 4096 MB
│   ├── Boot Order: Optical, Hard Disk
│   └── Enable I/O APIC: ✅
├── Processor
│   ├── Processors: 2 CPUs
│   └── Enable PAE/NX: ✅
└── Acceleration
    └── Hardware Virtualization: Enable VT-x/AMD-V ✅

# Storage Tab
├── Controller: IDE
│   └── Empty → Choose Ubuntu Server ISO
└── Controller: SATA
    └── Ubuntu-N8N-Server.vdi

# Network Tab
├── Adapter 1
│   ├── Enable Network Adapter: ✅
│   ├── Attached to: NAT (or Bridged Adapter)
│   └── Advanced → Port Forwarding (if using NAT)
```

## 🌐 Network Configuration Options

### Option A: NAT with Port Forwarding (Easier)
```bash
# VirtualBox → VM Settings → Network → Adapter 1
Attached to: NAT

# Advanced → Port Forwarding → Add Rule
Name: SSH
Protocol: TCP
Host IP: 127.0.0.1
Host Port: 2222
Guest IP: (leave empty)
Guest Port: 22

# Optional: N8N Access (if not using Cloudflare Tunnel)
Name: N8N
Protocol: TCP
Host IP: 127.0.0.1
Host Port: 5678
Guest IP: (leave empty)
Guest Port: 5678
```

### Option B: Bridged Adapter (Recommended)
```bash
# VirtualBox → VM Settings → Network → Adapter 1
Attached to: Bridged Adapter
Name: [Your host network interface]

# VM gets its own IP on your local network
# Access via VM's IP address directly
```

## 💿 Ubuntu Server Installation

### 1. Download Ubuntu Server
- **URL**: https://ubuntu.com/download/server
- **Version**: Ubuntu Server 22.04 LTS (recommended)
- **File**: ubuntu-22.04.x-live-server-amd64.iso

### 2. Mount ISO and Start VM
```bash
# VirtualBox → VM Settings → Storage
# Controller: IDE → Empty → Choose disk file
# Select the Ubuntu Server ISO file
# Start the VM
```

### 3. Ubuntu Installation Process
```bash
# Language: English
# Keyboard: [Your layout]
# Network: Configure automatically (DHCP)
# Proxy: (leave empty)
# Mirror: Default
# Storage: Use entire disk (guided)
# Profile Setup:
#   ├── Your name: [Your name]
#   ├── Server name: ubuntu-n8n
#   ├── Username: [your-username]
#   └── Password: [secure-password]
# SSH Setup: Install OpenSSH server ✅
# Snaps: (skip or install Docker if available)
# Installation: Wait for completion
# Reboot: Remove ISO and reboot
```

## 🔧 Post-Installation Setup

### 1. First Boot and Updates
```bash
# Login with your credentials
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git nano htop net-tools

# Check network configuration
ip addr show
# Note the IP address for SSH access
```

### 2. SSH Access (Optional but Recommended)
```bash
# From your host machine:

# If using NAT with port forwarding:
ssh -p 2222 username@localhost

# If using Bridged network:
ssh username@VM_IP_ADDRESS

# Example:
ssh ubuntu@192.168.1.100
```

### 3. Download and Run N8N Installer
```bash
# Method 1: Direct download
curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/ubuntu-n8n-auto-install.sh -o install-n8n.sh
chmod +x install-n8n.sh
sudo ./install-n8n.sh

# Method 2: Clone repository first
git clone https://github.com/guiboratto/n8n-deployment-project.git
cd n8n-deployment-project
sudo ./ubuntu-n8n-auto-install.sh
```

## 📋 Pre-Installation Checklist

### Required Information:
- [ ] **Cloudflare Account** with API token
- [ ] **Supabase Account** with database URL
- [ ] **Domain name** (or use auto-generated)
- [ ] **N8N admin credentials** (username/password)

### Cloudflare API Token Setup:
```bash
# 1. Go to: https://dash.cloudflare.com/profile/api-tokens
# 2. Click "Create Token"
# 3. Use "Custom token" template
# 4. Permissions:
#    ├── Zone:Zone:Read
#    └── Zone:DNS:Edit
# 5. Zone Resources: Include → All zones
# 6. Copy the generated token
```

### Supabase Database Setup:
```bash
# 1. Go to: https://supabase.com/dashboard
# 2. Click "New project"
# 3. Choose organization and fill details
# 4. Wait for project creation
# 5. Go to Settings → Database
# 6. Copy "Connection string" (URI format)
# Example: postgresql://postgres:[password]@[host]:5432/postgres
```

## 🚀 Installation Process

### What the Automation Script Does:
1. ✅ **System Update** - Updates Ubuntu packages
2. ✅ **Docker Installation** - Installs Docker & Docker Compose
3. ✅ **Cloudflare Tunnel** - Installs and configures cloudflared
4. ✅ **Project Setup** - Creates directory structure
5. ✅ **N8N Configuration** - Docker Compose with Supabase
6. ✅ **SSL/TLS Setup** - Automatic HTTPS via Cloudflare
7. ✅ **Service Start** - Starts all services
8. ✅ **Management Scripts** - Creates helper scripts

### Expected Installation Time:
- **System updates**: 2-5 minutes
- **Docker installation**: 3-5 minutes
- **Cloudflare setup**: 2-3 minutes
- **N8N deployment**: 2-3 minutes
- **Total time**: 10-15 minutes

## 🔍 Verification Steps

### Check Installation Success:
```bash
# Check Docker
docker --version
docker ps

# Check N8N container
docker ps | grep n8n

# Check Cloudflare Tunnel
sudo systemctl status cloudflared

# Test local access
curl http://localhost:5678/healthz

# Check logs
docker-compose logs n8n
```

### Access N8N:
- **Secure URL**: https://your-domain.com
- **Local URL**: http://localhost:5678 (or VM IP)
- **Username**: [as configured]
- **Password**: [as configured]

## 🛠️ Troubleshooting

### Common VirtualBox Issues:

#### VM Won't Start
```bash
# Enable virtualization in BIOS/UEFI
# Check: VT-x/AMD-V enabled
# Disable Hyper-V on Windows (if applicable)
```

#### Network Issues
```bash
# Check VM network settings
# Try different network adapter types
# Restart VM networking:
sudo systemctl restart networking
```

#### Performance Issues
```bash
# Increase VM memory allocation
# Enable hardware acceleration
# Close unnecessary host applications
```

### N8N Installation Issues:

#### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

#### Cloudflare Tunnel Issues
```bash
# Check internet connectivity
ping cloudflare.com

# Verify API token permissions
# Check domain ownership in Cloudflare
```

## 📊 Resource Usage

### Minimum Requirements:
- **Host RAM**: 8GB (to allocate 4GB to VM)
- **Host Storage**: 30GB free space
- **Host CPU**: Dual-core with virtualization support

### Recommended Requirements:
- **Host RAM**: 16GB (to allocate 6-8GB to VM)
- **Host Storage**: 50GB+ free space
- **Host CPU**: Quad-core with virtualization support

## 🎯 Final Result

After successful setup, you'll have:

- ✅ **Ubuntu Server VM** running in VirtualBox
- ✅ **Docker environment** fully configured
- ✅ **N8N instance** accessible via HTTPS
- ✅ **Supabase database** integration
- ✅ **Cloudflare Tunnel** for secure access
- ✅ **Management scripts** for easy operation
- ✅ **Automated backups** and monitoring

**Access your N8N securely at: `https://your-domain.com`**

No port forwarding needed, no VPN required! 🚀