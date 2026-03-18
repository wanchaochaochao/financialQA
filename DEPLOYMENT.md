# 云服务器部署文档

金融资产问答系统云服务器部署指南。

## 目录

- [架构说明](#架构说明)
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [手动部署](#手动部署)
- [环境变量配置](#环境变量配置)
- [Nginx 配置说明](#nginx-配置说明)
- [故障排查](#故障排查)
- [常用命令](#常用命令)

---

## 架构说明

### 部署架构

```
用户浏览器
    ↓
[Nginx :80]  ← 反向代理
    ├─→ /api/*     → [Python FastAPI :9000]  ← AI 后端
    └─→ /*         → [Next.js :3000]         ← 前端
```

### 关键优势

1. **统一入口**：所有请求通过 Nginx（80 端口）进入，避免跨域问题
2. **端口隐藏**：后端端口（9000, 3000）不对外暴露，提高安全性
3. **负载均衡**：Nginx 可配置负载均衡和缓存
4. **易于扩展**：可轻松添加 HTTPS、CDN 等功能

---

## 环境要求

### 操作系统
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+

### 软件依赖
- **Python**: 3.10+
- **Node.js**: 18+
- **Nginx**: 1.18+
- **Conda**: 可选，用于 Python 环境管理

### 硬件建议
- **CPU**: 2 核心+
- **内存**: 4GB+
- **磁盘**: 20GB+

---

## 快速部署

### 方法一：使用自动化脚本（推荐）

```bash
# 1. 上传代码到服务器
git clone <your-repo-url>
cd financialQA

# 2. 配置环境变量
cp web-app/.env.example web-app/.env.local
nano web-app/.env.local

# 修改为：
# NEXT_PUBLIC_PYTHON_API_URL=
# （留空表示使用 Nginx 反向代理）

# 3. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 4. 完成！访问 http://your-server-ip
```

---

## 手动部署

如果需要更精细的控制，可以手动执行以下步骤。

### 步骤 1：安装系统依赖

#### Ubuntu/Debian

```bash
# 更新软件包
sudo apt update && sudo apt upgrade -y

# 安装 Nginx
sudo apt install nginx -y

# 安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 Python 3.10+ (如果系统版本较低)
sudo apt install python3 python3-pip -y

# 安装 Miniconda (可选)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

#### CentOS/RHEL

```bash
# 更新软件包
sudo yum update -y

# 安装 Nginx
sudo yum install nginx -y

# 安装 Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y

# 安装 Python 3.10+
sudo yum install python3 python3-pip -y
```

### 步骤 2：配置 Python 后端

```bash
cd financialQA

# 创建 conda 环境（推荐）
conda create -n financial python=3.10 -y
conda activate financial

# 安装 Python 依赖
pip install -r requirements.txt

# 测试后端
python main.py

# 确认后端运行在 http://localhost:9000
# 访问 http://localhost:9000/docs 查看 API 文档
```

### 步骤 3：配置前端

```bash
cd web-app

# 配置环境变量
cp .env.example .env.local

# 编辑环境变量
nano .env.local
```

**重要：配置 `.env.local`**

```bash
# 云服务器部署配置（使用 Nginx 反向代理）
NEXT_PUBLIC_PYTHON_API_URL=

# 注意：留空表示使用相对路径，Nginx 会将 /api/* 代理到后端
```

```bash
# 安装依赖
npm install

# 构建生产版本
npm run build

# 启动生产服务器
npm start

# 确认前端运行在 http://localhost:3000
```

### 步骤 4：配置 Nginx

```bash
# 复制 Nginx 配置文件
sudo cp ../nginx.conf /etc/nginx/sites-available/financial-qa

# 创建软链接
sudo ln -s /etc/nginx/sites-available/financial-qa /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 设置 Nginx 开机自启
sudo systemctl enable nginx
```

### 步骤 5：配置 systemd 服务（开机自启）

#### 创建 Python 后端服务

```bash
sudo nano /etc/systemd/system/financial-backend.service
```

```ini
[Unit]
Description=Financial QA System - Python Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/financialQA
Environment="PATH=/home/your-username/miniconda3/envs/financial/bin:$PATH"
ExecStart=/home/your-username/miniconda3/envs/financial/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 创建前端服务

```bash
sudo nano /etc/systemd/system/financial-frontend.service
```

```ini
[Unit]
Description=Financial QA System - Next.js Frontend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/financialQA/web-app
Environment="PATH=/usr/bin:$PATH"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable financial-backend
sudo systemctl enable financial-frontend

# 启动服务
sudo systemctl start financial-backend
sudo systemctl start financial-frontend

# 检查服务状态
sudo systemctl status financial-backend
sudo systemctl status financial-frontend
```

### 步骤 6：配置防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用 HTTPS
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 步骤 7：访问系统

打开浏览器，访问：

```
http://your-server-ip
```

---

## 环境变量配置

### 前端环境变量 (`web-app/.env.local`)

```bash
# ==========================================
# 部署模式选择
# ==========================================

# 【推荐】方案 1：Nginx 反向代理（生产环境）
NEXT_PUBLIC_PYTHON_API_URL=

# 方案 2：直接连接后端 IP（仅测试用）
# NEXT_PUBLIC_PYTHON_API_URL=http://your-server-ip:9000

# 方案 3：使用域名（需配置 DNS 和证书）
# NEXT_PUBLIC_PYTHON_API_URL=https://api.yourdomain.com
```

### 后端环境变量

如果后端有 `.env` 文件，确保配置：

```bash
# 后端端口（默认 9000）
PORT=9000

# 数据库连接等其他配置
# ...
```

---

## Nginx 配置说明

### 核心配置解析

```nginx
# 后端 API 代理
location /api/ {
    proxy_pass http://localhost:9000;
    # 将所有 /api/* 请求代理到 Python 后端
}

# 前端代理
location / {
    proxy_pass http://localhost:3000;
    # 将其他所有请求代理到 Next.js 前端
}
```

### 请求流程示例

```
用户请求: http://your-server-ip/api/chat
    ↓
Nginx 接收 (端口 80)
    ↓
匹配 location /api/
    ↓
代理到: http://localhost:9000/api/chat
    ↓
Python FastAPI 处理并返回
    ↓
Nginx 返回给用户
```

### 修改端口

如果需要修改后端或前端端口，需要同步修改：

1. **后端端口（例如改为 8000）**：
   - 修改 `nginx.conf` 中的 `upstream python_backend`
   - 修改 Python 启动命令中的端口

2. **前端端口（例如改为 4000）**：
   - 修改 `nginx.conf` 中的 `upstream nextjs_frontend`
   - 修改 `web-app/package.json` 中的启动命令

---

## 故障排查

### 问题 1：ERR_CONNECTION_REFUSED

**原因**：前端无法连接到后端

**解决方案**：

```bash
# 1. 检查后端是否运行
curl http://localhost:9000/api/health

# 2. 检查前端环境变量
cat web-app/.env.local

# 3. 检查 Nginx 是否运行
sudo systemctl status nginx

# 4. 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/financial-qa-error.log
```

### 问题 2：Nginx 502 Bad Gateway

**原因**：Nginx 无法连接到后端/前端服务

**解决方案**：

```bash
# 检查后端和前端是否运行
sudo systemctl status financial-backend
sudo systemctl status financial-frontend

# 重启服务
sudo systemctl restart financial-backend financial-frontend
```

### 问题 3：前端显示空白页面

**原因**：前端未正确构建或环境变量错误

**解决方案**：

```bash
cd web-app

# 重新构建
npm run build

# 重启前端服务
sudo systemctl restart financial-frontend
```

### 问题 4：API 请求 404

**原因**：API 路由配置错误

**解决方案**：

```bash
# 1. 检查 Nginx 配置
sudo nginx -t

# 2. 查看 Nginx 配置中的 location 匹配规则
sudo cat /etc/nginx/sites-available/financial-qa

# 3. 测试后端 API
curl http://localhost:9000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "测试"}'
```

---

## 常用命令

### 服务管理

```bash
# 查看服务状态
sudo systemctl status financial-backend
sudo systemctl status financial-frontend
sudo systemctl status nginx

# 启动服务
sudo systemctl start financial-backend
sudo systemctl start financial-frontend

# 停止服务
sudo systemctl stop financial-backend
sudo systemctl stop financial-frontend

# 重启服务
sudo systemctl restart financial-backend
sudo systemctl restart financial-frontend
sudo systemctl restart nginx

# 查看日志
sudo journalctl -u financial-backend -f
sudo journalctl -u financial-frontend -f
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 查看错误日志
sudo tail -f /var/log/nginx/financial-qa-error.log

# 查看访问日志
sudo tail -f /var/log/nginx/financial-qa-access.log
```

### 进程管理

```bash
# 查看 Python 后端进程
ps aux | grep python

# 查看 Node.js 进程
ps aux | grep node

# 查看端口占用
sudo lsof -i :80    # Nginx
sudo lsof -i :3000  # Next.js
sudo lsof -i :9000  # Python FastAPI

# 杀死进程
kill -9 <PID>
```

---

## 高级配置

### 配置 HTTPS (SSL)

1. 获取 SSL 证书（推荐使用 Let's Encrypt）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx -y

# 自动配置 HTTPS
sudo certbot --nginx -d yourdomain.com
```

2. 或手动配置（取消 `nginx.conf` 中 HTTPS 部分的注释）

### 配置域名

1. 在域名服务商处添加 A 记录：
   - 主机记录: `@` 或 `www`
   - 记录值: `your-server-ip`

2. 修改 `nginx.conf` 中的 `server_name`:
   ```nginx
   server_name yourdomain.com www.yourdomain.com;
   ```

3. 重启 Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

### 性能优化

1. **启用 Gzip 压缩**（已在 nginx.conf 中配置）
2. **配置缓存**（静态资源已配置缓存）
3. **调整 worker_processes**（根据 CPU 核心数）

---

## 安全建议

1. **防火墙**：只开放必要端口（80, 443）
2. **SSH**：修改默认端口，禁用密码登录
3. **定期更新**：保持系统和软件包更新
4. **备份**：定期备份数据库和配置文件
5. **监控**：使用工具监控服务器资源使用情况

---

## 支持

如遇到问题，请检查：

1. 系统日志: `/var/log/syslog`
2. Nginx 日志: `/var/log/nginx/`
3. 应用日志: `sudo journalctl -u financial-backend -f`

---

**部署完成后，别忘了测试所有功能是否正常！**
