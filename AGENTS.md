# SmartHire — Agent Guide

## Repo structure

```
smarthire/
├── backend/
│   └── app/
│       ├── agents/       # 4 AI Agents + Orchestrator
│       ├── api/v1/       # FastAPI routes
│       ├── models/       # SQLAlchemy 2.0 async models
│       ├── schemas/      # Pydantic v2 request/response
│       ├── services/     # auth, resume_parser
│       ├── config.py     # pydantic-settings
│       └── main.py       # FastAPI entry + lifespan
├── frontend/
│   └── src/
│       ├── api/          # axios API client
│       ├── components/   # shadcn/ui components
│       ├── pages/        # 10 pages
│       └── types/        # TS → Pydantic mirror types
├── Taskfile.yml          # Dev task runner (go-task)
└── docker-compose.yml
```

## First-time setup

```bash
cd backend && uv sync
cd frontend && npm ci
cd backend && uv run alembic upgrade head  # creates DB
```

## Dev servers

```bash
task backend:dev    # uvicorn --reload :8000
task frontend:dev   # Vite :5173 (proxies /api → :8000)
task                # both concurrently
```

## Critical SQLAlchemy async rule

**Always use `selectinload()` for relationships when reading data that will be serialized.** Without it, lazy-loading in an async context raises `MissingGreenlet`. Both `.clear()` and `.append()` on relationship attributes trigger lazy loads — use `db.add()` with explicit FK instead.

```python
# ✅ Good
result = await db.execute(
    select(Job).options(selectinload(Job.requirements))
)
# ❌ Avoid — triggers lazy load → MissingGreenlet
await db.refresh(job)
job.requirements = []
```

## LLM config\n\nUses DeepSeek via `DEEPSEEK_API_KEY` in `.env`. Model: `deepseek-chat`.\n\nAgent structured output is done via manual JSON prompt + `json.loads()` + `Pydantic.model_validate()`.\n\n## Agent pipeline

4 agents chained by `Orchestrator.analyze()`:
```
ResumeAnalysisAgent → JobAnalysisAgent → MatchingRecommendationAgent → ReportGenerationAgent
```
Each agent uses `_call_llm_structured()` (JSON prompt → parse → validate, up to 2 attempts). Missing API keys, invalid output, or service failures raise `AgentError`; no empty success results are generated.

## Commands

```bash
task backend:lint        # ruff check + format check
task backend:format      # ruff format
task backend:migrate     # alembic upgrade head
task backend:migration name="desc"  # alembic revision --autogenerate
task backend:check       # import sanity test
task frontend:check      # tsc --noEmit + build
task install             # uv sync + npm install
task docker:up           # docker compose up -d --build
```

## Conventions

- **Code comments**: All in Chinese. Technical terms (Python, FastAPI, SQLAlchemy, DeepSeek) stay English.
- **Spec docs** (`.trellis/spec/`): Written in Chinese.
- **Frontend**: shadcn/ui (base-nova) + lucide-react icons. **No daisyUI or raw color tokens.** Use `cn()`, semantic CSS variables (`text-foreground`, `bg-background`).
- **Agent prompts**: English instructions + `IMPORTANT: All text output MUST be written in Simplified Chinese.`
- **Database**: SQLite local, PostgreSQL production. Chosen automatically by `DATABASE_URL`.
- **Git repos**: `IRA-JM/` (root, includes `.trellis/` spec) + `smarthire/` (app code). Both are independent git repos.

## Known gotchas

1. **MissingGreenlet**: Any ORM relationship access outside an explicit `selectinload()` in async context will crash. Fix: always use `selectinload()` on queries, never rely on lazy loading.
2. **`with_structured_output`**: ChatTongyi's implementation rejects `method=...` kwargs. Use manual JSON prompting instead.
3. **`.env` location**: Backend reads `.env` from `backend/` (working directory). Keep both `smarthire/.env` and `smarthire/backend/.env` in sync.
4. **Resume upload AI**: Without an API key, uploads still extract text, but AI analysis is skipped. Explicit analysis returns HTTP 503. Local admin seeding requires `SEED_ADMIN=true`; Docker defaults to false.
5. **Alembic env.py** overrides `sqlalchemy.url` from `settings.DATABASE_URL` at runtime. Don't edit the hardcoded URL in `alembic.ini`.
