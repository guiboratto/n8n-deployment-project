#!/bin/bash

# N8N Deployment Script
# =====================
# 
# This script automates the complete deployment process for the N8N project
# including file reading, Git operations, and N8N setup.
#
# Usage:
#   ./deploy.sh [options]
#
# Options:
#   --help, -h          Show this help message
#   --config, -c        Specify config file (default: config/config.yaml)
#   --git-remote, -r    Git remote repository URL
#   --read-only         Only read files, do not deploy
#   --setup-n8n         Only setup N8N environment
#   --git-only          Only perform Git operations
#   --verbose, -v       Enable verbose output
#   --dry-run           Show what would be done without executing
#   --force             Force deployment even if checks fail
#   --backup            Create backup before deployment
#   --no-docker         Skip Docker-based N8N setup
#   --ssl               Enable SSL/TLS configuration
#   --database TYPE     Database type (sqlite, postgres, mysql)

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CONFIG_FILE="$PROJECT_ROOT/config/config.yaml"
LOG_FILE="$PROJECT_ROOT/logs/deploy.log"
PYTHON_SCRIPT="$PROJECT_ROOT/scripts/script.py"

# Default options
VERBOSE=false
DRY_RUN=false
FORCE=false
BACKUP=false
NO_DOCKER=false
SSL_ENABLED=false
DATABASE_TYPE="sqlite"
GIT_REMOTE=""
MODE="full"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    echo "[ERROR] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
    echo "[WARNING] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[INFO] $1${NC}"
        echo "[INFO] $1" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

# Help function
show_help() {
    cat << EOF
N8N Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -c, --config FILE       Configuration file (default: config/config.yaml)
    -r, --git-remote URL    Git remote repository URL
    -v, --verbose           Enable verbose output
    --read-only             Only read files, do not deploy
    --setup-n8n             Only setup N8N environment
    --git-only              Only perform Git operations
    --dry-run               Show what would be done without executing
    --force                 Force deployment even if checks fail
    --backup                Create backup before deployment
    --no-docker             Skip Docker-based N8N setup
    --ssl                   Enable SSL/TLS configuration
    --database TYPE         Database type: sqlite, postgres, mysql

EXAMPLES:
    # Full deployment
    $0

    # Deploy with custom Git remote
    $0 --git-remote https://github.com/user/repo.git

    # Only read files and analyze
    $0 --read-only

    # Setup N8N with PostgreSQL and SSL
    $0 --setup-n8n --database postgres --ssl

    # Git operations only
    $0 --git-only --git-remote https://github.com/user/repo.git

    # Dry run to see what would happen
    $0 --dry-run --verbose

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -r|--git-remote)
                GIT_REMOTE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --read-only)
                MODE="read-only"
                shift
                ;;
            --setup-n8n)
                MODE="setup-n8n"
                shift
                ;;
            --git-only)
                MODE="git-only"
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --backup)
                BACKUP=true
                shift
                ;;
            --no-docker)
                NO_DOCKER=true
                shift
                ;;
            --ssl)
                SSL_ENABLED=true
                shift
                ;;
            --database)
                DATABASE_TYPE="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    local errors=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        errors=$((errors + 1))
    else
        log_info "Python 3 found: $(python3 --version)"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        errors=$((errors + 1))
    else
        log_info "Git found: $(git --version)"
    fi
    
    # Check Docker (if needed)
    if [ "$NO_DOCKER" = false ] && [ "$MODE" != "read-only" ] && [ "$MODE" != "git-only" ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker is not installed"
            errors=$((errors + 1))
        else
            log_info "Docker found: $(docker --version)"
            
            # Check if Docker daemon is running
            if ! docker info &> /dev/null; then
                log_error "Docker daemon is not running"
                errors=$((errors + 1))
            fi
        fi
        
        # Check Docker Compose
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            log_error "Docker Compose is not installed"
            errors=$((errors + 1))
        else
            log_info "Docker Compose found"
        fi
    fi
    
    # Check config file
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warning "Config file not found: $CONFIG_FILE"
        log_info "Will use default configuration"
    else
        log_info "Config file found: $CONFIG_FILE"
    fi
    
    # Check Python script
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_error "Main Python script not found: $PYTHON_SCRIPT"
        errors=$((errors + 1))
    fi
    
    if [ $errors -gt 0 ] && [ "$FORCE" = false ]; then
        log_error "Prerequisites check failed with $errors errors"
        log_error "Use --force to ignore these errors"
        exit 1
    elif [ $errors -gt 0 ]; then
        log_warning "Prerequisites check failed with $errors errors, but continuing due to --force"
    else
        log "Prerequisites check passed"
    fi
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/backups"
    mkdir -p "$PROJECT_ROOT/local-files"
    
    # Create log file
    touch "$LOG_FILE"
    
    # Install Python dependencies if requirements.txt exists
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        if [ "$DRY_RUN" = false ]; then
            python3 -m pip install -r "$PROJECT_ROOT/requirements.txt" --quiet || {
                log_warning "Failed to install some Python dependencies"
            }
        else
            log_info "[DRY RUN] Would install Python dependencies"
        fi
    fi
    
    log "Environment setup completed"
}

# Create backup
create_backup() {
    if [ "$BACKUP" = true ]; then
        log "Creating backup..."
        
        local backup_dir="$PROJECT_ROOT/backups"
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="$backup_dir/deployment-backup-$timestamp.tar.gz"
        
        if [ "$DRY_RUN" = false ]; then
            tar -czf "$backup_file" \
                --exclude="backups" \
                --exclude="logs" \
                --exclude="*.log" \
                --exclude=".git" \
                -C "$PROJECT_ROOT" . || {
                log_warning "Backup creation failed"
                return 1
            }
            log "Backup created: $backup_file"
        else
            log_info "[DRY RUN] Would create backup: $backup_file"
        fi
    fi
}

# Build Python command
build_python_command() {
    local cmd="python3 $PYTHON_SCRIPT"
    
    # Add config file
    if [ -f "$CONFIG_FILE" ]; then
        cmd="$cmd --config $CONFIG_FILE"
    fi
    
    # Add Git remote if specified
    if [ -n "$GIT_REMOTE" ]; then
        cmd="$cmd --git-remote $GIT_REMOTE"
    fi
    
    # Add mode-specific flags
    case $MODE in
        "read-only")
            cmd="$cmd --read-only"
            ;;
        "setup-n8n")
            cmd="$cmd --setup-n8n"
            ;;
        "git-only")
            cmd="$cmd --git-only"
            ;;
    esac
    
    echo "$cmd"
}

# Execute deployment
execute_deployment() {
    log "Starting deployment process..."
    
    local python_cmd=$(build_python_command)
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would execute: $python_cmd"
        return 0
    fi
    
    log_info "Executing: $python_cmd"
    
    # Execute the Python script
    if eval "$python_cmd"; then
        log "Deployment completed successfully!"
        return 0
    else
        log_error "Deployment failed!"
        return 1
    fi
}

# Post-deployment actions
post_deployment() {
    if [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    log "Running post-deployment actions..."
    
    # Display deployment information
    if [ "$MODE" = "full" ] || [ "$MODE" = "setup-n8n" ]; then
        echo
        echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║                    🎉 DEPLOYMENT SUCCESSFUL! 🎉              ║${NC}"
        echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
        echo -e "${CYAN}║                                                              ║${NC}"
        echo -e "${CYAN}║  N8N Web Interface: ${GREEN}http://localhost:5678${CYAN}                  ║${NC}"
        echo -e "${CYAN}║  Project Directory: ${GREEN}$PROJECT_ROOT${CYAN}${NC}"
        echo -e "${CYAN}║  Log File:          ${GREEN}$LOG_FILE${CYAN}${NC}"
        echo -e "${CYAN}║                                                              ║${NC}"
        echo -e "${CYAN}║  Next Steps:                                                 ║${NC}"
        echo -e "${CYAN}║  1. Open N8N in your browser                                ║${NC}"
        echo -e "${CYAN}║  2. Create your first workflow                              ║${NC}"
        echo -e "${CYAN}║  3. Check the documentation in docs/                       ║${NC}"
        echo -e "${CYAN}║                                                              ║${NC}"
        echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo
    fi
    
    # Show deployment report if it exists
    if [ -f "$PROJECT_ROOT/deployment_report.md" ]; then
        log_info "Deployment report generated: deployment_report.md"
    fi
}

# Cleanup function
cleanup() {
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            echo
            echo -e "${RED}Recent log entries:${NC}"
            tail -n 10 "$LOG_FILE" 2>/dev/null || true
        fi
    fi
    
    exit $exit_code
}

# Main function
main() {
    # Set up error handling
    trap cleanup EXIT
    
    # Parse arguments
    parse_args "$@"
    
    # Show banner
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  N8N Deployment Script                      ║"
    echo "║                                                              ║"
    echo "║  Automated deployment for N8N workflow automation           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Show configuration
    log "Starting N8N deployment..."
    log_info "Mode: $MODE"
    log_info "Config file: $CONFIG_FILE"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Verbose: $VERBOSE"
    log_info "Dry run: $DRY_RUN"
    log_info "Force: $FORCE"
    log_info "Backup: $BACKUP"
    
    if [ -n "$GIT_REMOTE" ]; then
        log_info "Git remote: $GIT_REMOTE"
    fi
    
    # Execute deployment steps
    check_prerequisites
    setup_environment
    create_backup
    execute_deployment
    post_deployment
    
    log "All deployment steps completed successfully!"
}

# Run main function with all arguments
main "$@"