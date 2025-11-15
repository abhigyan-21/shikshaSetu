#!/bin/bash
# Quick Start Script for Multilingual Education Content Pipeline
# This script helps you get started quickly with Docker

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Multilingual Education Content Pipeline - Quick Start    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Please edit .env and add your API keys:${NC}"
    echo "   - HUGGINGFACE_API_KEY (required)"
    echo "   - BHASHINI_API_KEY (optional)"
    echo "   - Update POSTGRES_PASSWORD and FLASK_SECRET_KEY for production"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Create necessary directories
echo ""
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p data/audio data/cache data/curriculum logs backups
echo -e "${GREEN}✓ Directories created${NC}"

# Ask user which mode to run
echo ""
echo -e "${BLUE}Select mode:${NC}"
echo "  1) Development (with hot-reload)"
echo "  2) Production"
echo "  3) Development with PgAdmin"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Starting in development mode...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        ;;
    2)
        echo ""
        echo -e "${BLUE}Starting in production mode...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        ;;
    3)
        echo ""
        echo -e "${BLUE}Starting in development mode with PgAdmin...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile admin up -d
        ;;
    *)
        echo ""
        echo -e "${BLUE}Starting in default mode...${NC}"
        docker-compose up -d
        ;;
esac

# Wait for services to be ready
echo ""
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Check health
echo ""
echo -e "${BLUE}Checking service health...${NC}"
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Flask API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Flask