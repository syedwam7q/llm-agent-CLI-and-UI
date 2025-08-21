#!/bin/bash

# 🤖 LLM Agent v2.0.0 - Modern Web UI Startup Script
# Created by: Syed Wamiq (https://github.com/syedwam7q)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🤖 LLM Agent v2.0.0 - Modern Web UI${NC}"
echo -e "${CYAN}Created by: Syed Wamiq (https://github.com/syedwam7q)${NC}"
echo "=============================================="

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

# Start the modern web UI
echo -e "${GREEN}🚀 Starting modern web UI...${NC}"
echo -e "${CYAN}🌐 Open your browser to: http://localhost:8000${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

python src/main.py chat --web-ui

echo ""
echo -e "${GREEN}👋 Modern web UI stopped. Goodbye!${NC}"