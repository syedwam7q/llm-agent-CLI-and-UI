#!/bin/bash

# 🤖 LLM Agent v2.0.0 - CLI Chat Launcher
# Created by: Syed Wamiq (https://github.com/syedwam7q)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🤖 LLM Agent v2.0.0 - CLI Chat Interface${NC}"
echo -e "${CYAN}Created by: Syed Wamiq (https://github.com/syedwam7q)${NC}"
echo "=============================================="

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found.${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your API keys before continuing${NC}"
        echo -e "${BLUE}Required: OPENAI_API_KEY${NC}"
        echo -e "${BLUE}Optional: TAVILY_API_KEY${NC}"
        echo ""
        read -p "Press Enter after you've configured your .env file..."
    else
        echo -e "${RED}❌ .env.example not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Start the chat interface
echo -e "${GREEN}🚀 Starting LLM Agent CLI Chat Interface...${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to exit${NC}"
echo -e "${CYAN}💬 Type '/help' for available commands${NC}"
echo ""

python src/main.py chat