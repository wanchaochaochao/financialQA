# 金融资产问答系统 - Web前端

基于 Next.js 14 + TypeScript + Tailwind CSS 的现代化前端界面。

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 2. 启动开发服务器

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

访问 [http://localhost:3000](http://localhost:3000)

### 3. 确保后端运行

前端需要Python FastAPI后端运行在端口8000：

```bash
# 在项目根目录
python start_api.py --dev
```

## 📁 项目结构

```
web-app/
├── src/
│   ├── app/              # Next.js 14 App Router
│   │   ├── layout.tsx    # 全局布局
│   │   ├── page.tsx      # 主页面
│   │   └── globals.css   # 全局样式
│   ├── components/       # React组件
│   │   ├── ChatInterface.tsx      # 聊天界面主组件
│   │   ├── MessageList.tsx        # 消息列表
│   │   ├── MessageItem.tsx        # 消息项
│   │   ├── InputBox.tsx           # 输入框
│   │   └── ExampleQuestions.tsx   # 示例问题
│   ├── lib/             # 工具函数
│   │   ├── api.ts       # API调用
│   │   └── utils.ts     # 通用工具
│   └── types/           # TypeScript类型定义
│       └── index.ts
├── public/              # 静态资源
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🛠️ 技术栈

- **Next.js 14** - React框架 (App Router)
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **Axios** - HTTP请求
- **React Markdown** - Markdown渲染
- **Lucide Icons** - 图标库

## 🎨 功能特性

- ✅ 聊天式问答界面
- ✅ 实时消息流
- ✅ Markdown渲染支持
- ✅ 示例问题快速点击
- ✅ 加载状态提示
- ✅ 错误处理
- ✅ 响应式设计
- ✅ 自动滚动到最新消息

## 🔧 环境变量

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 构建生产版本

```bash
npm run build
npm run start
```

## 💡 使用示例

1. 启动Python后端：`python start_api.py --dev`
2. 启动Next.js前端：`npm run dev`
3. 访问 http://localhost:3000
4. 输入问题或点击示例问题

## 🐛 故障排查

### 问题：无法连接到后端

**解决方案**：
1. 确保Python FastAPI服务正在运行
2. 检查端口8000是否被占用
3. 验证 `.env.local` 中的 `NEXT_PUBLIC_API_URL` 配置

### 问题：样式不生效

**解决方案**：
```bash
rm -rf .next
npm run dev
```

## 📚 更多信息

- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [项目总览](../README.md)
