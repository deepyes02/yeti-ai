#!/bin/bash

# Yeti AI Agent - Complete Environment Reset Script
# This script performs a full clean restart of the development environment

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/env"
VENV_STATUS_FILE="$PROJECT_ROOT/.venv_status"
AI_SERVER_SCRIPT="$PROJECT_ROOT/run_ai_server.sh"

echo "🔥 Yeti Flush - Complete Environment Reset"
echo "=========================================="
echo ""

# Step 1: Shutdown and clean Docker containers and volumes
echo "📦 Step 1/5: Shutting down Docker containers and cleaning volumes..."
docker compose down -v
echo "✅ Containers stopped and volumes cleaned"
echo ""

# Step 2: Start Docker containers in detached mode
echo "🚀 Step 2/5: Starting Docker containers in detached mode..."
docker compose up -d
echo "✅ Containers started"
echo ""

# Step 3: Check virtual environment status
echo "🐍 Step 3/4: Checking virtual environment..."
if [ -d "$VENV_PATH" ]; then
    # Check if we're currently in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "✅ Virtual environment is ACTIVE: $VIRTUAL_ENV"
        echo "ACTIVE:$VIRTUAL_ENV:$(date +%s)" > "$VENV_STATUS_FILE"
    else
        echo "⚠️  Virtual environment exists but is NOT ACTIVE"
        echo "💡 To activate: source ./env/bin/activate"
        echo "INACTIVE:$VENV_PATH:$(date +%s)" > "$VENV_STATUS_FILE"
    fi
else
    echo "❌ Virtual environment NOT FOUND at: $VENV_PATH"
    echo "💡 To create: python -m venv env && source ./env/bin/activate && pip install -r requirements.txt"
    echo "MISSING::$(date +%s)" > "$VENV_STATUS_FILE"
fi
echo ""

# Step 4: Summary
echo "✨ Step 4/4: Environment Status Summary"
echo "=========================================="
docker compose ps
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8000"
echo "🗄️  Database: postgresql://localhost:5432"
echo "🤖 AI Server: http://localhost:8080"
echo ""
echo "🎉 Yeti is ready to rumble!"
echo ""
echo "⚠️  NOTE: Make sure llama-server is running at OS level!"
echo "   Start manually: ./run_ai_server.sh"
echo ""
echo "📊 Quick commands:"
echo "  - View backend logs:  docker logs -f backend"
echo "  - View frontend logs: docker logs -f frontend"
echo "  - Stop Docker:        docker compose down"
