# 用户认证系统使用指南

## 系统概述

已成功为金融资产问答系统添加完整的用户认证系统，包括：
- 用户注册
- 用户登录
- JWT Token 认证
- 会话管理
- 前端路由保护

## 技术栈

### 后端
- **数据库**: SQLite3（轻量级本地数据库）
- **ORM**: SQLAlchemy 2.0
- **密码加密**: Passlib + Bcrypt
- **JWT**: python-jose

### 前端
- **认证状态**: localStorage
- **路由保护**: Next.js useRouter + useEffect
- **UI**: Tailwind CSS

---

## 数据库结构

### Users 表

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    nickname VARCHAR UNIQUE NOT NULL,          -- 用户名（唯一）
    password_hash VARCHAR NOT NULL,            -- 密码哈希
    phone VARCHAR UNIQUE,                      -- 手机号（可选，唯一）
    email VARCHAR UNIQUE,                      -- 邮箱（可选，唯一）
    vip_level INTEGER DEFAULT 0,              -- VIP等级（0=普通，1-5=VIP）
    vip_expire DATETIME,                       -- VIP到期时间
    status BOOLEAN DEFAULT TRUE,               -- 账户状态（True=激活）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

**数据库位置**: `/Users/wanchao/financialQA/data/financial_qa.db`

---

## API 端点

### 认证相关端点

| 端点 | 方法 | 功能 | 需要认证 |
|------|------|------|----------|
| `/api/auth/register` | POST | 用户注册 | ❌ |
| `/api/auth/login` | POST | 用户登录 | ❌ |
| `/api/auth/me` | GET | 获取当前用户信息 | ✅ |

### 1. 用户注册

**请求**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "testuser",
    "password": "password123",
    "phone": "13800138000",
    "email": "test@example.com"
  }'
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nickname": "testuser",
    "phone": "13800138000",
    "email": "test@example.com",
    "vip_level": 0,
    "status": true
  }
}
```

### 2. 用户登录

**请求**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "testuser",
    "password": "password123"
  }'
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nickname": "testuser",
    "vip_level": 0,
    "vip_active": false,
    "status": true
  }
}
```

### 3. 获取当前用户信息

**请求**:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**响应**:
```json
{
  "id": 1,
  "nickname": "testuser",
  "phone": "13800138000",
  "email": "test@example.com",
  "vip_level": 0,
  "vip_expire": null,
  "status": true,
  "created_at": "2026-03-15T10:30:00",
  "last_login": "2026-03-15T14:30:00"
}
```

### 4. 聊天接口（可选认证）

现在 `/api/chat` 接口支持可选的用户认证。如果提供 Token，会记录是哪个用户的对话。

**请求**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -d '{"question": "阿里巴巴最新股价？"}'
```

---

## 前端使用

### 页面路由

| 路由 | 页面 | 需要登录 |
|------|------|----------|
| `/` | 聊天界面 | ✅ |
| `/login` | 登录页面 | ❌ |
| `/register` | 注册页面 | ❌ |

### 用户流程

```mermaid
graph TD
    A[访问首页] --> B{已登录?}
    B -->|否| C[跳转到登录页]
    C --> D[登录]
    C --> E[注册]
    D --> F[保存Token]
    E --> F
    F --> G[跳转到首页]
    B -->|是| G
    G --> H[显示聊天界面]
    H --> I[点击退出]
    I --> J[清除Token]
    J --> C
```

### 认证状态管理

**保存登录状态**:
```typescript
import { saveAuth, TokenResponse } from '@/lib/auth';

const tokenResponse: TokenResponse = {
  access_token: "...",
  token_type: "bearer",
  user: { ... }
};

saveAuth(tokenResponse);  // 保存到 localStorage
```

**检查登录状态**:
```typescript
import { isAuthenticated, getUser } from '@/lib/auth';

if (isAuthenticated()) {
  const user = getUser();
  console.log(user.nickname);
}
```

**清除登录状态**:
```typescript
import { clearAuth } from '@/lib/auth';

clearAuth();  // 退出登录
```

---

## 安装和运行

### 1. 安装依赖

```bash
# 后端依赖
cd /Users/wanchao/financialQA
pip install -r requirements.txt

# 新增的依赖：
# - sqlalchemy>=2.0.0
# - passlib[bcrypt]>=1.7.4
# - python-jose[cryptography]>=3.3.0
```

### 2. 启动后端

```bash
# 启动 FastAPI
python start_api.py --dev

# 或使用 uvicorn
uvicorn ai_agent.api:app --reload
```

**数据库自动初始化**: FastAPI 启动时会自动创建数据库和表。

### 3. 启动前端

```bash
cd web-app
npm run dev
```

### 4. 访问系统

1. 打开浏览器访问: http://localhost:3000
2. 自动跳转到登录页面
3. 点击"立即注册"创建账号
4. 登录后即可使用聊天功能

---

## 密码安全

### 密码加密

- 使用 **Bcrypt** 哈希算法
- 密码不会以明文存储
- 每个密码都有唯一的 salt

### JWT Token

- 使用 **HS256** 算法签名
- Token 有效期: **7天**
- Token 存储在浏览器 localStorage

### 安全建议

**生产环境配置**:

1. **修改 JWT 密钥**（`.env` 文件）:
   ```bash
   JWT_SECRET_KEY=your-very-secret-random-string-here
   ```

2. **使用 HTTPS**:
   - 生产环境必须使用 HTTPS
   - Token 在 HTTPS 下传输更安全

3. **Token 过期时间**:
   - 当前设置: 7天
   - 可在 `ai_agent/auth.py` 中调整:
     ```python
     ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
     ```

4. **CORS 配置**:
   - 当前允许所有域名（开发环境）
   - 生产环境应限制特定域名
   - 在 `ai_agent/api.py` 中修改:
     ```python
     allow_origins=["https://yourdomain.com"]
     ```

---

## 文件结构

### 后端文件

```
ai_agent/
├── database.py         # 数据库配置
├── models.py           # 数据库模型（User）
├── auth.py             # 认证工具（密码加密、JWT）
├── crud.py             # CRUD 操作
└── api.py              # API 端点（新增认证端点）

data/
└── financial_qa.db     # SQLite 数据库（自动创建）
```

### 前端文件

```
web-app/src/
├── lib/
│   ├── auth.ts         # 认证工具函数
│   └── api.ts          # API 调用（新增认证接口）
├── app/
│   ├── login/
│   │   └── page.tsx    # 登录页面
│   └── register/
│       └── page.tsx    # 注册页面
└── components/
    └── ChatInterface.tsx  # 聊天界面（新增认证检查）
```

---

## 常见问题

### Q1: 忘记密码怎么办？

目前系统不支持找回密码功能。如需重置密码，可以：

**方法1**: 直接删除数据库重新注册
```bash
rm /Users/wanchao/financialQA/data/financial_qa.db
```

**方法2**: 使用 SQLite 工具修改密码哈希
```bash
sqlite3 /Users/wanchao/financialQA/data/financial_qa.db
# 然后执行 SQL 更新
```

### Q2: 如何查看所有用户？

```bash
# 使用 SQLite 命令行
sqlite3 /Users/wanchao/financialQA/data/financial_qa.db

# 查询所有用户
SELECT id, nickname, phone, email, vip_level, status FROM users;
```

### Q3: 如何设置用户为 VIP？

```bash
sqlite3 /Users/wanchao/financialQA/data/financial_qa.db

# 设置用户为 VIP3，有效期30天
UPDATE users
SET vip_level = 3,
    vip_expire = datetime('now', '+30 days')
WHERE nickname = 'testuser';
```

### Q4: Token 过期后怎么办？

- Token 过期后，前端会自动跳转到登录页面
- 用户需要重新登录获取新 Token

### Q5: 如何禁用某个用户？

```bash
sqlite3 /Users/wanchao/financialQA/data/financial_qa.db

# 禁用用户
UPDATE users SET status = 0 WHERE nickname = 'testuser';

# 启用用户
UPDATE users SET status = 1 WHERE nickname = 'testuser';
```

---

## 测试

### 测试用例

#### 1. 注册新用户
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nickname": "alice", "password": "alice123"}'
```

#### 2. 用户名重复
```bash
# 应返回 400 错误
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nickname": "alice", "password": "different"}'
```

#### 3. 登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"nickname": "alice", "password": "alice123"}'
```

#### 4. 错误密码
```bash
# 应返回 401 错误
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"nickname": "alice", "password": "wrongpassword"}'
```

#### 5. 获取用户信息
```bash
# 替换 TOKEN 为实际的 JWT token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

---

## 下一步扩展

### 可选功能

1. **邮箱验证**: 注册时发送验证邮件
2. **手机验证码**: 使用短信验证码注册/登录
3. **找回密码**: 通过邮箱重置密码
4. **第三方登录**: 微信、QQ、GitHub OAuth
5. **用户头像**: 支持头像上传
6. **VIP 功能**: VIP 用户享受特殊功能（如更快的响应、更多查询次数）
7. **用户权限**: 管理员、普通用户等角色管理
8. **聊天历史**: 保存每个用户的聊天记录

---

## 总结

✅ **已完成**:
- SQLite 数据库和 Users 表
- 用户注册/登录 API
- JWT Token 认证
- 密码加密存储
- Next.js 登录/注册页面
- 前端认证状态管理
- 路由保护（未登录跳转）
- 用户信息显示
- 退出登录功能

🚀 **系统已可投入使用**，支持多用户同时使用金融问答平台！

---

**创建时间**: 2026-03-15
**版本**: 1.0.0
