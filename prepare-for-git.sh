#!/bin/bash

# 🚀 Prepare LLM Agent for Git Repository
# Created by: Syed Wamiq (https://github.com/syedwam7q)
# 
# This script prepares the project for safe Git operations

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Preparing LLM Agent for Git Repository${NC}"
echo -e "${CYAN}Created by: Syed Wamiq (https://github.com/syedwam7q)${NC}"
echo "=============================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Clean up Python cache files
cleanup_python_cache() {
    print_info "Cleaning up Python cache files..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    print_status "Python cache cleaned"
}

# Clean up database files
cleanup_databases() {
    print_info "Cleaning up database files..."
    rm -f data/memory.db data/sessions.db 2>/dev/null || true
    print_status "Database files cleaned"
}

# Clean up uploaded files (keep .gitkeep)
cleanup_uploads() {
    print_info "Cleaning up uploaded files..."
    if [ -d "data/uploads" ]; then
        find data/uploads -type f ! -name ".gitkeep" -delete 2>/dev/null || true
    fi
    print_status "Upload directory cleaned"
}

# Clean up log files
cleanup_logs() {
    print_info "Cleaning up log files..."
    if [ -d "logs" ]; then
        find logs -name "*.log" -delete 2>/dev/null || true
    fi
    print_status "Log files cleaned"
}

# Ensure .env is not present (only .env.example should exist)
check_env_file() {
    print_info "Checking environment files..."
    if [ -f ".env" ]; then
        if grep -q "your_.*_key_here" .env; then
            print_status ".env contains only placeholder values"
        else
            print_warning ".env contains real API keys - removing for safety"
            rm -f .env
            print_status ".env removed (will be recreated from .env.example during setup)"
        fi
    else
        print_status "No .env file found (good for Git safety)"
    fi
}

# Ensure necessary directories exist with .gitkeep
ensure_directories() {
    print_info "Ensuring necessary directories exist..."
    
    mkdir -p data/uploads logs
    
    # Create .gitkeep files
    touch data/uploads/.gitkeep
    touch logs/.gitkeep
    
    print_status "Directory structure verified"
}

# Make scripts executable
make_scripts_executable() {
    print_info "Making scripts executable..."
    chmod +x setup.sh 2>/dev/null || true
    chmod +x start_modern_ui.sh 2>/dev/null || true
    chmod +x run_chat.sh 2>/dev/null || true
    chmod +x git-safety-check.sh 2>/dev/null || true
    chmod +x prepare-for-git.sh 2>/dev/null || true
    print_status "Scripts made executable"
}

# Run safety check
run_safety_check() {
    print_info "Running Git safety check..."
    if [ -f "git-safety-check.sh" ]; then
        ./git-safety-check.sh
    else
        print_warning "git-safety-check.sh not found"
    fi
}

# Show Git status
show_git_status() {
    print_info "Current Git status:"
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git status
    else
        print_warning "Not in a Git repository yet"
        echo
        echo -e "${CYAN}To initialize Git repository:${NC}"
        echo -e "${BLUE}git init${NC}"
        echo -e "${BLUE}git add .${NC}"
        echo -e "${BLUE}git commit -m 'Initial commit: LLM Agent v2.0.0'${NC}"
        echo -e "${BLUE}git branch -M main${NC}"
        echo -e "${BLUE}git remote add origin https://github.com/syedwam7q/llm-agent.git${NC}"
        echo -e "${BLUE}git push -u origin main${NC}"
    fi
}

# Main execution
main() {
    echo
    cleanup_python_cache
    echo
    cleanup_databases
    echo
    cleanup_uploads
    echo
    cleanup_logs
    echo
    check_env_file
    echo
    ensure_directories
    echo
    make_scripts_executable
    echo
    run_safety_check
    echo
    show_git_status
    echo
    
    echo -e "${GREEN}🎉 Project prepared for Git!${NC}"
    echo
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "${YELLOW}1.${NC} Review the safety check results above"
    echo -e "${YELLOW}2.${NC} If all checks pass, you can safely commit to Git"
    echo -e "${YELLOW}3.${NC} Users will run './setup.sh' to install dependencies"
    echo -e "${YELLOW}4.${NC} Users will configure their own .env file with API keys"
    echo
    echo -e "${PURPLE}Repository: https://github.com/syedwam7q/llm-agent${NC}"
}

# Run main function
main "$@"