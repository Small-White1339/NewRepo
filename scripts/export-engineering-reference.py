"""从代码导出数据库字典、接口目录和测试清单，不读取业务数据库。"""

import ast
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-root", type=Path, default=ROOT / "docs/software-engineering")
args = parser.parse_args()
OUT = args.output_root / "reference"
sys.path.insert(0, str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["SECRET_KEY"] = "documentation-only-not-a-deployment-secret"

from loguru import logger

logger.remove()

from app.database import Base
from app.models import *  # noqa: F403, F401


def safe(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def write(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content.rstrip() + "\n", encoding="utf-8")


code_revision = subprocess.check_output(
    ["git", "log", "-1", "--format=%h", "--", "backend/app", "frontend/src"], cwd=ROOT
).decode().strip()
header = (
    f"代码基线：`{code_revision}`。由 `scripts/export-engineering-reference.py` 自动生成。"
    "只读取 ORM、路由和测试源代码，不连接业务数据库，不导出账号、简历或密钥。\n\n"
)

lines = ["# 数据库字段字典\n", header]
tables = sorted(Base.metadata.tables.values(), key=lambda t: t.name)
lines += [f"共 **{len(tables)} 张业务表**，不包含 Alembic 的迁移版本表。\n"]
for table in tables:
    lines += [f"\n## `{table.name}`\n", "| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |", "|---|---|---|---|---|"]
    for column in table.columns:
        notes = [f"FK → `{fk.target_fullname}`" for fk in column.foreign_keys]
        if column.default is not None:
            value = column.default.arg
            notes.append("应用默认：" + (getattr(value, "__name__", "函数") if callable(value) else safe(value)))
        if column.server_default is not None:
            notes.append("数据库默认：" + safe(column.server_default.arg))
        lines.append(f"| `{column.name}` | `{safe(column.type)}` | {'是' if column.primary_key else '否'} | {'是' if column.nullable else '否'} | {'；'.join(notes) or '—'} |")
    unique = []
    for constraint in table.constraints:
        if constraint.__class__.__name__ == "UniqueConstraint":
            unique.append(", ".join(c.name for c in constraint.columns))
    lines.append("\n唯一约束：" + ("；".join(f"`{x}`" for x in unique) or "除主键外无表级唯一约束") + "。\n")
    indexes = [
        ("唯一索引 " if index.unique else "普通索引 ")
        + index.name + "(" + ", ".join(c.name for c in index.columns) + ")"
        for index in sorted(table.indexes, key=lambda index: index.name)
    ]
    lines.append("索引：" + ("；".join(f"`{x}`" for x in indexes) or "无额外索引") + "。\n")
    enum_columns = [c for c in table.columns if getattr(c.type, "enums", None)]
    for column in enum_columns:
        lines.append(f"枚举 `{column.name}`：" + " / ".join(f"`{x}`" for x in column.type.enums) + "。\n")
lines += [
    "\n## 字段解释注意事项\n",
    "`UUID` 在 SQLite 中通常以字符类型存储，在 PostgreSQL 中使用对应 UUID 类型；上表显示 ORM 声明的通用类型。",
    "`saved_jobs.stage` 是 `VARCHAR(20)`，允许值由 Pydantic 请求模型校验，不是数据库枚举。",
    "`Resume` 的教育、技能、经历等使用子表，AI 全量结果另存 `parsed_data`；报告全量结果使用 JSON 字段 `result_data`。",
    "`certificates` 表已建模并可序列化，但当前 `_populate_resume_relations` 没有写入证书的循环，不能宣称证书自动提取已完成。",
    "`file_path` 保存上传文件位置；图片和原文件不作为数据库二进制字段保存。",
    "业务关系由 ORM 的级联设置维护；SQLite 引擎当前没有显式设置 `PRAGMA foreign_keys=ON`，不要把 ORM 删除行为写成所有数据库环境均已强制启用外键级联。",
]
write("database-dictionary.md", "\n".join(lines))


def dependency_names(node):
    return {
        item.args[0].id
        for item in ast.walk(node)
        if isinstance(item, ast.Call)
        and isinstance(item.func, ast.Name)
        and item.func.id == "Depends"
        and item.args
        and isinstance(item.args[0], ast.Name)
    }


router_tree = ast.parse((ROOT / "backend/app/api/v1/router.py").read_text(encoding="utf-8"))
router_modules = {
    alias.asname or alias.name: node.module
    for node in router_tree.body
    if isinstance(node, ast.ImportFrom)
    for alias in node.names
    if alias.name == "router"
}
sources = [(ROOT / "backend/app/main.py", "")]
for node in ast.walk(router_tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "include_router":
        alias = node.args[0].id
        prefix = next(ast.literal_eval(kw.value) for kw in node.keywords if kw.arg == "prefix")
        sources.append((ROOT / "backend" / (router_modules[alias].replace(".", "/") + ".py"), "/api/v1" + prefix))


lines = ["# REST 接口目录\n", header,
         "权限列描述后端依赖；资源归属、岗位状态等业务检查详见正文和函数实现。前端入口可能比后端读取权限更窄。\n",
         "| 方法 | 路径 | 权限依赖 | 实现位置 |", "|---|---|---|---|"]
route_count = 0
for source, prefix in sources:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    router_dependencies = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "router" for target in node.targets):
            router_dependencies.update(dependency_names(node))
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.upper()
            if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                continue
            path = prefix + ast.literal_eval(decorator.args[0])
            names = dependency_names(node.args) | router_dependencies
            role = "未登录可访问"
            if "get_current_hr" in names:
                role = "HR"
            elif "get_current_job_seeker" in names:
                role = "求职者"
            elif "get_current_user_from_query" in names:
                role = "登录用户；文件预览兼容查询令牌"
            elif "get_current_user" in names:
                role = "登录用户"
            file = source.relative_to(ROOT).as_posix()
            line = node.lineno
            route_count += 1
            lines.append(f"| `{method}` | `{path}` | {role} | [{file}:{line}](../../../{file}#L{line}) `{node.name}` |")
assert route_count >= 30, "接口导出不完整，请检查路由解析"
lines += [f"\n共 **{route_count} 个方法与路径组合**，包含健康检查，不包含框架自带的文档页面。\n",
          "登录响应提供 access_token 和 refresh_token，但当前没有 refresh 端点；不要把令牌自动刷新写成已实现功能。",
          "`/users/me` 的修改资料接口已存在，当前前端没有独立的个人资料编辑页面。",
          "`/jobs` 与 `/matches` 的部分 GET 依赖是登录用户，查询仍按用户资源归属过滤；求职者专用入口使用 `/career`。",
          "本目录是代码参考，运行时完整请求 / 响应 Schema 可在本地 `/docs` 查看。"]
write("api-inventory.md", "\n".join(lines))

lines = ["# 自动化测试清单\n", header,
         "本清单仅证明测试函数存在。实际执行结果见 [验证记录](../verification.md)，不代表覆盖率达到某一百分比。\n",
         "| 编号 | 测试函数 | 源文件 |", "|---|---|---|"]
count = 0
for path in sorted((ROOT / "backend/tests").glob("test_*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT).as_posix()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            count += 1
            lines.append(f"| T{count:02d} | `{node.name}` | [{rel}:{node.lineno}](../../../{rel}#L{node.lineno}) |")
lines.append(f"\n当前共 **{count} 个测试函数**。测试使用临时数据库，模型服务主要使用模拟响应；OCR 另有真实本地引擎测试。")
write("test-inventory.md", "\n".join(lines))
print(f"Exported {len(tables)} tables, {route_count} endpoints, {count} tests.")

# ER 图仅展示键和少量业务字段，完整属性在上方字典中。
from html import escape

er = [
    'digraph ER {',
    'graph [rankdir=LR, bgcolor="white", fontname="Microsoft YaHei", fontsize=20, label="F10 数据库 ER 图  键与关键业务字段", labelloc=t, pad=0.4, nodesep=0.6, ranksep=1.2];',
    'node [shape=plain, fontname="Microsoft YaHei", fontsize=13];',
    'edge [fontname="Microsoft YaHei", fontsize=11, color="#475569", dir=both, arrowtail=teetee, arrowhead=crowodot];',
]
for table in tables:
    rows = []
    for column in table.columns:
        if column.primary_key or column.foreign_keys or column.name in {"title", "name", "username", "role", "status", "stage", "overall_score", "school", "company"}:
            flag = "PK " if column.primary_key else "FK " if column.foreign_keys else ""
            rows.append(f'<TR><TD ALIGN="LEFT">{flag}{escape(column.name)}</TD><TD ALIGN="LEFT">{escape(str(column.type))}</TD></TR>')
    er.append(f'{table.name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6" COLOR="#64748B"><TR><TD COLSPAN="2" BGCOLOR="#DBEAFE"><B>{table.name}</B></TD></TR>{"".join(rows)}</TABLE>>];')
for table in tables:
    for column in table.columns:
        for fk in column.foreign_keys:
            er.append(f'{fk.column.table.name} -> {table.name} [label="{column.name}"];')
er += ['}']
src = OUT.parent / "diagrams/src/F10-database-er.dot"
src.parent.mkdir(parents=True, exist_ok=True)
src.write_text("\n".join(er) + "\n", encoding="utf-8")
