#!/bin/bash

# Prepare VirtualBox Ubuntu Server for N8N Migration
# ==================================================
# 
# This script prepares a fresh VirtualBox Ubuntu Server
# to receive N8N migration from Ubuntu 22.04 PC

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║            VirtualBox Server Preparation Tool               ║
║                                                              ║
║  Prepares Ubuntu Server in VirtualBox for N8N migration:    ║
║  • System updates and essential packages                    ║
║  • Docker and Docker Compose installation                   ║
║  • SSH server configuration                                 ║
║  • Network and firewall setup                               ║
║  • Migration tools download                                 ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should NOT be run as root"
   log_info "Run as regular user with sudo privileges"
   exit 1
fi

# Check if user has sudo privileges
if ! sudo -n true 2>/dev/null; then
    log_error "This script requires sudo privileges"
    log_info "Please ensure your user can run sudo commands"
    exit 1
fi

log "Starting VirtualBox Ubuntu Server preparation..."

# Update system packages
update_system() {
    log "Updating system packages..."
    
    sudo apt update
    sudo apt upgrade -y
    
    # Install essential packages
    sudo apt install -y \
        curl \
        wget \
        git \
        nano \
        htop \
        net-tools \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        openssh-server \
        ufw
    
    log "System packages updated successfully"
}

# Configure SSH server
configure_ssh() {
    log "Configuring SSH server..."
    
    # Ensure SSH is running
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # Configure SSH for better security
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Basic SSH hardening
    sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
    
    # Restart SSH service
    sudo systemctl restart ssh
    
    log "SSH server configured and running"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Reset UFW to defaults
    sudo ufw --force reset
    
    # Set default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow N8N port
    sudo ufw allow 5678
    
    # Allow HTTP and HTTPS (for Cloudflare Tunnel)
    sudo ufw allow 80
    sudo ufw allow 443
    
    # Enable firewall
    sudo ufw --force enable
    
    log "Firewall configured successfully"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    # Remove old Docker versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Install Docker Compose (standalone)
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log "Docker installation completed"
    log_warning "You need to logout and login again for Docker group changes to take effect"
}

# Download migration tools
download_migration_tools() {
    log "Downloading N8N migration tools..."
    
    # Create tools directory
    mkdir -p ~/n8n-tools
    cd ~/n8n-tools
    
    # Download migration tool
    curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/n8n-migration-tool.sh -o n8n-migration-tool.sh
    chmod +x n8n-migration-tool.sh
    
    # Download automated installer
    curl -fsSL https://raw.githubusercontent.com/guiboratto/n8n-deployment-project/master/ubuntu-n8n-auto-install.sh -o ubuntu-n8n-auto-install.sh
    chmod +x ubuntu-n8n-auto-install.sh
    
    # Download project files
    git clone https://github.com/guiboratto/n8n-deployment-project.git
    
    log "Migration tools downloaded to ~/n8n-tools/"
}

# Create migration directory
create_migration_directory() {
    log "Creating migration directory..."
    
    mkdir -p ~/n8n-migration
    chmod 755 ~/n8n-migration
    
    log "Migration directory created: ~/n8n-migration"
}

# Display network information
display_network_info() {
    log "Gathering network information..."
    
    echo -e "${CYAN}Network Configuration:${NC}"
    
    # Get IP addresses
    IP_ADDRESSES=$(ip addr show | grep -E "inet.*scope global" | awk '{print $2}' | cut -d'/' -f1)
    
    echo "IP Addresses:"
    for ip in $IP_ADDRESSES; do
        echo "  - $ip"
    done
    
    # Get hostname
    echo "Hostname: $(hostname)"
    
    # Get SSH status
    if systemctl is-active --quiet ssh; then
        echo "SSH Status: ✅ Running"
        echo "SSH Port: 22"
    else
        echo "SSH Status: ❌ Not running"
    fi
    
    # Get firewall status
    echo "Firewall Status: $(sudo ufw status | head -1)"
}

# Create helpful scripts
create_helper_scripts() {
    log "Creating helper scripts..."
    
    # Create migration helper script
    cat > ~/start-migration.sh << 'EOF'
#!/bin/bash
echo "N8N Migration Helper"
echo "==================="
echo ""
echo "Available commands:"
echo "1. Restore complete backup:    ~/n8n-tools/n8n-migration-tool.sh --target restore"
echo "2. Import workflows only:      ~/n8n-tools/n8n-migration-tool.sh --target import"
echo "3. Install fresh N8N:         sudo ~/n8n-tools/ubuntu-n8n-auto-install.sh"
echo ""
echo "Migration directory: ~/n8n-migration"
echo "Tools directory: ~/n8n-tools"
echo ""
echo "Network Information:"
ip addr show | grep -E "inet.*scope global" | awk '{print "IP: " $2}' | cut -d'/' -f1
echo "SSH: ssh $(whoami)@$(hostname -I | awk '{print $1}')"
EOF
    chmod +x ~/start-migration.sh
    
    # Create system info script
    cat > ~/system-info.sh << 'EOF'
#!/bin/bash
echo "VirtualBox Ubuntu Server Information"
echo "==================================="
echo ""
echo "System:"
echo "  OS: $(lsb_release -d | cut -f2)"
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo "  Hostname: $(hostname)"
echo ""
echo "Resources:"
echo "  Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "  Disk: $(df -h / | tail -1 | awk '{print $2}')"
echo "  CPU: $(nproc) cores"
echo ""
echo "Network:"
ip addr show | grep -E "inet.*scope global" | awk '{print "  IP: " $2}' | cut -d'/' -f1
echo ""
echo "Services:"
echo "  SSH: $(systemctl is-active ssh)"
echo "  Docker: $(systemctl is-active docker)"
echo "  UFW: $(sudo ufw status | head -1 | cut -d':' -f2)"
echo ""
echo "Docker:"
if command -v docker &> /dev/null; then
    echo "  Version: $(docker --version)"
    echo "  Compose: $(docker-compose --version)"
else
    echo "  Not installed"
fi
EOF
    chmod +x ~/system-info.sh
    
    log "Helper scripts created in home directory"
}

# Display final information
display_final_info() {
    echo -e "${GREEN}"
    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║                🎉 PREPARATION COMPLETE! 🎉                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  VirtualBox Ubuntu Server is ready for N8N migration!       ║
║                                                              ║
║  📁 Tools Location: ~/n8n-tools/                            ║
║  📁 Migration Directory: ~/n8n-migration/                   ║
║                                                              ║
║  🔧 Helper Scripts:                                          ║
║  • ~/start-migration.sh    - Migration commands             ║
║  • ~/system-info.sh        - System information             ║
║                                                              ║
║  🌐 Network Access:                                          ║
EOF

    # Display IP addresses
    IP_ADDRESSES=$(ip addr show | grep -E "inet.*scope global" | awk '{print $2}' | cut -d'/' -f1)
    for ip in $IP_ADDRESSES; do
        echo "║  • SSH: ssh $(whoami)@$ip                                    ║"
    done

    cat << EOF
║                                                              ║
║  📋 Next Steps:                                              ║
║  1. Transfer backup from Ubuntu 22.04 PC                    ║
║  2. Run: ~/start-migration.sh                               ║
║  3. Follow migration instructions                           ║
║                                                              ║
║  ⚠️  Important: Logout and login again for Docker access    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
}

# Main execution
main() {
    log "Starting VirtualBox Ubuntu Server preparation..."
    
    update_system
    configure_ssh
    configure_firewall
    install_docker
    download_migration_tools
    create_migration_directory
    create_helper_scripts
    display_network_info
    display_final_info
    
    log "VirtualBox Ubuntu Server preparation completed successfully!"
    log_warning "Please logout and login again to apply Docker group changes"
}

# Run main function
main "$@"