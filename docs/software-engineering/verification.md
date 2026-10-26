# 工程材料验证记录

代码基线：`e92e561`。本记录仅列实际执行的检查，不替代性能、覆盖率、Docker 或真实用户验收报告。

检查日期：2026-10-26。范围为本轮软件工程材料与辅助脚本。

## 本次检查范围

| 检查项 | 方法 | 结果记录 |
|---|---|---|
| 字段与关系 | 从 ORM 元数据重新导出字典与 ER 图源 | 通过；11 张业务表，含唯一索引与联合唯一约束 |
| 接口与权限依赖 | 静态解析路由注册、端点和 Depends | 通过；30 个方法与路径组合，包含健康检查 |
| 测试清单 | AST 解析 test 函数 | 通过；29 个函数，与源码逐项对应；未把数量当覆盖率 |
| 文档与源码链接 | 检查本地目标、Markdown 锚点和源码行号 | 通过；14 份 Markdown、238 个本地引用 |
| UML / DFD 等图源 | PlantUML 与 Graphviz 在本机渲染 | 通过；F01–F22 全部成功导出 |
| 导出图片 | SVG XML 校验、PNG 解码、图号与错误图检测、人工查看 | 通过；22 SVG + 22 PNG；已查看全套预览并单独复核调整图 |
| 图片与图源同步 | 对比图源、公共样式及图片 SHA256 | 通过；渲染清单与全部导出图一致 |
| 文档脚本语法 | Python 编译检查与 PowerShell 实际执行 | 通过；导出、链接检查与渲染脚本均执行成功 |
| Git 内容安全 | 全部提交候选及 85 个待提交文件扫描；排除配置、业务数据和工具缓存 | 通过，无密钥匹配；未包含业务数据库、上传资料或本地工具缓存 |

## 可复现方法

```powershell
backend/.venv/Scripts/python.exe scripts/export-engineering-reference.py
powershell -File scripts/render-engineering-diagrams.ps1 -PlantUmlJar <本机PlantUML路径>
backend/.venv/Scripts/python.exe scripts/check-engineering-docs.py
git diff --check
```

本次 PlantUML 使用官方 MIT 发布包 `1.2026.9`，下载文件 SHA256 为 `835b2f2eb1d756da3f03bffdbd0baf252b4b858547a741ac8e972958a09c7f91`。下载入口见 [PlantUML 官方下载页](https://plantuml.com/download)。JAR 与本机缓存不提交到仓库。

DOT 图片使用独立 Graphviz `14.1.5`；PlantUML 运行时报告的内嵌 Graphviz 为 `2.44.1`。渲染环境有 Java 21 与中文字体，不要求最终读者安装工具即可查看已导出的图片。

最终检查的关键输出：

```text
Exported 11 tables, 30 endpoints, 29 tests.
Checked 14 Markdown files, 238 local links, 22 diagram sources and 44 images.
ENGINEERING_DOCS_VALID=True
```

## 结果解释边界

自动导出“11 表、30 接口、29 测试”描述代码结构；测试数量不是覆盖率。图源全部渲染成功只说明图形语法可处理，还需人工核对业务含义。文档链接验证不自动保证外部网站永久可用。

本轮只新增工程材料与文档辅助脚本，不修改应用业务实现。此前已执行的应用测试与本轮资料校验应分开说明，避免把文档检查描述成重新完成了 Docker、模型准确率或大规模并发验收。
