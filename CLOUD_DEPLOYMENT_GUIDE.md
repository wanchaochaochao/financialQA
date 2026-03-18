# 云服务器部署指南

本指南帮助你将金融资产问答系统部署到云服务器（阿里云、腾讯云、AWS、Azure 等）。

---

## 📋 系统要求

### 服务器配置
- **CPU**: 2核及以上
- **内存**: 4GB 及以上（推荐 8GB）
- **硬盘**: 20GB 及以上
- **操作系统**: Ubuntu 20.04/22.04 或 CentOS 7/8

### 网络要求
- 开放端口（根据你的配置调整）:
  - **前端**: 3000 (或自定义)
  - **后端**: 8000 (或自定义)
  - **SSH**: 22
  - **HTTP**: 80 (可选，用于 Nginx 反向代理)
  - **HTTPS**: 443 (可选，用于 SSL)

---

## 🚀 快速部署（推荐流程）

### 步骤 1: 连接到云服务器

```bash
# 使用 SSH 连接到服务器
ssh root@your-server-ip

# 或使用密钥文件
ssh -i /path/to/your-key.pem ubuntu@your-server-ip
```

### 步骤 2: 安装基础环境

#### 方式 A: 使用 Anaconda/Miniconda（推荐）

```bash
# 下载 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装 Miniconda
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# 初始化 conda
~/miniconda3/bin/conda init bash
source ~/.bashrc

# 创建 Python 环境
conda create -n financial python=3.10 -y
conda activate financial
```

#### 方式 B: 使用系统 Python + venv

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
```

#### 安装 Node.js（前端需要）

```bash
# 使用 NodeSource 安装 Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 或使用 nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 步骤 3: 克隆项目代码

```bash
# 进入工作目录
cd /opt  # 或你选择的目录

# 克隆项目（假设你已上传到 GitHub）
git clone https://github.com/your-username/financialQA.git
cd financialQA

# 或者使用 scp 上传本地代码
# 在本地执行:
# scp -r /Users/wanchao/financialQA root@your-server-ip:/opt/
```

### 步骤 4: 配置环境变量

#### 后端配置 (.env)

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

修改以下配置：

```bash
# API Server Configuration
API_HOST=0.0.0.0                              # 监听所有网络接口
API_PORT=8000                                  # 后端端口（可自定义）

# API Base URL（重要！修改为你的服务器地址）
API_BASE_URL=http://your-server-ip:8000       # 或使用域名
# API_BASE_URL=https://api.yourdomain.com

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here    # 填入真实的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1

# LLM Model Configuration
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0

# Agent Configuration
AGENT_MAX_ITERATIONS=15
AGENT_MAX_EXECUTION_TIME=60
AGENT_VERBOSE=true

# Optional: AI Image Generation
# TUZI_API_KEY=your-tuzi-api-key-here
```

#### 前端配置 (web-app/.env.local)

```bash
cd web-app
cp .env.example .env.local
vim .env.local
```

修改为你的服务器地址：

```bash
# Python FastAPI Backend URL（重要！修改为你的服务器地址）
NEXT_PUBLIC_PYTHON_API_URL=http://your-server-ip:8000
# 或使用域名
# NEXT_PUBLIC_PYTHON_API_URL=https://api.yourdomain.com
```

### 步骤 5: 安装依赖

#### 后端依赖

```bash
cd /opt/financialQA

# 激活 conda 环境
conda activate financial

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd /opt/financialQA/web-app
npm install
```

### 步骤 6: 构建前端（生产环境）

```bash
cd /opt/financialQA/web-app

# 构建生产版本
npm run build

# 测试构建是否成功
npm run start
```

### 步骤 7: 使用 PM2 管理进程（推荐）

PM2 是一个生产级的进程管理工具，可以自动重启、日志管理、开机自启等。

#### 安装 PM2

```bash
npm install -g pm2
```

#### 创建 PM2 配置文件

```bash
cd /opt/financialQA
vim ecosystem.config.js
```

添加以下内容：

```javascript
module.exports = {
  apps: [
    {
      name: 'financial-backend',
      script: '/opt/financialQA/start_api.py',
      interpreter: '/home/your-user/miniconda3/envs/financial/bin/python',
      cwd: '/opt/financialQA',
      env: {
        API_HOST: '0.0.0.0',
        API_PORT: 8000,
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/var/log/pm2/financial-backend-error.log',
      out_file: '/var/log/pm2/financial-backend-out.log',
      log_file: '/var/log/pm2/financial-backend-combined.log',
      time: true,
    },
    {
      name: 'financial-frontend',
      script: 'npm',
      args: 'run start',
      cwd: '/opt/financialQA/web-app',
      env: {
        PORT: 3000,
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/log/pm2/financial-frontend-error.log',
      out_file: '/var/log/pm2/financial-frontend-out.log',
      log_file: '/var/log/pm2/financial-frontend-combined.log',
      time: true,
    },
  ],
};
```

#### 启动服务

```bash
# 创建日志目录
sudo mkdir -p /var/log/pm2
sudo chown $USER:$USER /var/log/pm2

# 启动所有服务
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs

# 开机自启
pm2 startup
pm2 save
```

---

## 🔐 使用 Nginx 反向代理（可选但推荐）

使用 Nginx 可以实现：
- 统一域名访问（前后端同域）
- SSL/HTTPS 支持
- 负载均衡
- Gzip 压缩

### 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx -y

# CentOS/RHEL
sudo yum install nginx -y

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 配置 Nginx

```bash
sudo vim /etc/nginx/sites-available/financial-qa
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名或服务器 IP

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # 超时设置（AI 响应可能较慢）
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
    }

    # 图表静态文件
    location /charts/ {
        proxy_pass http://localhost:8000/charts/;
        proxy_set_header Host $host;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/financial-qa /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl reload nginx
```

### 配置 SSL/HTTPS（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 📊 环境变量完整配置示例

### 本地开发环境

**后端 (.env)**:
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000
OPENAI_API_KEY=sk-xxx
```

**前端 (web-app/.env.local)**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
```

### 云服务器直接访问（无 Nginx）

**后端 (.env)**:
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://123.45.67.89:8000  # 你的服务器 IP
OPENAI_API_KEY=sk-xxx
```

**前端 (web-app/.env.local)**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://123.45.67.89:8000
```

### 云服务器 + Nginx 反向代理

**后端 (.env)**:
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://your-domain.com  # 通过 Nginx 访问
OPENAI_API_KEY=sk-xxx
```

**前端 (web-app/.env.local)**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=https://your-domain.com
```

---

## 🛠️ 常用运维命令

### PM2 管理

```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs
pm2 logs financial-backend
pm2 logs financial-frontend

# 重启服务
pm2 restart financial-backend
pm2 restart financial-frontend
pm2 restart all

# 停止服务
pm2 stop financial-backend
pm2 stop all

# 删除服务
pm2 delete financial-backend

# 监控
pm2 monit
```

### 日志查看

```bash
# PM2 日志
tail -f /var/log/pm2/financial-backend-out.log
tail -f /var/log/pm2/financial-frontend-out.log

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 更新代码

```bash
# 拉取最新代码
cd /opt/financialQA
git pull

# 更新后端依赖
conda activate financial
pip install -r requirements.txt

# 更新前端依赖并重新构建
cd web-app
npm install
npm run build

# 重启服务
pm2 restart all
```

---

## ⚠️ 常见问题

### Q1: 端口被占用
```bash
# 查看端口占用
lsof -i:8000
lsof -i:3000

# 杀死进程
kill -9 <PID>
```

### Q2: 防火墙阻止访问
```bash
# Ubuntu UFW
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS firewalld
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload
```

### Q3: 云服务器安全组配置
- 阿里云: 进入 ECS 控制台 → 安全组 → 配置规则 → 添加入方向规则
- 腾讯云: 进入 CVM 控制台 → 安全组 → 入站规则 → 新建
- AWS: EC2 → Security Groups → Inbound Rules → Edit

### Q4: API 连接失败
检查：
1. 后端是否启动：`pm2 status`
2. 端口是否开放：`lsof -i:8000`
3. 防火墙设置
4. 环境变量配置是否正确

### Q5: 图表图片无法显示
确保 `API_BASE_URL` 配置正确：
- 如果使用 IP 访问：`http://123.45.67.89:8000`
- 如果使用域名：`https://your-domain.com`

---

## 📝 部署检查清单

- [ ] 服务器环境安装完成（Python、Node.js）
- [ ] 项目代码已上传到服务器
- [ ] 后端 .env 文件配置完成（API_HOST、API_PORT、API_BASE_URL、OPENAI_API_KEY）
- [ ] 前端 .env.local 文件配置完成（NEXT_PUBLIC_PYTHON_API_URL）
- [ ] Python 依赖安装完成（pip install -r requirements.txt）
- [ ] 前端依赖安装并构建完成（npm install && npm run build）
- [ ] PM2 配置文件创建并启动服务
- [ ] 防火墙/安全组配置端口开放
- [ ] Nginx 配置并启用（可选）
- [ ] SSL 证书配置（可选）
- [ ] PM2 开机自启配置（pm2 startup && pm2 save）

---

## 🎉 完成部署

部署完成后，你可以通过以下地址访问：

- **前端**: `http://your-server-ip:3000` 或 `https://your-domain.com`
- **后端 API 文档**: `http://your-server-ip:8000/docs` 或 `https://your-domain.com/api/docs`

祝部署顺利！🚀
