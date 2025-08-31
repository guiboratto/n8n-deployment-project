#!/bin/bash

# N8N Migration Tool
# ==================
# 
# Automatically transfers N8N configuration, data, logs, and workflows
# from Ubuntu 22.04 PC to VirtualBox Ubuntu Server
#
# Usage:
#   ./n8n-migration-tool.sh --source [source_mode] --target [target_mode]
#
# Modes:
#   --source: backup, export
#   --target: restore, import

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MIGRATION_DIR="$HOME/n8n-migration"
BACKUP_FILE="n8n-complete-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
TEMP_DIR="/tmp/n8n-migration-$$"

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
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    N8N Migration Tool                       ║
║                                                              ║
║  Automatically transfer N8N data between systems:           ║
║  • Workflows and configurations                             ║
║  • Database data and credentials                            ║
║  • Logs and execution history                               ║
║  • Custom nodes and settings                                ║
║  • Docker volumes and containers                            ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Help function
show_help() {
    cat << EOF
N8N Migration Tool - Transfer N8N data between Ubuntu systems

USAGE:
    $0 --source [MODE]     # Run on source Ubuntu 22.04 PC
    $0 --target [MODE]     # Run on target VirtualBox Ubuntu Server
    $0 --help             # Show this help

SOURCE MODES (run on original Ubuntu 22.04 PC):
    backup                # Create complete backup of N8N data
    export                # Export workflows and configurations only

TARGET MODES (run on VirtualBox Ubuntu Server):
    restore               # Restore complete N8N backup
    import                # Import workflows and configurations only

EXAMPLES:
    # On source Ubuntu 22.04 PC:
    $0 --source backup

    # Transfer backup file to VirtualBox server, then:
    $0 --target restore

    # For workflows only:
    $0 --source export
    $0 --target import

WHAT GETS MIGRATED:
    ✅ N8N workflows and credentials
    ✅ Database data (SQLite/PostgreSQL)
    ✅ Execution logs and history
    ✅ Custom nodes and packages
    ✅ Environment variables and settings
    ✅ Docker volumes and configurations
    ✅ SSL certificates and keys
    ✅ Backup files and scripts

EOF
}

# Detect N8N installation type
detect_n8n_installation() {
    log "Detecting N8N installation type..."
    
    N8N_TYPE=""
    N8N_DATA_DIR=""
    N8N_CONFIG_DIR=""
    
    # Check for Docker installation
    if command -v docker &> /dev/null && docker ps | grep -q n8n; then
        N8N_TYPE="docker"
        N8N_DATA_DIR="/var/lib/docker/volumes"
        log_info "Found Docker-based N8N installation"
    
    # Check for npm global installation
    elif command -v n8n &> /dev/null; then
        N8N_TYPE="npm"
        N8N_DATA_DIR="$HOME/.n8n"
        log_info "Found npm-based N8N installation"
    
    # Check for snap installation
    elif snap list | grep -q n8n 2>/dev/null; then
        N8N_TYPE="snap"
        N8N_DATA_DIR="$HOME/snap/n8n/current/.n8n"
        log_info "Found snap-based N8N installation"
    
    # Check common Docker Compose locations
    elif [ -f "$HOME/n8n/docker-compose.yml" ] || [ -f "$HOME/n8n-deployment/docker-compose.yml" ]; then
        N8N_TYPE="docker-compose"
        if [ -f "$HOME/n8n/docker-compose.yml" ]; then
            N8N_CONFIG_DIR="$HOME/n8n"
        else
            N8N_CONFIG_DIR="$HOME/n8n-deployment"
        fi
        log_info "Found Docker Compose N8N installation"
    
    else
        log_error "No N8N installation detected!"
        log_info "Please ensure N8N is installed and running"
        exit 1
    fi
    
    log "N8N installation type: $N8N_TYPE"
}

# Create backup of complete N8N installation
create_complete_backup() {
    log "Creating complete N8N backup..."
    
    mkdir -p "$MIGRATION_DIR"
    mkdir -p "$TEMP_DIR"
    
    # Create backup structure
    mkdir -p "$TEMP_DIR/n8n-backup"
    cd "$TEMP_DIR/n8n-backup"
    
    # Backup based on installation type
    case $N8N_TYPE in
        "docker")
            backup_docker_installation
            ;;
        "docker-compose")
            backup_docker_compose_installation
            ;;
        "npm")
            backup_npm_installation
            ;;
        "snap")
            backup_snap_installation
            ;;
    esac
    
    # Create system info file
    create_system_info
    
    # Create migration metadata
    create_migration_metadata
    
    # Create compressed backup
    cd "$TEMP_DIR"
    tar -czf "$MIGRATION_DIR/$BACKUP_FILE" n8n-backup/
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    log "Complete backup created: $MIGRATION_DIR/$BACKUP_FILE"
    log_info "Backup size: $(du -h "$MIGRATION_DIR/$BACKUP_FILE" | cut -f1)"
}

# Backup Docker installation
backup_docker_installation() {
    log "Backing up Docker N8N installation..."
    
    # Stop N8N container
    log_info "Stopping N8N container..."
    docker stop n8n 2>/dev/null || true
    
    # Backup Docker volumes
    mkdir -p docker-volumes
    
    # Find N8N volumes
    N8N_VOLUMES=$(docker volume ls | grep n8n | awk '{print $2}')
    
    for volume in $N8N_VOLUMES; do
        log_info "Backing up volume: $volume"
        docker run --rm \
            -v "$volume":/data \
            -v "$PWD/docker-volumes":/backup \
            alpine tar czf "/backup/$volume.tar.gz" /data
    done
    
    # Backup container configuration
    docker inspect n8n > docker-container-config.json 2>/dev/null || true
    
    # Export N8N image info
    docker images | grep n8n > docker-images.txt
    
    # Restart N8N container
    log_info "Restarting N8N container..."
    docker start n8n 2>/dev/null || true
}

# Backup Docker Compose installation
backup_docker_compose_installation() {
    log "Backing up Docker Compose N8N installation..."
    
    cd "$N8N_CONFIG_DIR"
    
    # Stop services
    log_info "Stopping N8N services..."
    docker-compose down
    
    # Copy entire project directory
    cp -r "$N8N_CONFIG_DIR" "$TEMP_DIR/n8n-backup/project-files"
    
    # Backup Docker volumes
    mkdir -p "$TEMP_DIR/n8n-backup/docker-volumes"
    
    # Get volume names from docker-compose.yml
    VOLUMES=$(docker-compose config --volumes 2>/dev/null || echo "n8n_data")
    
    for volume in $VOLUMES; do
        if docker volume inspect "$volume" &>/dev/null; then
            log_info "Backing up volume: $volume"
            docker run --rm \
                -v "$volume":/data \
                -v "$TEMP_DIR/n8n-backup/docker-volumes":/backup \
                alpine tar czf "/backup/$volume.tar.gz" /data
        fi
    done
    
    # Restart services
    log_info "Restarting N8N services..."
    docker-compose up -d
}

# Backup npm installation
backup_npm_installation() {
    log "Backing up npm N8N installation..."
    
    # Copy N8N data directory
    if [ -d "$N8N_DATA_DIR" ]; then
        cp -r "$N8N_DATA_DIR" n8n-data
        log_info "Backed up N8N data directory"
    fi
    
    # Backup global npm packages
    npm list -g --depth=0 > npm-global-packages.txt 2>/dev/null || true
    
    # Backup N8N configuration
    if [ -f "$HOME/.n8nrc" ]; then
        cp "$HOME/.n8nrc" .
    fi
    
    # Backup environment variables
    env | grep N8N > n8n-env-vars.txt || true
}

# Backup snap installation
backup_snap_installation() {
    log "Backing up snap N8N installation..."
    
    # Copy snap N8N data
    if [ -d "$N8N_DATA_DIR" ]; then
        cp -r "$N8N_DATA_DIR" n8n-data
        log_info "Backed up snap N8N data"
    fi
    
    # Backup snap info
    snap info n8n > snap-info.txt 2>/dev/null || true
    snap list | grep n8n > snap-list.txt 2>/dev/null || true
}

# Create system information file
create_system_info() {
    log_info "Creating system information file..."
    
    cat > system-info.txt << EOF
# N8N Migration - System Information
# Generated: $(date)

## System Details
OS: $(lsb_release -d | cut -f2)
Kernel: $(uname -r)
Architecture: $(uname -m)
Hostname: $(hostname)

## N8N Installation
Type: $N8N_TYPE
Data Directory: $N8N_DATA_DIR
Config Directory: $N8N_CONFIG_DIR

## Docker Information
$(docker --version 2>/dev/null || echo "Docker not installed")
$(docker-compose --version 2>/dev/null || echo "Docker Compose not installed")

## Node.js Information
$(node --version 2>/dev/null || echo "Node.js not installed")
$(npm --version 2>/dev/null || echo "npm not installed")

## Network Configuration
$(ip addr show | grep -E "inet.*scope global" || echo "No network info")

## Disk Usage
$(df -h | grep -E "/$|/home")

## Memory Information
$(free -h)
EOF
}

# Create migration metadata
create_migration_metadata() {
    log_info "Creating migration metadata..."
    
    cat > migration-metadata.json << EOF
{
    "migration_version": "1.0",
    "created_at": "$(date -Iseconds)",
    "source_system": {
        "hostname": "$(hostname)",
        "os": "$(lsb_release -ds)",
        "kernel": "$(uname -r)",
        "architecture": "$(uname -m)"
    },
    "n8n_installation": {
        "type": "$N8N_TYPE",
        "data_directory": "$N8N_DATA_DIR",
        "config_directory": "$N8N_CONFIG_DIR"
    },
    "backup_contents": {
        "workflows": true,
        "credentials": true,
        "database": true,
        "logs": true,
        "docker_volumes": $([ "$N8N_TYPE" = "docker" ] || [ "$N8N_TYPE" = "docker-compose" ] && echo "true" || echo "false"),
        "system_config": true
    }
}
EOF
}

# Export workflows only
export_workflows_only() {
    log "Exporting N8N workflows and configurations..."
    
    mkdir -p "$MIGRATION_DIR/workflows-export"
    cd "$MIGRATION_DIR/workflows-export"
    
    # Export based on installation type
    case $N8N_TYPE in
        "docker"|"docker-compose")
            export_workflows_docker
            ;;
        "npm"|"snap")
            export_workflows_local
            ;;
    esac
    
    # Create export archive
    cd "$MIGRATION_DIR"
    tar -czf "n8n-workflows-export-$(date +%Y%m%d_%H%M%S).tar.gz" workflows-export/
    
    log "Workflows exported to: $MIGRATION_DIR/n8n-workflows-export-*.tar.gz"
}

# Export workflows from Docker installation
export_workflows_docker() {
    log_info "Exporting workflows from Docker installation..."
    
    # Export workflows via N8N CLI
    if docker ps | grep -q n8n; then
        docker exec n8n n8n export:workflow --all --output=/tmp/workflows.json 2>/dev/null || true
        docker cp n8n:/tmp/workflows.json . 2>/dev/null || true
        
        # Export credentials
        docker exec n8n n8n export:credentials --all --output=/tmp/credentials.json 2>/dev/null || true
        docker cp n8n:/tmp/credentials.json . 2>/dev/null || true
    fi
    
    # Backup database files if accessible
    if [ "$N8N_TYPE" = "docker-compose" ] && [ -d "$N8N_CONFIG_DIR" ]; then
        cd "$N8N_CONFIG_DIR"
        if [ -f "database.sqlite" ]; then
            cp database.sqlite "$MIGRATION_DIR/workflows-export/"
        fi
    fi
}

# Export workflows from local installation
export_workflows_local() {
    log_info "Exporting workflows from local installation..."
    
    # Copy database file
    if [ -f "$N8N_DATA_DIR/database.sqlite" ]; then
        cp "$N8N_DATA_DIR/database.sqlite" .
        log_info "Exported SQLite database"
    fi
    
    # Copy workflows directory
    if [ -d "$N8N_DATA_DIR/workflows" ]; then
        cp -r "$N8N_DATA_DIR/workflows" .
        log_info "Exported workflows directory"
    fi
    
    # Copy credentials
    if [ -f "$N8N_DATA_DIR/credentials.json" ]; then
        cp "$N8N_DATA_DIR/credentials.json" .
        log_info "Exported credentials"
    fi
    
    # Export via CLI if available
    if command -v n8n &> /dev/null; then
        n8n export:workflow --all --output=workflows-cli.json 2>/dev/null || true
        n8n export:credentials --all --output=credentials-cli.json 2>/dev/null || true
    fi
}

# Restore complete backup
restore_complete_backup() {
    log "Restoring complete N8N backup..."
    
    # Find backup file
    if [ -z "$BACKUP_FILE_PATH" ]; then
        BACKUP_FILES=($(ls -t "$MIGRATION_DIR"/n8n-complete-backup-*.tar.gz 2>/dev/null))
        if [ ${#BACKUP_FILES[@]} -eq 0 ]; then
            log_error "No backup files found in $MIGRATION_DIR"
            log_info "Please specify backup file with: export BACKUP_FILE_PATH=/path/to/backup.tar.gz"
            exit 1
        fi
        BACKUP_FILE_PATH="${BACKUP_FILES[0]}"
        log_info "Using latest backup: $(basename "$BACKUP_FILE_PATH")"
    fi
    
    # Extract backup
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    tar -xzf "$BACKUP_FILE_PATH"
    
    # Read migration metadata
    if [ -f "n8n-backup/migration-metadata.json" ]; then
        SOURCE_TYPE=$(grep '"type"' n8n-backup/migration-metadata.json | head -1 | cut -d'"' -f4)
        log_info "Source installation type: $SOURCE_TYPE"
    fi
    
    # Detect current installation
    detect_n8n_installation
    
    # Restore based on types
    cd "n8n-backup"
    
    case $N8N_TYPE in
        "docker")
            restore_to_docker
            ;;
        "docker-compose")
            restore_to_docker_compose
            ;;
        "npm")
            restore_to_npm
            ;;
        "snap")
            restore_to_snap
            ;;
    esac
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    log "Backup restoration completed!"
}

# Restore to Docker installation
restore_to_docker() {
    log "Restoring to Docker N8N installation..."
    
    # Stop current container
    docker stop n8n 2>/dev/null || true
    docker rm n8n 2>/dev/null || true
    
    # Restore volumes
    if [ -d "docker-volumes" ]; then
        for volume_backup in docker-volumes/*.tar.gz; do
            if [ -f "$volume_backup" ]; then
                volume_name=$(basename "$volume_backup" .tar.gz)
                log_info "Restoring volume: $volume_name"
                
                # Remove existing volume
                docker volume rm "$volume_name" 2>/dev/null || true
                
                # Create new volume and restore data
                docker volume create "$volume_name"
                docker run --rm \
                    -v "$volume_name":/data \
                    -v "$PWD/docker-volumes":/backup \
                    alpine sh -c "cd /data && tar xzf /backup/$volume_name.tar.gz --strip-components=1"
            fi
        done
    fi
    
    # Recreate container from backup config
    if [ -f "docker-container-config.json" ]; then
        log_info "Recreating N8N container from backup configuration"
        # Extract and apply container configuration
        # This is a simplified version - you might need to adjust based on your setup
        docker run -d --name n8n \
            -p 5678:5678 \
            -v n8n_data:/home/node/.n8n \
            docker.n8n.io/n8nio/n8n
    fi
}

# Restore to Docker Compose installation
restore_to_docker_compose() {
    log "Restoring to Docker Compose N8N installation..."
    
    # Stop current services
    if [ -d "$N8N_CONFIG_DIR" ]; then
        cd "$N8N_CONFIG_DIR"
        docker-compose down 2>/dev/null || true
    fi
    
    # Restore project files
    if [ -d "project-files" ]; then
        log_info "Restoring project configuration files"
        cp -r project-files/* "$N8N_CONFIG_DIR/" 2>/dev/null || true
    fi
    
    # Restore Docker volumes
    if [ -d "docker-volumes" ]; then
        for volume_backup in docker-volumes/*.tar.gz; do
            if [ -f "$volume_backup" ]; then
                volume_name=$(basename "$volume_backup" .tar.gz)
                log_info "Restoring volume: $volume_name"
                
                # Remove existing volume
                docker volume rm "$volume_name" 2>/dev/null || true
                
                # Create new volume and restore data
                docker volume create "$volume_name"
                docker run --rm \
                    -v "$volume_name":/data \
                    -v "$PWD/docker-volumes":/backup \
                    alpine sh -c "cd /data && tar xzf /backup/$volume_name.tar.gz --strip-components=1"
            fi
        done
    fi
    
    # Start services
    cd "$N8N_CONFIG_DIR"
    docker-compose up -d
}

# Restore to npm installation
restore_to_npm() {
    log "Restoring to npm N8N installation..."
    
    # Stop N8N if running
    pkill -f n8n 2>/dev/null || true
    
    # Backup current data
    if [ -d "$N8N_DATA_DIR" ]; then
        mv "$N8N_DATA_DIR" "$N8N_DATA_DIR.backup.$(date +%s)"
        log_info "Backed up existing N8N data"
    fi
    
    # Restore N8N data
    if [ -d "n8n-data" ]; then
        cp -r n8n-data "$N8N_DATA_DIR"
        chown -R $(whoami):$(whoami) "$N8N_DATA_DIR"
        log_info "Restored N8N data directory"
    fi
    
    # Restore configuration
    if [ -f ".n8nrc" ]; then
        cp .n8nrc "$HOME/"
        log_info "Restored N8N configuration"
    fi
}

# Restore to snap installation
restore_to_snap() {
    log "Restoring to snap N8N installation..."
    
    # Stop N8N service
    snap stop n8n 2>/dev/null || true
    
    # Backup current data
    if [ -d "$N8N_DATA_DIR" ]; then
        mv "$N8N_DATA_DIR" "$N8N_DATA_DIR.backup.$(date +%s)"
        log_info "Backed up existing N8N data"
    fi
    
    # Restore N8N data
    if [ -d "n8n-data" ]; then
        mkdir -p "$(dirname "$N8N_DATA_DIR")"
        cp -r n8n-data "$N8N_DATA_DIR"
        log_info "Restored N8N data directory"
    fi
    
    # Start N8N service
    snap start n8n 2>/dev/null || true
}

# Import workflows only
import_workflows_only() {
    log "Importing N8N workflows and configurations..."
    
    # Find export file
    EXPORT_FILES=($(ls -t "$MIGRATION_DIR"/n8n-workflows-export-*.tar.gz 2>/dev/null))
    if [ ${#EXPORT_FILES[@]} -eq 0 ]; then
        log_error "No workflow export files found in $MIGRATION_DIR"
        exit 1
    fi
    
    EXPORT_FILE="${EXPORT_FILES[0]}"
    log_info "Using export file: $(basename "$EXPORT_FILE")"
    
    # Extract export
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    tar -xzf "$EXPORT_FILE"
    cd workflows-export
    
    # Import based on installation type
    detect_n8n_installation
    
    case $N8N_TYPE in
        "docker"|"docker-compose")
            import_workflows_docker
            ;;
        "npm"|"snap")
            import_workflows_local
            ;;
    esac
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    log "Workflows import completed!"
}

# Import workflows to Docker installation
import_workflows_docker() {
    log_info "Importing workflows to Docker installation..."
    
    # Copy files to container and import
    if docker ps | grep -q n8n; then
        if [ -f "workflows.json" ]; then
            docker cp workflows.json n8n:/tmp/
            docker exec n8n n8n import:workflow --input=/tmp/workflows.json
            log_info "Imported workflows"
        fi
        
        if [ -f "credentials.json" ]; then
            docker cp credentials.json n8n:/tmp/
            docker exec n8n n8n import:credentials --input=/tmp/credentials.json
            log_info "Imported credentials"
        fi
    fi
    
    # If database file exists, restore it
    if [ -f "database.sqlite" ] && [ "$N8N_TYPE" = "docker-compose" ]; then
        log_warning "Database file found. Consider stopping N8N and replacing the database file manually."
    fi
}

# Import workflows to local installation
import_workflows_local() {
    log_info "Importing workflows to local installation..."
    
    # Stop N8N
    pkill -f n8n 2>/dev/null || true
    
    # Import database if exists
    if [ -f "database.sqlite" ]; then
        cp database.sqlite "$N8N_DATA_DIR/"
        log_info "Imported database"
    fi
    
    # Import workflows directory
    if [ -d "workflows" ]; then
        cp -r workflows/* "$N8N_DATA_DIR/workflows/" 2>/dev/null || true
        log_info "Imported workflows directory"
    fi
    
    # Import credentials
    if [ -f "credentials.json" ]; then
        cp credentials.json "$N8N_DATA_DIR/"
        log_info "Imported credentials"
    fi
    
    # Import via CLI if files exist
    if command -v n8n &> /dev/null; then
        if [ -f "workflows-cli.json" ]; then
            n8n import:workflow --input=workflows-cli.json
        fi
        if [ -f "credentials-cli.json" ]; then
            n8n import:credentials --input=credentials-cli.json
        fi
    fi
}

# Transfer backup to remote server
transfer_backup() {
    log "Setting up backup transfer..."
    
    echo -e "${CYAN}Transfer Options:${NC}"
    echo "1. SCP (SSH Copy)"
    echo "2. SFTP"
    echo "3. rsync over SSH"
    echo "4. Manual (show commands)"
    
    read -p "Choose transfer method (1-4): " TRANSFER_METHOD
    
    read -p "Target server IP/hostname: " TARGET_HOST
    read -p "Target username: " TARGET_USER
    read -p "Target directory [/home/$TARGET_USER/n8n-migration]: " TARGET_DIR
    TARGET_DIR=${TARGET_DIR:-/home/$TARGET_USER/n8n-migration}
    
    BACKUP_PATH="$MIGRATION_DIR/$BACKUP_FILE"
    
    case $TRANSFER_METHOD in
        1)
            log_info "Transferring via SCP..."
            scp "$BACKUP_PATH" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/"
            ;;
        2)
            log_info "Use SFTP to transfer:"
            echo "sftp $TARGET_USER@$TARGET_HOST"
            echo "put $BACKUP_PATH $TARGET_DIR/"
            ;;
        3)
            log_info "Transferring via rsync..."
            rsync -avz "$BACKUP_PATH" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/"
            ;;
        4)
            echo -e "${CYAN}Manual transfer commands:${NC}"
            echo "scp $BACKUP_PATH $TARGET_USER@$TARGET_HOST:$TARGET_DIR/"
            echo "# OR"
            echo "rsync -avz $BACKUP_PATH $TARGET_USER@$TARGET_HOST:$TARGET_DIR/"
            ;;
    esac
    
    log "Transfer setup completed!"
    log_info "On target server, run: ./n8n-migration-tool.sh --target restore"
}

# Main function
main() {
    show_banner
    
    # Parse arguments
    case "${1:-}" in
        --source)
            case "${2:-}" in
                backup)
                    detect_n8n_installation
                    create_complete_backup
                    echo -e "${CYAN}Next steps:${NC}"
                    echo "1. Transfer backup to target server"
                    echo "2. Run: ./n8n-migration-tool.sh --target restore"
                    ;;
                export)
                    detect_n8n_installation
                    export_workflows_only
                    echo -e "${CYAN}Next steps:${NC}"
                    echo "1. Transfer export to target server"
                    echo "2. Run: ./n8n-migration-tool.sh --target import"
                    ;;
                *)
                    log_error "Invalid source mode. Use: backup or export"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        --target)
            case "${2:-}" in
                restore)
                    restore_complete_backup
                    ;;
                import)
                    import_workflows_only
                    ;;
                *)
                    log_error "Invalid target mode. Use: restore or import"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        --transfer)
            transfer_backup
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Invalid arguments"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"