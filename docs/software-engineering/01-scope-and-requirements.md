# 系统范围与需求说明

代码基线：`e92e561`。本章描述当前已实现的软件，不声称进行过真实企业访谈。产品定位是同时服务招聘人员和求职者的 AI 辅助工具：HR 管理自己的岗位和候选人简历；求职者管理自己的简历、探索在招岗位并获取准备建议。

## 产品范围

HR 的主要问题是候选人资料格式不一、岗位要求难以统一比较、逐份阅读和形成初步评估耗时。求职者的主要问题是难以判断简历与具体岗位的差距，也缺少把目标岗位、准备事项与个人进度放在一起的工具。这是课程场景的需求假设，仍应通过实际访谈或问卷验证。

系统支持文件文字提取、本地图片 OCR、AI 结构化分析、匹配评分和角色化报告。AI 结果用于人工参考；软件不做自动录用决定。没有站内投递、聊天、面试邀约发送、招聘方审核流程、支付、自动求职、独立平台管理员或向量知识库。

`admin` 是可选初始化的 HR 演示账号，不是第三种角色。公开履历只作为本人公开职业背景的参考，不代表本人在平台求职或已投递。

## 角色与权限

| 操作 | 未登录用户 | HR | 求职者 | 实际约束 |
|---|---|---|---|---|
| 注册、登录 | 可以 | 可以 | 可以 | 注册可选择两种角色；不是经审核的企业认证 |
| 管理简历、预览文件、AI 解析 | 不可以 | 本人账号下的简历 | 本人账号下的简历 | 按 `Resume.user_id` 隔离 |
| 创建、修改、删除、AI 分析岗位 | 不可以 | 本人岗位 | 不可以 | 后端 HR 依赖与所有权检查 |
| 使用岗位管理页面 | 不可以 | 可以 | 不可以 | `/jobs` 前端 HR 路由 |
| 探索在招岗位 | 不可以 | 无求职入口 | 可以 | `/career/jobs`；仅 ACTIVE，按来源链接去重 |
| HR 批量匹配 | 不可以 | 本人岗位与本人简历 | 不可以 | 1–20 个输入简历 ID，重复 ID 合并，无效项跳过 |
| 个人岗位匹配 | 不可以 | 不可以 | 本人简历与 ACTIVE 岗位 | `/career/analyze`，不要求岗位归本人所有 |
| 查询报告 | 不可以 | 本人简历产生的报告 | 本人简历产生的报告 | 通过简历所有者查询；并非仅按岗位发布者可见 |
| 导入公开岗位或职业履历 | 不可以 | 可以 | 不可以 | 固定来源，一小时冷却，保留来源 |
| 收藏、备注、手动求职进度 | 不可以 | 不可以 | 可以 | 按用户隔离，每用户每岗位唯一 |
| 修改账号资料 | 不可以 | 后端接口可用 | 后端接口可用 | 当前没有独立资料编辑页面 |

F07 与 F08 使用 UML 的参与者、系统边界、用例和 include 关系表达角色目标；更细的接口依赖见 [接口目录](reference/api-inventory.md)。

## 功能性需求

| 编号 | 用户可验收的需求 | 模块 / 实现入口 | 代表测试 |
|---|---|---|---|
| FR01 | 用户可注册、登录，未认证访问受保护资源被拒绝 | M01；`auth.py` / `deps.py` | `test_progress_input_validated_and_roles_enforced` |
| FR02 | 不同账号不能查看对方简历和文件 | M01 / M02；`resumes.py` | `test_same_filename_is_independent_and_owner_is_checked` |
| FR03 | 支持 PDF、DOCX、TXT、Markdown 与常见简历图片上传 | M02；`resume_parser.py` | `test_photo_upload_runs_ocr_and_auto_ai` |
| FR04 | 图片自动识别中英文原文，可核对识别文字 | M02；本地 RapidOCR | `test_real_ocr_engine_recognizes_text` |
| FR05 | 非法、空白图片被拒绝，不保留无效上传记录 | M02；`upload_resume` | `test_invalid_and_blank_photo_do_not_create_resume` |
| FR06 | 可预览或下载本人简历，DOCX 预览不执行嵌入 HTML | M02；`get_resume_file` | `test_docx_preview_escapes_html_and_download_has_filename` |
| FR07 | 可重新 AI 解析简历，替换旧关联资料 | M02；`analyze_resume` | `test_resume_reanalysis_replaces_relations_and_update_serializes` |
| FR08 | HR 可管理本人岗位并重新提取岗位要求 | M03；`jobs.py` | `test_job_reanalysis_refreshes_requirements` |
| FR09 | HR 可对有效简历批量匹配，逐项显示成功与失败 | M04；`matches.py` | `test_match_success_deduplicates_and_failure_is_persisted` |
| FR10 | AI 不可用时有明确错误，不生成假的成功分数 | M04；`base.py` / `career.py` | `test_failed_ai_does_not_fabricate_score_or_leak_error` |
| FR11 | HR 可导入真实岗位，来源可核验且不重复创建 | M05；`imports.py` | `test_job_import_attribution_dedup_and_cooldown` |
| FR12 | HR 可导入公开职业履历，移除联系方式并标注来源 | M05；`public_sources.py` | `test_public_resume_preserves_facts_and_removes_contacts` |
| FR13 | 求职者可按关键词和职级查找在招岗位 | M06；`browse_jobs` | `test_catalog_only_active_search_and_source_dedup` |
| FR14 | 求职者可用本人简历生成三项分数与准备建议 | M04 / M06；`analyze_career_match` | `test_match_own_resume_against_public_job_and_history_isolation` |
| FR15 | 求职者不能用他人简历或关闭岗位发起新匹配 | M01 / M06 | `test_cannot_match_foreign_resume_closed_job_or_missing_key` |
| FR16 | 收藏、个人备注和进度在刷新后保留，其他账号不可见 | M06；`SavedJob` | `test_saved_progress_is_private_persistent_and_closed_job_readable` |
| FR17 | 已收藏关闭岗位可继续查看、记录或归档 | M06；`get_career_job` / `save_job` | 同 FR16 测试 |
| FR18 | 求职者可查看本人历史报告，在页面按时间或分数排序 | M06；`Career.tsx` | 报告隔离有接口测试；排序仍需前端交互验收 |
| FR19 | 删除岗位时同步删除关联收藏与报告 | M03 / M08；ORM 关系 | `test_hr_deletion_cascades_saved_records_and_reports` |
| FR20 | 启动可执行迁移，旧岗位数据升级后仍保留 | M08；Alembic 与启动脚本 | `test_upgrade_existing_jobs_and_downgrade` |

表中的代表测试名可在 [测试清单](reference/test-inventory.md) 直接定位；“有测试”不等于所有输入、浏览器和部署环境均已覆盖。

## 非功能性需求

| 编号 | 需求与判定方式 | 当前证据或边界 |
|---|---|---|
| NFR01 安全与隔离 | 认证、角色和资源归属均由后端检查 | 已有跨账号、角色拒绝测试；未做渗透测试 |
| NFR02 文件约束 | 单文件最大 10 MB，图片最大 2500 万像素 | 代码约束与部分边界测试；不是无限大文件处理 |
| NFR03 错误可理解性 | 模型失败保留已识别原文，报告失败不显示成功分数 | 有失败路径测试；需人工核对所有页面文案 |
| NFR04 响应与并发 | 单次模型请求默认超时 60 秒；HR 批量并发默认 3 | 这是参数限制，**不是整体请求 60 秒内完成的 SLA**；流水线有 4 步和可能的重试 |
| NFR05 可维护性 | 锁文件、迁移、自动化测试、图源可版本管理 | 当前已具备；文档需要随代码持续更新 |
| NFR06 兼容性 | 本地 SQLite 与 Windows 启动已运行验证 | Docker / PostgreSQL 端到端、不同浏览器与多机访问待验收 |
| NFR07 性能 | 提交前约定并测量列表响应、OCR 耗时和并发能力 | 尚无压测、容量或性能百分位结果，不填写虚构指标 |
| NFR08 AI 可信度 | 保留原文、区分可选与必需要求，人工复核建议 | 提示词提供约束；仍可能误读，不宣称客观准确率或录用概率 |

## 典型用例说明

| 用例 | 前置条件 | 主成功场景 | 替代或异常场景 | 后置结果 |
|---|---|---|---|---|
| UC02 上传简历照片 | 已登录，照片含可读文字 | 选文件→校验→保存→OCR→可选 AI→展示原文与资料 | 400 非法格式、413 超限、422 无文字；AI 失败保留文字 | 有效简历为 PARSED；PARSED 不保证 AI 成功 |
| UC06 HR 批量匹配 | HR、本人岗位及至少一份有效简历、已配置 AI | 选择资源→去重校验→创建报告→分析→保存→逐项展示 | 无效简历跳过；全部无效返回 400；单份失败不伪造分数 | 每份有效简历产生一份完成或失败报告 |
| UC08 导入公开资料 | HR，当前类别最近一小时没有同步 | 请求固定来源→净化与去重→保留链接→持久化 | 429 冷却；全部来源失败返回 502；不编造替代数据 | HR 工作区增加或更新带来源的资料 |
| UC09 探索岗位 | 求职者登录 | 关键词 / 职级筛选→查看原文与采集时间 | 草稿不公开，关闭且未收藏的岗位详情不可见 | 不改变简历或岗位所有权 |
| UC10 个人岗位匹配 | 求职者、本人简历、ACTIVE 岗位、正文和 Key | 校验→提交 PENDING→4 步分析→展示三项评分与个人建议 | 404 / 422 / 503；AI 失败记录 FAILED，分数为空 | 本人可再次查询历史报告；不发送给招聘方 |
| UC11 收藏并记录进度 | 求职者，首次收藏时岗位 ACTIVE | 收藏→选择有效 stage→写备注→保存→刷新核对 | 关闭岗位可更新已有记录；草稿撤回后不允许更新 | 私有记录持久化，不等于实际投递或邀约 |
| UC12 查看历史报告 | 求职者，已有本人简历生成的报告 | 打开我的求职→匹配报告→排序→查看详情 | 失败报告显示失败；不存在他人报告入口 | 数据不变 |
| UC13 打开原招聘网页 | 存在 HTTP(S) 来源链接 | 点击链接，在外部网页继续操作 | 原网页可能失效或岗位已结束 | 软件不记录外部投递是否成功 |

## 尚未实现与不应扩写的内容

刷新令牌端点、忘记密码、企业身份审核、站内投递与招聘方反馈、自动面试安排、后台任务恢复、RAG/向量检索、自动推荐全站岗位排名、完整证书自动提取都不能写成既有能力。后续确需新增，应建立单独需求编号、修改代码并补测试与图表。
