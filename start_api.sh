#!/bin/bash

# Financial QA System - API Service Startup Script
# =================================================

echo "============================================================"
echo "🏦 Financial Asset QA System - API Service"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ] || [ -d "env" ] || [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment detected"
else
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider creating one: python -m venv venv"
    echo ""
fi

# Check if dependencies are installed
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastAPI not installed"
    echo "   Please run: pip install -r requirements.txt"
    exit 1
fi

echo "📦 Dependencies OK"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📝 Loading configuration from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Parse arguments (environment variables can be overridden by command line)
DEV_MODE=false
PORT=${API_PORT:-8000}
HOST=${API_HOST:-"0.0.0.0"}

for arg in "$@"
do
    case $arg in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --port=*)
            PORT="${arg#*=}"
            shift
            ;;
        --host=*)
            HOST="${arg#*=}"
            shift
            ;;
    esac
done

echo "📍 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Mode: $([ "$DEV_MODE" = true ] && echo 'Development (auto-reload)' || echo 'Production')"
echo ""

echo "🚀 Starting API server..."
echo ""
echo "📖 API Documentation: http://localhost:$PORT/docs"
echo "📚 ReDoc: http://localhost:$PORT/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Start server
if [ "$DEV_MODE" = true ]; then
    # Development mode with auto-reload
    uvicorn ai_agent.api:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --log-level info
else
    # Production mode
    uvicorn ai_agent.api:app \
        --host "$HOST" \
        --port "$PORT" \
        --log-level info
fi
