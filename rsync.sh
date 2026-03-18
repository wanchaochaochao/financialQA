#!/bin/bash

# 配置变量
LOCAL_DIR="/Users/wanchao/financialQA/"
REMOTE_USER="root"
#REMOTE_HOST="8.136.8.9"
REMOTE_HOST="39.106.23.157"
REMOTE_DIR="/root/workspace/financialQA"

echo "开始同步项目到云服务器..."

# rsync -avz --progress --delete \
#   --exclude 'node_modules/' \
#   --exclude '.git/' \
#   --exclude '.next/' \
#   --exclude '*.log' \
#   --exclude '.DS_Store' \
#   --exclude 'npm-debug.log*' \
#   --exclude 'yarn-debug.log*' \
#   --exclude 'yarn-error.log*' \
#   --exclude '.env.local' \
#   ${LOCAL_DIR} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}
# 
# if [ $? -eq 0 ]; then
#     echo "✅ 文件同步成功！"
#     echo "🔄 正在云服务器上安装依赖..."
#     
#     ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ~/shouban && npm install && echo '✅ 依赖安装完成！'"
# else
#     echo "❌ 同步失败，请检查网络连接和服务器配置"
# fi
# 

rsync -avz --progress --stats \
  --exclude 'ai_agent/__pycache__/' \
  --exclude 'web-app/.next/' \
  --exclude 'web-app/node_modules/' \
  --exclude 'web-app/next.config.js' \
  --exclude 'ecosystem.config.js' \
  --exclude '.env' \
  --exclude 'start_api.py' \
  --exclude 'start_api.sh' \
  --exclude 'web-app/.env.example' \
  --exclude 'start_fullstack.sh' \
  --exclude 'web-app/.env.local' \
  --exclude 'web-app/.env.example' \
  ${LOCAL_DIR} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}