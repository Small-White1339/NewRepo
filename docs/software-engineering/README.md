# SmartHire 软件工程课程资料索引

这套资料用于后续编写课程报告、制作 PPT、分配组员工作和准备答辩。它以已提交的功能代码 **`e92e561`** 为基线，把需求、模块、数据、接口、流程、测试和图表关联起来。它是可复用的工程材料包，**不是已排版完成的 30 页课程报告**。

## 先看什么

| 文件 | 这是什么 | 后续怎么用 |
|---|---|---|
| [00 课程要求对照](00-course-checklist.md) | 原课程要求与材料位置的对应表 | 查漏补缺，避免只交代码和页面 |
| [01 范围与需求](01-scope-and-requirements.md) | 产品边界、角色权限、功能需求和典型用例 | 写项目概述、需求分析和验收标准 |
| [02 架构与模块](02-architecture-and-modules.md) | 模块职责、调用关系、代码入口和技术说明 | 写概要设计，快速定位代码 |
| [03 业务流程与 UML](03-processes-and-uml.md) | 分层 DFD、用例、顺序、状态和活动的解释 | 选择合适图表，说明业务行为 |
| [04 数据库与接口设计](04-data-and-api.md) | ER 关系、约束、数据量估算、接口规则 | 写数据库设计、接口设计与数据量分析 |
| [05 测试与质量](05-testing-and-quality.md) | 黑盒用例、白盒分支、测试映射和质量边界 | 写测试章节和验收记录 |
| [06 项目管理与交付](06-project-management.md) | 生命周期建议、WBS、相对周甘特图、配置管理与报价模板 | 填入真实成员、计划、工时和报价 |
| [07 报告与答辩使用指南](07-report-and-presentation.md) | 30 页以上报告框架、PPT 结构和答辩要点 | 把材料整理为最终作业 |
| [验证记录](verification.md) | 本次资料生成与检查的实际结果 | 区分“已经验证”和“计划验证” |

## 自动导出的代码参考

以下内容由 [导出脚本](../../scripts/export-engineering-reference.py) 读取源码和 ORM 元数据生成，不连接业务数据库。

- [数据库字段字典](reference/database-dictionary.md)：11 张业务表的字段、可空性、默认值、外键和枚举。
- [REST 接口目录](reference/api-inventory.md)：30 个方法与路径组合，标明后端权限依赖和函数位置。
- [自动化测试清单](reference/test-inventory.md)：29 个测试函数及源码入口。

## 图表目录

**SVG** 适合放大、打印和插入支持矢量图的 Word/PPT；**PNG** 适合直接粘贴；**图源** 用于修改和重新生成。每张图内部都有编号与名称。不要只贴图片：报告中应保留图名，并用一段话解释它解决的问题。

| 编号 | 图名与类型 | 主要用途 | 范围 | SVG / PNG / 图源 |
|---|---|---|---|---|
| F01 | 系统分层架构图 | 解释前端、业务、AI、数据与外部服务 | 当前实现 | [SVG](diagrams/svg/F01-system-architecture.svg) · [PNG](diagrams/png/F01-system-architecture.png) · [图源](diagrams/src/F01-system-architecture.puml) |
| F02 | 系统功能结构图 | 展示 M01–M08 模块与子功能 | 当前实现 | [SVG](diagrams/svg/F02-functional-structure.svg) · [PNG](diagrams/png/F02-functional-structure.png) · [图源](diagrams/src/F02-functional-structure.puml) |
| F03 | 软件包依赖图 | 说明源码目录与依赖方向 | 当前实现 | [SVG](diagrams/svg/F03-package-dependencies.svg) · [PNG](diagrams/png/F03-package-dependencies.png) · [图源](diagrams/src/F03-package-dependencies.puml) |
| F04 | 顶层 DFD | 明确系统与外部实体的数据边界 | 需求分析视图 | [SVG](diagrams/svg/F04-dfd-context.svg) · [PNG](diagrams/png/F04-dfd-context.png) · [图源](diagrams/src/F04-dfd-context.dot) |
| F05 | 一层 DFD | 分解业务处理与数据存储 | 需求分析视图 | [SVG](diagrams/svg/F05-dfd-level1.svg) · [PNG](diagrams/png/F05-dfd-level1.png) · [图源](diagrams/src/F05-dfd-level1.dot) |
| F06 | 二层 DFD | 细化 P4 匹配与报告处理 | 需求分析视图 | [SVG](diagrams/svg/F06-dfd-match-level2.svg) · [PNG](diagrams/png/F06-dfd-match-level2.png) · [图源](diagrams/src/F06-dfd-match-level2.dot) |
| F07 | HR UML 用例图 | 说明招聘人员的使用目标 | 当前实现 | [SVG](diagrams/svg/F07-hr-use-cases.svg) · [PNG](diagrams/png/F07-hr-use-cases.png) · [图源](diagrams/src/F07-hr-use-cases.puml) |
| F08 | 求职者 UML 用例图 | 说明个人匹配、收藏与求职准备 | 当前实现 | [SVG](diagrams/svg/F08-seeker-use-cases.svg) · [PNG](diagrams/png/F08-seeker-use-cases.png) · [图源](diagrams/src/F08-seeker-use-cases.puml) |
| F09 | 核心领域 UML 类图 | 展示实体对象和多重关系 | 当前模型 | [SVG](diagrams/svg/F09-domain-class.svg) · [PNG](diagrams/png/F09-domain-class.png) · [图源](diagrams/src/F09-domain-class.puml) |
| F10 | 数据库 ER 图 | 展示 11 张表及主外键关系 | 当前模型 | [SVG](diagrams/svg/F10-database-er.svg) · [PNG](diagrams/png/F10-database-er.png) · [图源](diagrams/src/F10-database-er.dot) |
| F11 | HR 匹配 UML 顺序图 | 说明批量请求中的单份分析子流程 | 当前实现 | [SVG](diagrams/svg/F11-hr-match-sequence.svg) · [PNG](diagrams/png/F11-hr-match-sequence.png) · [图源](diagrams/src/F11-hr-match-sequence.puml) |
| F12 | 求职匹配 UML 顺序图 | 说明个人报告创建、保存和查询 | 当前实现 | [SVG](diagrams/svg/F12-seeker-match-sequence.svg) · [PNG](diagrams/png/F12-seeker-match-sequence.png) · [图源](diagrams/src/F12-seeker-match-sequence.puml) |
| F13 | 照片解析 UML 顺序图 | 解释本地 OCR 与远端文字分析的分工 | 当前实现 | [SVG](diagrams/svg/F13-photo-upload-sequence.svg) · [PNG](diagrams/png/F13-photo-upload-sequence.png) · [图源](diagrams/src/F13-photo-upload-sequence.puml) |
| F14 | 匹配报告 UML 状态图 | 说明 PENDING、COMPLETED、FAILED | 当前实现 | [SVG](diagrams/svg/F14-match-state.svg) · [PNG](diagrams/png/F14-match-state.png) · [图源](diagrams/src/F14-match-state.puml) |
| F15 | 求职记录 UML 状态图 | 说明可自由切换的手动进度 | 当前实现 | [SVG](diagrams/svg/F15-saved-job-state.svg) · [PNG](diagrams/png/F15-saved-job-state.png) · [图源](diagrams/src/F15-saved-job-state.puml) |
| F16 | 照片解析 UML 活动图 | 说明文件校验、识字与失败处理 | 当前实现 | [SVG](diagrams/svg/F16-photo-activity.svg) · [PNG](diagrams/png/F16-photo-activity.png) · [图源](diagrams/src/F16-photo-activity.puml) |
| F17 | 本地运行 UML 部署图 | 说明端口、进程、文件与外部网络 | 已验证的本地方式 | [SVG](diagrams/svg/F17-local-deployment.svg) · [PNG](diagrams/png/F17-local-deployment.png) · [图源](diagrams/src/F17-local-deployment.puml) |
| F18 | Docker UML 部署图 | 说明 Compose 容器与卷 | 配置方案，未做容器验收 | [SVG](diagrams/svg/F18-docker-deployment.svg) · [PNG](diagrams/png/F18-docker-deployment.png) · [图源](diagrams/src/F18-docker-deployment.puml) |
| F19 | AI 流水线活动图 | 解释 5 个 Agent 类与 4 步执行 | 当前实现 | [SVG](diagrams/svg/F19-ai-pipeline.svg) · [PNG](diagrams/png/F19-ai-pipeline.png) · [图源](diagrams/src/F19-ai-pipeline.puml) |
| F20 | Git 配置管理流程图 | 展示验证、排密钥、提交与推送过程 | 工作流程说明，非 CI 平台 | [SVG](diagrams/svg/F20-configuration-workflow.svg) · [PNG](diagrams/png/F20-configuration-workflow.png) · [图源](diagrams/src/F20-configuration-workflow.dot) |
| F21 | 相对周甘特图 | 建议后续课程材料完善排期 | 建议计划，非实际工期 | [SVG](diagrams/svg/F21-relative-gantt.svg) · [PNG](diagrams/png/F21-relative-gantt.png) · [图源](diagrams/src/F21-relative-gantt.dot) |
| F22 | UI 页面导航图 | 说明两种角色的页面入口 | 当前实现 | [SVG](diagrams/svg/F22-ui-navigation.svg) · [PNG](diagrams/png/F22-ui-navigation.png) · [图源](diagrams/src/F22-ui-navigation.dot) |

## 后续维护与导出

1. 代码发生变化后，先更新本目录正文的实现说明，再运行元数据导出脚本。
2. 修改 `diagrams/src` 中的 PlantUML 或 Graphviz 文件，在本机导出 SVG 和 PNG。
3. 图源、导出图片和说明文档一并提交，避免图片与代码不一致。

渲染脚本会生成 [图片校验清单](diagrams/render-manifest.json)，记录图源、公共样式与 SVG/PNG 的 SHA256。文本先统一为 UTF-8 / LF 再计算，兼容 Windows 的 Git 换行转换。修改图源后若忘记重新导出，文档检查会提示不同步。

```powershell
# 在项目根目录，使用已安装依赖的 Python 环境
backend/.venv/Scripts/python.exe scripts/export-engineering-reference.py

# 需安装 Java、Graphviz，另行准备官方 PlantUML JAR
powershell -File scripts/render-engineering-diagrams.ps1 -PlantUmlJar <本机PlantUML路径>

# 检查目录链接、图像、图编号与自动导出结果
backend/.venv/Scripts/python.exe scripts/check-engineering-docs.py
```

本次渲染工具使用 PlantUML MIT 版本 `1.2026.9` 和 Graphviz；JAR 只放在本机缓存，不放进 Git。首次获取工具可参照 [PlantUML 官方下载说明](https://plantuml.com/download)，语法参照 [用例图说明](https://plantuml.com/use-case-diagram) 与 [命令行导出说明](https://plantuml.com/command-line)。图表在本机渲染，不使用在线图床。

**资料边界：**政策依据、真实用户单位组织结构、访谈记录、实际组员分工、真实工时、报价依据和 Docker 验收仍需要补充；不能把模板或建议当成已经调研、已经完成的事实。密钥、业务数据库、真实简历和本地日志不属于课程资料包。
