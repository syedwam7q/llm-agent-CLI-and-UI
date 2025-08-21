#!/bin/bash

# 🤖 LLM Agent v2.0.0 - Setup Script
# Created by: Syed Wamiq (https://github.com/syedwam7q)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="ℹ️"
ROBOT="🤖"

echo -e "${PURPLE}${ROBOT} LLM Agent v2.0.0 - Setup Script${NC}"
echo -e "${CYAN}Created by: Syed Wamiq (https://github.com/syedwam7q)${NC}"
echo "=================================================="
echo

# Function to print colored output
print_status() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

print_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

# Check if Python 3.8+ is installed
check_python() {
    print_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Python $PYTHON_VERSION found"
            PYTHON_CMD="python"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    print_status "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_info "Upgrading pip..."
    pip install --upgrade pip
    print_status "Pip upgraded"
}

# Install requirements
install_requirements() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p data/uploads
    mkdir -p logs
    
    # Create .gitkeep files
    touch data/uploads/.gitkeep
    touch logs/.gitkeep
    
    print_status "Directories created"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Environment file created from template"
            print_warning "Please edit .env file with your API keys before running the application"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    if $PYTHON_CMD -c "import src.main" 2>/dev/null; then
        print_status "Installation test passed"
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Make scripts executable
make_scripts_executable() {
    print_info "Making scripts executable..."
    
    chmod +x run_chat.sh 2>/dev/null || true
    chmod +x start_modern_ui.sh 2>/dev/null || true
    chmod +x setup.sh 2>/dev/null || true
    
    print_status "Scripts made executable"
}

# Print final instructions
print_final_instructions() {
    echo
    echo "=================================================="
    echo -e "${GREEN}${ROCKET} Setup completed successfully!${NC}"
    echo "=================================================="
    echo
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "${YELLOW}1.${NC} Edit the .env file with your API keys:"
    echo -e "   ${BLUE}nano .env${NC}"
    echo
    echo -e "${YELLOW}2.${NC} Required API keys:"
    echo -e "   ${BLUE}OPENAI_API_KEY${NC} - Get from https://platform.openai.com/api-keys"
    echo -e "   ${BLUE}TAVILY_API_KEY${NC} - Optional, get from https://tavily.com/"
    echo
    echo -e "${YELLOW}3.${NC} Start the application:"
    echo -e "   ${GREEN}# Modern Web Interface (Recommended)${NC}"
    echo -e "   ${BLUE}./start_modern_ui.sh${NC}"
    echo
    echo -e "   ${GREEN}# Traditional CLI${NC}"
    echo -e "   ${BLUE}./run_chat.sh${NC}"
    echo
    echo -e "   ${GREEN}# Manual activation${NC}"
    echo -e "   ${BLUE}source venv/bin/activate${NC}"
    echo -e "   ${BLUE}python src/main.py chat --web-ui${NC}  # Web interface"
    echo -e "   ${BLUE}python src/main.py chat${NC}           # CLI interface"
    echo
    echo -e "${YELLOW}4.${NC} Access the Modern Web Interface:"
    echo -e "   ${BLUE}http://localhost:8000${NC}"
    echo
    echo -e "${CYAN}For help and documentation:${NC}"
    echo -e "   ${BLUE}python src/main.py --help${NC}"
    echo -e "   ${BLUE}python src/main.py tools${NC}  # List available tools"
    echo
    echo -e "${PURPLE}Created by: Syed Wamiq (https://github.com/syedwam7q)${NC}"
    echo
}

# Main execution
main() {
    echo -e "${ROCKET} Starting LLM Agent setup..."
    echo
    
    check_python
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    create_directories
    setup_env
    make_scripts_executable
    test_installation
    
    print_final_instructions
}

# Run main function
main "$@"