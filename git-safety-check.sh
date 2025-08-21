#!/bin/bash

# 🔒 Git Safety Check Script for LLM Agent
# Created by: Syed Wamiq (https://github.com/syedwam7q)
# 
# This script checks for sensitive files before Git operations

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔒 Git Safety Check for LLM Agent${NC}"
echo "=================================="

# Check if .env file exists and contains real API keys
check_env_file() {
    if [ -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Found .env file${NC}"
        
        # Check if it contains real API keys (not placeholder values)
        if grep -q "your_.*_key_here" .env; then
            echo -e "${GREEN}✅ .env contains placeholder values (safe)${NC}"
        else
            echo -e "${RED}❌ DANGER: .env contains real API keys!${NC}"
            echo -e "${RED}   This file should NOT be committed to Git${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✅ No .env file found${NC}"
    fi
    return 0
}

# Check if .gitignore properly excludes sensitive files
check_gitignore() {
    if [ -f ".gitignore" ]; then
        echo -e "${BLUE}ℹ️  Checking .gitignore...${NC}"
        
        # Check for essential entries
        local missing_entries=()
        
        if ! grep -q "^\.env$" .gitignore; then
            missing_entries+=(".env")
        fi
        
        if ! grep -q "venv/" .gitignore; then
            missing_entries+=("venv/")
        fi
        
        if ! grep -q "\*\.db$" .gitignore; then
            missing_entries+=("*.db")
        fi
        
        if [ ${#missing_entries[@]} -eq 0 ]; then
            echo -e "${GREEN}✅ .gitignore properly configured${NC}"
        else
            echo -e "${YELLOW}⚠️  Missing entries in .gitignore:${NC}"
            for entry in "${missing_entries[@]}"; do
                echo -e "${YELLOW}   - $entry${NC}"
            done
        fi
    else
        echo -e "${RED}❌ No .gitignore file found${NC}"
        return 1
    fi
    return 0
}

# Check for database files
check_database_files() {
    local db_files=$(find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" 2>/dev/null)
    if [ -n "$db_files" ]; then
        echo -e "${YELLOW}⚠️  Found database files:${NC}"
        echo "$db_files" | while read -r file; do
            echo -e "${YELLOW}   - $file${NC}"
        done
        echo -e "${YELLOW}   These should be in .gitignore${NC}"
    else
        echo -e "${GREEN}✅ No database files found${NC}"
    fi
}

# Check for uploaded files
check_uploaded_files() {
    if [ -d "data/uploads" ]; then
        local upload_count=$(find data/uploads -type f ! -name ".gitkeep" | wc -l)
        if [ "$upload_count" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Found $upload_count uploaded files in data/uploads/${NC}"
            echo -e "${YELLOW}   These should be in .gitignore${NC}"
        else
            echo -e "${GREEN}✅ No uploaded files found${NC}"
        fi
    fi
}

# Check for Python cache files
check_python_cache() {
    local cache_dirs=$(find . -name "__pycache__" -type d 2>/dev/null)
    if [ -n "$cache_dirs" ]; then
        echo -e "${YELLOW}⚠️  Found Python cache directories:${NC}"
        echo "$cache_dirs" | while read -r dir; do
            echo -e "${YELLOW}   - $dir${NC}"
        done
        echo -e "${YELLOW}   These should be cleaned up${NC}"
    else
        echo -e "${GREEN}✅ No Python cache directories found${NC}"
    fi
}

# Check what would be committed
check_git_status() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${BLUE}ℹ️  Git status:${NC}"
        git status --porcelain | while read -r line; do
            echo -e "${BLUE}   $line${NC}"
        done
    else
        echo -e "${YELLOW}⚠️  Not in a Git repository${NC}"
    fi
}

# Main safety check
main() {
    local errors=0
    
    echo
    check_env_file || ((errors++))
    echo
    check_gitignore || ((errors++))
    echo
    check_database_files
    echo
    check_uploaded_files
    echo
    check_python_cache
    echo
    check_git_status
    echo
    
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}🎉 All safety checks passed!${NC}"
        echo -e "${GREEN}✅ Safe to proceed with Git operations${NC}"
        return 0
    else
        echo -e "${RED}❌ Safety check failed!${NC}"
        echo -e "${RED}🚨 DO NOT commit until issues are resolved${NC}"
        echo
        echo -e "${YELLOW}To fix issues:${NC}"
        echo -e "${YELLOW}1. Remove or secure sensitive files${NC}"
        echo -e "${YELLOW}2. Update .gitignore if needed${NC}"
        echo -e "${YELLOW}3. Clean up cache files: find . -name '__pycache__' -exec rm -rf {} +${NC}"
        echo -e "${YELLOW}4. Run this script again${NC}"
        return 1
    fi
}

# Run the safety check
main "$@"