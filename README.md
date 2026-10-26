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
npm ci
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

本地示例配置启用了 `SEED_ADMIN=true`，首次启动服务时创建 `admin / admin` 演示账户。默认配置及 Docker 部署不创建该账户；可在注册页面选择 HR 角色创建招聘人员账户。公开部署前请设置随机 `SECRET_KEY`，并关闭演示账户初始化。

### 4. 启动开发服务

Windows 已安装依赖时，双击项目根目录的 `启动软件.cmd`，或运行 `powershell -File scripts/start-local.ps1`。
脚本会创建缺失的 `backend/.env`（含随机本地 JWT 密钥）、执行数据库迁移，并在后台启动前后端。
访问 http://127.0.0.1:5180；使用 `停止软件.cmd` 关闭本项目启动的服务。运行日志保存在 `.local-run/`。
示例简历位于 `demo/示例简历.txt`，仅含虚构数据。

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
- 本地演示账户：`admin / admin`（仅 `SEED_ADMIN=true` 时创建）
- HR 可管理自己的岗位、上传候选人简历并执行匹配；求职者可管理自己的简历

### 简历管理

- 支持格式：PDF、DOCX、TXT、Markdown
- 自动文本提取 + AI 智能解析（姓名/联系方式/学历/技能/工作经历/教育经历/项目经历）
- 技能标签展示，关联报告级联删除
- 文件预览（PDF 内联 / DOCX 转 HTML / TXT/MD 文本）+ 文件下载
- 支持简历照片（JPG、JPEG、PNG、WEBP、BMP）：本地 RapidOCR 识别中英文文字，随后调用已有 DeepSeek 分析流程；详情页可核对识别原文。每个文件最多 10 MB、图片最多 2500 万像素。
- HR 可点击“导入公开简历”读取 JSON Resume 本人公开维护的职业履历，保留来源和采集日期，移除联系方式；这些资料不代表本人正在求职或向本平台投递。

### 岗位管理

- 创建 / 编辑 / 删除岗位
- 职级：初级 / 中级 / 高级 / 专家
- 状态：草稿 / 发布中 / 已关闭
- AI 自动分析 JD 提取技能要求
- 关键词搜索 + 状态/职级过滤
- HR 可点击“同步真实岗位”读取 Palantir、Spotify 在 Lever 官方公开的招聘信息，每个来源最多 30 条。岗位保留原文和原始链接；未注明的统一标记“以原始岗位说明为准”，不编造职级。每小时最多同步一次，同一来源不会重复创建。

公开简历和岗位的来源清单见 [公开数据来源说明](docs/public-data-sources.md)。数据只保存到本地业务数据库与上传目录，不作为演示数据提交到 Git；已有虚构演示记录仍保留明确的演示标记。

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

未配置 API Key 时，仍可登录、管理岗位和上传简历提取文本。主动 AI 分析返回明确的配置错误；模型调用失败或连续两次返回无效数据时，分析标记失败，不会生成空的成功报告。`LLM_TIMEOUT_SECONDS` 控制单次模型请求超时，`MATCH_CONCURRENCY` 控制批量匹配并发数（默认 3）。

### 回归测试

```bash
cd backend
uv sync --extra dev
uv run --extra dev pytest tests/
```

测试使用独立 SQLite 数据库、临时上传目录和模拟 AI 响应，不需要真实 API Key。覆盖认证、角色权限、上传大小限制、同名文件、DOCX 预览转义、重复分析替换数据和匹配成功/失败状态。

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

### 求职者使用流程

注册时选择“求职者”，登录后可使用以下功能：

1. **我的简历**：上传文本、PDF、Word 或简历照片，查看解析结果。
2. **岗位探索**：浏览 HR 发布为“招聘中”的岗位，包括已导入的真实公开岗位；按岗位、公司、技能、城市关键词和职级筛选，保留来源与采集日期。
3. **岗位匹配度**：打开岗位，选择自己的简历，获取综合、技能、经验三个分数，以及已有优势、差距、简历修改建议、技能提升计划和面试准备清单。分数表示岗位适配程度，不是录用概率。
4. **我的求职**：收藏岗位，手动记录“已收藏 / 已投递 / 面试中 / 收到录用 / 已归档”和个人备注；查看历史报告，并按匹配度或时间排序。
5. **原站投递**：通过岗位来源链接前往招聘网站实际投递。本软件的进度记录不向招聘方发送简历，也不会自动确认投递结果。

求职者只能使用自己的简历，收藏、备注和匹配报告按账号隔离。HR 管理入口保留原有权限。草稿岗位不会展示；已收藏的关闭岗位可以继续查看和归档，但不能新建匹配分析。没有 AI Key 时仍可浏览和收藏；AI 分析不可用时会显示错误，不生成虚构分数。

新增业务接口位于 `/api/v1/career`：`jobs`（浏览 / 详情）、`saved`（收藏 / 进度 / 移除）、`analyze`（个人匹配）、`reports`（个人报告）。启动脚本会自动执行新增的收藏表迁移。

API 是不同程序之间的通信接口。本软件中有三类：

| API | 主要作用 | 是否需要你的 DeepSeek Key |
|---|---|---|
| 本地业务 API `/api/v1` | 网页向后端请求登录、上传、查询和保存简历、岗位、报告 | 否，使用本地登录令牌 |
| DeepSeek API | 将简历文字和岗位要求转换为结构化数据，评估匹配并生成报告 | 是 |
| Lever / JSON Resume 公开 API | 获取可核验的真实岗位和本人公开职业履历 | 否 |

图片文字识别（OCR）在本机运行，不依赖 DeepSeek 识图接口。开启 AI 分析后，识别出的文字会发送到 DeepSeek；照片原件保留在本机。DeepSeek Key 只保存在后端 `.env`，前端不会获得该密钥。

启动后端后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 部署

### Docker

```bash
cp .env.example .env
# 编辑根目录 .env，设置 SECRET_KEY 与 DEEPSEEK_API_KEY
docker compose up -d --build
```

本地运行使用 `backend/.env`；Docker Compose 使用项目根目录 `.env`。依赖锁文件 `backend/uv.lock` 和 `frontend/package-lock.json` 必须一起提交。Docker 构建会排除本地虚拟环境、上传文件和环境配置文件。

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
