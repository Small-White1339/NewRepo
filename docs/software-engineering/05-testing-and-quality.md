# 测试设计与质量说明

代码基线：`e92e561`。当前自动化测试共 29 个函数，清单见 [测试索引](reference/test-inventory.md)。测试使用临时 SQLite 数据库与上传目录，模型结果大多使用模拟对象；另有真实本地 OCR 测试。实际执行结果单列于 [验证记录](verification.md)，不能把“存在测试”写成“所有场景均已验证”。

## 测试层次与需求关联

| 层次 | 关注点 | 现有证据 | 仍需补充 |
|---|---|---|---|
| Agent 单元与编排测试 | 缺 Key、首次初始化、围栏 JSON、格式重试、服务异常、角色化最后一步 | test_agents.py；test_career.py 的编排测试 | 模型对更多真实样本的事实准确性评估 |
| API 集成测试 | 认证、权限、所有权、上传、再分析、来源导入、个人匹配与收藏 | test_api.py、test_images_and_sources.py、test_career.py | 更多并发、输入边界和运行中断场景 |
| 数据迁移测试 | 旧岗位升级与回退时保留数据 | test_migrations.py | PostgreSQL 实例上的迁移和部署验收 |
| 本地 OCR 测试 | 真实引擎能识别生成图中的文字 | test_real_ocr_engine_recognizes_text | 倾斜、低分辨率、复杂排版的真实样本集 |
| 浏览器验收 | 页面入口、上传、搜索、收藏、报告展示 | 已做本地操作验证；截图需按课程采集 | 不同浏览器、键盘操作、排序与完整移动端矩阵 |

## 黑盒示例 个人匹配的输入与输出

**测试对象：**`POST /api/v1/career/analyze`。黑盒方法只根据输入与可观察结果判断，不依赖内部如何调用 Agent。使用独立测试账号与测试资源；AI 成功 / 失败由可控模拟对象提供，避免把外部服务随机性混入接口验收。

| 用例 | 输入条件 | 期望输出与可见后置条件 | 对应自动化测试 |
|---|---|---|---|
| BB01 正常个人匹配 | 求职者、本人的有正文简历、ACTIVE 岗位、有 Key、有效 AI 结果 | 201、COMPLETED、真实返回分数、历史可查询 | test_match_own_resume_against_public_job_and_history_isolation |
| BB02 未登录 | 无令牌，其余请求字段有效 | 401，不出现可见报告 | test_progress_input_validated_and_roles_enforced 验证未登录入口；该 POST 组合仍需补专用断言 |
| BB03 错误角色 | HR 调用 career/analyze | 403 | test_progress_input_validated_and_roles_enforced |
| BB04 其他账号简历 | 求职者给出 HR 或他人 resume_id | 404，不调用模型，不新增报告 | test_cannot_match_foreign_resume_closed_job_or_missing_key |
| BB05 已关闭岗位 | 本人简历与 CLOSED 岗位 | 404，不调用模型 | 同 BB04 测试 |
| BB06 缺少 Key | 其他条件有效但 Key 为空 | 503，不创建报告 | 同 BB04 测试 |
| BB07 AI 异常 | 业务校验通过，AI 抛出异常 | 201、FAILED、分数 null、不向用户泄漏内部异常 | test_failed_ai_does_not_fabricate_score_or_leak_error |
| BB08 其他账号查报告 | 他人尝试查询刚生成的报告 | 历史列表为空；报告详情访问 404 | test_match_own_resume_against_public_job_and_history_isolation |

表中“期望”是验收标准；“对应测试”说明当前覆盖到哪一部分。最终报告应把选定用例的实际状态码、截图或测试输出补在旁边，不要把尚未跑的手工步骤填为通过。

### 边界值与等价类补充

- 文件大小：0 字节、上限以下、恰好 10 MB、10 MB 加 1 字节；现有测试用缩小后的配置模拟超限，并未逐项使用真实 10 MB 文件。
- 图片：有效 JPG/PNG、内容损坏、空白图片、不支持真实格式、像素恰好上限与超限。已有有效、损坏、空白路径，其他边界需补充。
- 批量简历：1、20、0、21 个 ID，重复 ID、部分无效、全部无效。当前请求模型限制与部分去重 / 失败场景已有测试，完整边界矩阵尚未补齐。
- 求职记录：合法 stage、非法 stage、null、4000 字备注和 4001 字备注；已有非法 stage、null 和超长备注测试。

## 白盒示例 个人匹配的判定分支

**测试对象：**[analyze_career_match](../../backend/app/api/v1/career.py)。白盒分析关注代码中的判定与异常分支，不直接把需求流程图当作代码覆盖报告。

| 判定或路径 | 触发条件 | 当前测试 / 待补情况 |
|---|---|---|
| C1 active_job 查询为空 | 岗位不存在或不再 ACTIVE | 关闭岗位路径已覆盖；完全不存在 UUID 的专门用例可补 |
| C2 resume 查询为空 | 简历不属于本人或不存在 | 他人简历路径已覆盖 |
| C3 简历或岗位正文为空 | `not resume.raw_text or not job.raw_description` | 当前缺专用测试；还需分别覆盖 OR 两个操作数 |
| C4 未配置 AI Key | 其他资源有效但 Key 为空 | 缺 Key 路径已覆盖 |
| C5 分析正常返回 | Orchestrator 返回有效结果 | 完成报告与个人建议路径已覆盖 |
| C6 分析抛出异常 | 任一步骤失败 | FAILED、空分数和通用错误路径已覆盖 |
| C7 报告持久化后查询 | 由本人和他人分别请求 | 历史存在与隔离路径已覆盖 |

**白盒结论：**现有测试覆盖了主要成功与失败分支，但 C3 和部分组合尚有缺口。没有运行覆盖率工具，因此不声称语句、分支或条件覆盖率为 100%。如果老师要求覆盖率，应固定工具与测试版本，保存实际 coverage 报告，再更新此处。

其他可选白盒例子是 `BaseAgent._call_llm_structured`：第一次输出无效 JSON、第二次仍不满足 Schema 时应抛 AgentError；网络异常走另一条失败分支；有效围栏 JSON 应被解析。这些路径在 test_agents.py 中已有测试。

## 测试执行方法

```powershell
cd backend
uv sync --extra dev
uv run --extra dev pytest tests/ -q
uv run --extra dev ruff check app/
uv run --extra dev ruff format app/ --check

cd ../frontend
npm ci
npm run build
```

Windows 的具体本地虚拟环境也可执行相同模块。出现测试临时目录权限问题时选择新的临时目录；不要删除业务数据库来“修复测试”。测试样本不使用真实私人简历，不把模型 Key 写进测试文件。

## 质量限制与后续验收

尚未完成独立压测、安全渗透、所有浏览器兼容、Docker/PostgreSQL 端到端、多用户并发导入和进程中断恢复验收。模型输出仍需人工核对原文，尤其是任选语言、学历和加分项。自动化测试主要证明程序行为符合约定，不能证明模型在全部真实简历上的结论准确。
