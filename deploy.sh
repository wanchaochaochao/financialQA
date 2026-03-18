#!/bin/bash

# ==========================================
# 金融资产问答系统 - 云服务器部署脚本
# ==========================================
#
# 使用方法：
# 1. chmod +x deploy.sh
# 2. ./deploy.sh
#
# 环境要求：
# - Ubuntu 20.04+ / CentOS 8+
# - Python 3.10+
# - Node.js 18+
# - Nginx
# - Conda (可选，用于 Python 环境管理)
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "金融资产问答系统 - 云服务器部署"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# ==========================================
# 1. 检查环境
# ==========================================
echo -e "\n${YELLOW}[步骤 1/7] 检查环境...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 版本: $(python3 --version)${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js 版本: $(node --version)${NC}"

# 检查 Nginx
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}错误: 未找到 Nginx，请先安装 Nginx${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Nginx 版本: $(nginx -v 2>&1 | cut -d'/' -f2)${NC}"

# ==========================================
# 2. 配置环境变量
# ==========================================
echo -e "\n${YELLOW}[步骤 2/7] 配置环境变量...${NC}"

# 检查 .env 文件
if [ ! -f "web-app/.env.local" ]; then
    echo -e "${YELLOW}警告: 未找到 .env.local 文件，从示例复制...${NC}"
    cp web-app/.env.example web-app/.env.local
fi

# 提示用户配置环境变量
echo -e "${YELLOW}请确保已正确配置以下环境变量：${NC}"
echo -e "  - web-app/.env.local 中的 ${GREEN}NEXT_PUBLIC_PYTHON_API_URL${NC}"
echo -e "  - 推荐设置为空字符串（使用 Nginx 反向代理）"
echo ""
read -p "是否已配置环境变量？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}请先配置环境变量后再运行此脚本${NC}"
    exit 1
fi

# ==========================================
# 3. 安装 Python 依赖
# ==========================================
echo -e "\n${YELLOW}[步骤 3/7] 安装 Python 依赖...${NC}"

# 检查是否使用 conda
if command -v conda &> /dev/null; then
    echo -e "${GREEN}检测到 Conda，使用 financial 环境${NC}"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate financial || {
        echo -e "${YELLOW}未找到 financial 环境，正在创建...${NC}"
        conda create -n financial python=3.10 -y
        conda activate financial
    }
    pip install -r requirements.txt
else
    echo -e "${YELLOW}未检测到 Conda，使用系统 Python${NC}"
    pip3 install -r requirements.txt
fi

echo -e "${GREEN}✓ Python 依赖安装完成${NC}"

# ==========================================
# 4. 安装前端依赖并构建
# ==========================================
echo -e "\n${YELLOW}[步骤 4/7] 安装前端依赖并构建...${NC}"

cd web-app

# 安装依赖
echo "正在安装 npm 依赖..."
npm install

# 构建生产版本
echo "正在构建生产版本..."
npm run build

echo -e "${GREEN}✓ 前端构建完成${NC}"

cd ..

# ==========================================
# 5. 配置 Nginx
# ==========================================
echo -e "\n${YELLOW}[步骤 5/7] 配置 Nginx...${NC}"

NGINX_CONFIG="/etc/nginx/sites-available/financial-qa"
NGINX_ENABLED="/etc/nginx/sites-enabled/financial-qa"

# 复制 Nginx 配置
sudo cp nginx.conf "$NGINX_CONFIG"

# 创建软链接
if [ -f "$NGINX_ENABLED" ]; then
    echo -e "${YELLOW}警告: Nginx 配置已存在，正在覆盖...${NC}"
    sudo rm "$NGINX_ENABLED"
fi
sudo ln -s "$NGINX_CONFIG" "$NGINX_ENABLED"

# 删除默认配置（如果存在）
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo -e "${YELLOW}删除 Nginx 默认配置...${NC}"
    sudo rm /etc/nginx/sites-enabled/default
fi

# 测试 Nginx 配置
echo "测试 Nginx 配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx 配置成功${NC}"
    # 重启 Nginx
    sudo systemctl restart nginx
    echo -e "${GREEN}✓ Nginx 已重启${NC}"
else
    echo -e "${RED}错误: Nginx 配置测试失败，请检查配置${NC}"
    exit 1
fi

# ==========================================
# 6. 创建 systemd 服务（可选）
# ==========================================
echo -e "\n${YELLOW}[步骤 6/7] 创建 systemd 服务...${NC}"

read -p "是否创建 systemd 服务以自动启动？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 创建 Python 后端服务
    cat > /tmp/financial-backend.service <<EOF
[Unit]
Description=Financial QA System - Python Backend
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=/home/$(whoami)/miniconda3/envs/financial/bin:\$PATH"
ExecStart=/home/$(whoami)/miniconda3/envs/financial/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/financial-backend.service /etc/systemd/system/

    # 创建前端服务
    cat > /tmp/financial-frontend.service <<EOF
[Unit]
Description=Financial QA System - Next.js Frontend
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT/web-app
Environment="PATH=/usr/bin:\$PATH"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/financial-frontend.service /etc/systemd/system/

    # 重新加载 systemd
    sudo systemctl daemon-reload

    # 启用并启动服务
    sudo systemctl enable financial-backend financial-frontend
    sudo systemctl restart financial-backend financial-frontend

    echo -e "${GREEN}✓ systemd 服务创建成功${NC}"
    echo -e "${GREEN}  - 后端服务: financial-backend.service${NC}"
    echo -e "${GREEN}  - 前端服务: financial-frontend.service${NC}"
fi

# ==========================================
# 7. 启动服务
# ==========================================
echo -e "\n${YELLOW}[步骤 7/7] 启动服务...${NC}"

# 检查服务是否已通过 systemd 启动
if systemctl is-active --quiet financial-backend && systemctl is-active --quiet financial-frontend; then
    echo -e "${GREEN}✓ 服务已通过 systemd 启动${NC}"
else
    echo -e "${YELLOW}手动启动服务...${NC}"
    echo ""
    echo "请在两个独立的终端中运行以下命令："
    echo ""
    echo -e "${GREEN}终端 1 (Python 后端):${NC}"
    echo "  cd $PROJECT_ROOT"
    if command -v conda &> /dev/null; then
        echo "  conda activate financial"
    fi
    echo "  python main.py"
    echo ""
    echo -e "${GREEN}终端 2 (Next.js 前端):${NC}"
    echo "  cd $PROJECT_ROOT/web-app"
    echo "  npm start"
fi

# ==========================================
# 部署完成
# ==========================================
echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址: http://your-server-ip"
echo ""
echo "服务状态检查："
echo "  - 后端状态: sudo systemctl status financial-backend"
echo "  - 前端状态: sudo systemctl status financial-frontend"
echo "  - Nginx 状态: sudo systemctl status nginx"
echo ""
echo "日志查看："
echo "  - 后端日志: sudo journalctl -u financial-backend -f"
echo "  - 前端日志: sudo journalctl -u financial-frontend -f"
echo "  - Nginx 日志: sudo tail -f /var/log/nginx/financial-qa-error.log"
echo ""
echo "=========================================="
