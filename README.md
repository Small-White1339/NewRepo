# SmartHire - 智能招聘辅助系统

基于 AI Agent 的多智能体协作招聘系统，支持简历解析、岗位需求分析、候选人能力评估及岗位匹配推荐。

## 系统架构

```
┌─────────────────────────────────────────────┐
│                用户层                        │
│       React + shadcn/ui Web 界面            │
├─────────────────────────────────────────────┤
│                业务层                        │
│       FastAPI RESTful API                    │
├─────────────────────────────────────────────┤
│              AI Agent 层                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│  │简历分析│ │岗位分析│ │匹配分析│ │报告生成│      │
│  │Agent │ │Agent │ │Agent │ │Agent │      │
│  └──────┘ └──────┘ └──────┘ └──────┘      │
│           LangChain + DeepSeek               │
├─────────────────────────────────────────────┤
│                数据层                        │
│      SQLite (开发) / PostgreSQL (生产)       │
└─────────────────────────────────────────────┘
```

## 技术栈

| 层 | 技术 |
|---|------|
| 后端框架 | FastAPI (Python 3.12+) |
| 前端框架 | React 19 + TypeScript |
| UI 组件 | shadcn/ui (base-nova) + Tailwind CSS v4 |
| 图标 | lucide-react |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| ORM | SQLAlchemy 2.0 (async) |
| 迁移工具 | Alembic |
| AI 框架 | LangChain |
| LLM | DeepSeek (deepseek-chat) |
| 认证 | JWT (python-jose) |
| 项目管理 | uv (Python) + npm (前端) |
| 任务编排 | Taskfile.yml (go-task) |

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 22+
- uv（Python 包管理）
- go-task（Taskfile 运行器）

### 1. 克隆并安装依赖

```bash
# 后端
cd backend
uv sync

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

### 3. 初始化数据库

```bash
cd backend
uv run alembic upgrade head
```

首次启动时自动创建 `admin / admin` 管理员账户。

### 4. 启动开发服务

```bash
# 使用 Taskfile（同时启动前后端）
task dev

# 或分别启动
task backend:dev    # 后端 http://localhost:8000
task frontend:dev   # 前端 http://localhost:5173
```

## 功能模块

### 用户管理

- 注册 / 登录（JWT 认证）
- 角色：HR（招聘人员）、JOB_SEEKER（求职者）
- 默认管理员：`admin / admin`

### 简历管理

- 支持格式：PDF、DOCX、TXT、Markdown
- 自动文本提取 + AI 智能解析（姓名/联系方式/学历/技能/工作经历/教育经历/项目经历）
- 技能标签展示，关联报告级联删除
- 文件预览（PDF 内联 / DOCX 转 HTML / TXT/MD 文本）+ 文件下载

### 岗位管理

- 创建 / 编辑 / 删除岗位
- 职级：初级 / 中级 / 高级 / 专家
- 状态：草稿 / 发布中 / 已关闭
- AI 自动分析 JD 提取技能要求
- 关键词搜索 + 状态/职级过滤

### 匹配分析

- 多选简历 + 选择岗位 → 批量匹配
- 4 Agent 协作流水线（简历分析 → 岗位分析 → 匹配推荐 → 报告生成）
- 综合评分（0-100）+ 技能/经验匹配评分
- 优势与不足分析 + 面试建议 + 招聘建议

## LLM 配置

系统仅支持 DeepSeek，通过环境变量配置：

```env
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

## 项目结构

```
smarthire/
├── backend/
│   ├── app/
│   │   ├── agents/          # 4 AI Agent + Orchestrator 编排器
│   │   ├── api/v1/          # RESTful API 端点
│   │   ├── models/          # SQLAlchemy 2.0 async 模型
│   │   ├── schemas/         # Pydantic v2 请求/响应模型
│   │   ├── services/        # 业务逻辑（认证、简历解析）
│   │   ├── config.py        # pydantic-settings 配置
│   │   ├── database.py      # 异步数据库引擎
│   │   └── main.py          # FastAPI 应用入口
│   ├── alembic/             # 数据库迁移
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/             # axios API 客户端
│       ├── components/      # shadcn/ui 组件
│       ├── pages/           # 10 个页面
│       ├── hooks/           # React Hooks
│       └── types/           # TypeScript 类型（映射后端 Pydantic）
├── Taskfile.yml             # go-task 任务编排
└── docker-compose.yml       # Docker 部署
```

## 开发命令

| 命令 | 功能 |
|------|------|
| `task backend:dev` | 启动后端开发服务器（热重载） |
| `task frontend:dev` | 启动前端开发服务器 |
| `task dev` | 同时启动前后端 |
| `task backend:lint` | ruff 代码检查 |
| `task backend:format` | ruff 格式化 |
| `task backend:migrate` | 执行数据库迁移 |
| `task backend:migration name=xxx` | 创建新迁移 |
| `task backend:test` | 运行后端测试 |
| `task install` | 安装所有依赖 |
| `task build` | 构建所有服务 |
| `task docker:up` | Docker Compose 启动 |

## API 文档

启动后端后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 部署

### Docker

```bash
docker compose up -d --build
```

### 单独部署

```bash
# 后端
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run build
# 使用 nginx 或 docker 部署 dist/ 目录
```

## 许可证

MIT License
