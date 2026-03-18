/**
 * PM2 Process Manager Configuration
 * ==================================
 *
 * 用于在生产环境中管理 Python 后端和 Next.js 前端进程
 *
 * 使用方法:
 * 1. 修改下面的配置（Python 路径、端口等）
 * 2. pm2 start ecosystem.config.js
 * 3. pm2 status  // 查看状态
 * 4. pm2 logs    // 查看日志
 * 5. pm2 save && pm2 startup  // 设置开机自启
 */

module.exports = {
  apps: [
    // ==================== Python FastAPI Backend ====================
    {
      name: 'financial-backend',

      // Python 后端启动脚本
      script: 'start_api.py',

      // Python 解释器路径（根据你的环境修改）
      // Conda 环境示例:
      interpreter: '/home/your-user/miniconda3/envs/financial/bin/python',
      // 或系统 Python:
      // interpreter: '/usr/bin/python3',
      // 或虚拟环境:
      // interpreter: '/opt/financialQA/venv/bin/python',

      // 工作目录
      cwd: '/opt/financialQA',

      // 环境变量（从 .env 文件读取，这里可覆盖）
      env: {
        API_HOST: '0.0.0.0',
        API_PORT: 8000,  // 修改此处可更改后端端口
        API_BASE_URL: 'http://your-server-ip:8000',  // 修改为你的服务器地址
        // 其他环境变量会从 .env 文件自动读取
      },

      // 生产环境配置（可选）
      env_production: {
        NODE_ENV: 'production',
        API_PORT: 8000,
      },

      // 进程配置
      instances: 1,                    // 实例数量（Python 后端建议用 1）
      exec_mode: 'fork',               // 执行模式
      autorestart: true,               // 自动重启
      watch: false,                    // 不监听文件变化（生产环境）
      max_memory_restart: '1G',        // 超过 1GB 内存自动重启

      // 日志配置
      error_file: '/var/log/pm2/financial-backend-error.log',
      out_file: '/var/log/pm2/financial-backend-out.log',
      log_file: '/var/log/pm2/financial-backend-combined.log',
      time: true,                      // 日志添加时间戳

      // 其他配置
      restart_delay: 4000,             // 重启延迟（毫秒）
      max_restarts: 10,                // 最大重启次数
      min_uptime: '10s',               // 最小运行时间
    },

    // ==================== Next.js Frontend ====================
    {
      name: 'financial-frontend',

      // Next.js 启动命令
      script: 'npm',
      args: 'run start',               // 使用 production 模式（需先 npm run build）
      // 开发模式（不推荐生产环境）:
      // args: 'run dev',

      // 工作目录
      cwd: '/opt/financialQA/web-app',

      // 环境变量
      env: {
        PORT: 3000,                    // 修改此处可更改前端端口
        NODE_ENV: 'production',
        // Next.js 后端 API 地址（应与 web-app/.env.local 一致）
        NEXT_PUBLIC_PYTHON_API_URL: 'http://your-server-ip:8000',
      },

      // 开发环境配置（可选）
      env_development: {
        PORT: 3000,
        NODE_ENV: 'development',
      },

      // 进程配置
      instances: 1,                    // Next.js 建议用 1 个实例
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',      // Next.js 内存限制

      // 日志配置
      error_file: '/var/log/pm2/financial-frontend-error.log',
      out_file: '/var/log/pm2/financial-frontend-out.log',
      log_file: '/var/log/pm2/financial-frontend-combined.log',
      time: true,

      // 其他配置
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
    },
  ],
};

/**
 * 快速配置指南
 * ==================================
 *
 * 1. 修改 Python 解释器路径:
 *    - 查看路径: which python (在 conda 环境中)
 *    - 或: /home/your-user/miniconda3/envs/financial/bin/python
 *
 * 2. 修改端口:
 *    - 后端: env.API_PORT
 *    - 前端: env.PORT
 *
 * 3. 修改服务器地址:
 *    - env.API_BASE_URL
 *    - env.NEXT_PUBLIC_PYTHON_API_URL
 *
 * 4. 创建日志目录:
 *    sudo mkdir -p /var/log/pm2
 *    sudo chown $USER:$USER /var/log/pm2
 *
 * 5. 启动服务:
 *    pm2 start ecosystem.config.js
 *
 * 6. 设置开机自启:
 *    pm2 startup
 *    pm2 save
 *
 * 常用命令:
 * - pm2 status              // 查看状态
 * - pm2 logs                // 查看日志
 * - pm2 logs backend        // 查看后端日志
 * - pm2 restart all         // 重启所有
 * - pm2 stop all            // 停止所有
 * - pm2 delete all          // 删除所有
 * - pm2 monit               // 监控面板
 */
