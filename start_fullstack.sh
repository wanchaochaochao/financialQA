#!/bin/bash

# Financial QA System - Full Stack Startup Script
# ================================================

echo "============================================================"
echo "🏦 金融资产问答系统 - 完整启动脚本"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda 未安装${NC}"
    echo "请先安装 Miniconda 或 Anaconda"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "请先安装 Node.js (推荐 v18+)"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📝 加载配置文件 .env"
    export $(grep -v '^#' .env | xargs)
    echo ""
fi

# Get port configuration
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

# Step 1: Activate conda environment and start backend
echo "📍 Step 1: 启动 Python FastAPI 后端..."
echo ""

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate financial

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 无法激活 financial 环境${NC}"
    echo "请先创建环境: conda create -n financial python=3.10"
    exit 1
fi

echo -e "${GREEN}✅ Conda 环境已激活: financial${NC}"

# Start backend in background
echo "🚀 启动 FastAPI 服务..."
python start_api.py --dev > /tmp/fastapi.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ FastAPI 后端已启动 (PID: $BACKEND_PID)${NC}"
    echo "   📖 API Documentation: http://localhost:$API_PORT/docs"
else
    echo -e "${RED}❌ FastAPI 启动失败${NC}"
    echo "请检查日志: cat /tmp/fastapi.log"
    exit 1
fi

echo ""

# Step 2: Start frontend
echo "📍 Step 2: 启动 Next.js 前端..."
echo ""

cd web-app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 安装 npm 依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ npm install 失败${NC}"
        kill $BACKEND_PID
        exit 1
    fi
fi

echo "🚀 启动 Next.js 开发服务器..."
PORT=$FRONTEND_PORT npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Next.js 前端已启动 (PID: $FRONTEND_PID)${NC}"
    echo "   🌐 访问: http://localhost:$FRONTEND_PORT"
else
    echo -e "${RED}❌ Next.js 启动失败${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "============================================================"
echo -e "${GREEN}🎉 系统启动成功！${NC}"
echo "============================================================"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:$FRONTEND_PORT"
echo "   后端: http://localhost:$API_PORT/docs"
echo ""
echo "📍 进程ID:"
echo "   后端 PID: $BACKEND_PID"
echo "   前端 PID: $FRONTEND_PID"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "============================================================"
echo ""

# Trap Ctrl+C
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

# Wait for processes
wait
