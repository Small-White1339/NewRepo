# 数据库字段字典

代码基线：`e92e561`。由 `scripts/export-engineering-reference.py` 自动生成。只读取 ORM、路由和测试源代码，不连接业务数据库，不导出账号、简历或密钥。


共 **11 张业务表**，不包含 Alembic 的迁移版本表。


## `certificates`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `name` | `VARCHAR(255)` | 否 | 否 | — |
| `issuer` | `VARCHAR(255)` | 否 | 是 | — |
| `issued_date` | `DATE` | 否 | 是 | — |
| `url` | `VARCHAR(500)` | 否 | 是 | — |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_certificates_resume_id(resume_id)`。


## `educations`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `school` | `VARCHAR(255)` | 否 | 否 | — |
| `degree` | `VARCHAR(100)` | 否 | 是 | — |
| `field` | `VARCHAR(255)` | 否 | 是 | — |
| `start_date` | `DATE` | 否 | 是 | — |
| `end_date` | `DATE` | 否 | 是 | — |
| `description` | `TEXT` | 否 | 是 | — |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_educations_resume_id(resume_id)`。


## `job_requirements`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `job_id` | `CHAR(32)` | 否 | 否 | FK → `jobs.id` |
| `category` | `VARCHAR(10)` | 否 | 否 | — |
| `name` | `VARCHAR(255)` | 否 | 否 | — |
| `description` | `TEXT` | 否 | 是 | — |
| `importance` | `INTEGER` | 否 | 否 | 应用默认：5 |
| `is_mandatory` | `BOOLEAN` | 否 | 否 | 应用默认：False |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_job_requirements_job_id(job_id)`。

枚举 `category`：`SKILL` / `EDUCATION` / `EXPERIENCE` / `PROJECT`。


## `jobs`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `CHAR(32)` | 是 | 否 | 应用默认：uuid4 |
| `user_id` | `CHAR(32)` | 否 | 否 | FK → `users.id` |
| `title` | `VARCHAR(255)` | 否 | 否 | — |
| `source_name` | `VARCHAR(100)` | 否 | 是 | — |
| `source_url` | `VARCHAR(1000)` | 否 | 是 | — |
| `imported_at` | `DATETIME` | 否 | 是 | — |
| `company` | `VARCHAR(255)` | 否 | 否 | — |
| `raw_description` | `TEXT` | 否 | 是 | — |
| `structured_data` | `JSON` | 否 | 是 | — |
| `status` | `VARCHAR(6)` | 否 | 否 | 应用默认：JobStatus.DRAFT |
| `level` | `VARCHAR(12)` | 否 | 否 | 应用默认：JobLevel.INTERMEDIATE；数据库默认：INTERMEDIATE |
| `created_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |
| `updated_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_jobs_user_id(user_id)`。

枚举 `status`：`DRAFT` / `ACTIVE` / `CLOSED`。

枚举 `level`：`JUNIOR` / `INTERMEDIATE` / `SENIOR` / `EXPERT` / `UNSPECIFIED`。


## `match_reports`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `CHAR(32)` | 是 | 否 | 应用默认：uuid4 |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `job_id` | `CHAR(32)` | 否 | 否 | FK → `jobs.id` |
| `overall_score` | `FLOAT` | 否 | 是 | — |
| `result_data` | `JSON` | 否 | 是 | — |
| `status` | `VARCHAR(9)` | 否 | 否 | 应用默认：MatchStatus.PENDING |
| `created_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_match_reports_job_id(job_id)`；`普通索引 ix_match_reports_resume_id(resume_id)`。

枚举 `status`：`PENDING` / `COMPLETED` / `FAILED`。


## `projects`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `name` | `VARCHAR(255)` | 否 | 否 | — |
| `role` | `VARCHAR(100)` | 否 | 是 | — |
| `description` | `TEXT` | 否 | 是 | — |
| `tech_stack` | `JSON` | 否 | 是 | — |
| `start_date` | `DATE` | 否 | 是 | — |
| `end_date` | `DATE` | 否 | 是 | — |
| `url` | `VARCHAR(500)` | 否 | 是 | — |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_projects_resume_id(resume_id)`。


## `resumes`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `CHAR(32)` | 是 | 否 | 应用默认：uuid4 |
| `user_id` | `CHAR(32)` | 否 | 否 | FK → `users.id` |
| `title` | `VARCHAR(255)` | 否 | 否 | — |
| `source_name` | `VARCHAR(100)` | 否 | 是 | — |
| `source_url` | `VARCHAR(1000)` | 否 | 是 | — |
| `imported_at` | `DATETIME` | 否 | 是 | — |
| `file_path` | `VARCHAR(500)` | 否 | 否 | — |
| `raw_text` | `TEXT` | 否 | 是 | — |
| `parsed_data` | `JSON` | 否 | 是 | — |
| `status` | `VARCHAR(7)` | 否 | 否 | 应用默认：ResumeStatus.PENDING |
| `created_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |
| `updated_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_resumes_user_id(user_id)`。

枚举 `status`：`PENDING` / `PARSED` / `FAILED`。


## `saved_jobs`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `CHAR(32)` | 是 | 否 | 应用默认：uuid4 |
| `user_id` | `CHAR(32)` | 否 | 否 | FK → `users.id` |
| `job_id` | `CHAR(32)` | 否 | 否 | FK → `jobs.id` |
| `stage` | `VARCHAR(20)` | 否 | 否 | 应用默认：SAVED；数据库默认：SAVED |
| `notes` | `TEXT` | 否 | 否 | 应用默认：；数据库默认： |
| `created_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |
| `updated_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |

唯一约束：`user_id, job_id`。

索引：`普通索引 ix_saved_jobs_job_id(job_id)`；`普通索引 ix_saved_jobs_user_id(user_id)`。


## `skills`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `name` | `VARCHAR(100)` | 否 | 否 | — |
| `level` | `VARCHAR(50)` | 否 | 是 | — |
| `category` | `VARCHAR(100)` | 否 | 是 | — |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_skills_resume_id(resume_id)`。


## `users`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `CHAR(32)` | 是 | 否 | 应用默认：uuid4 |
| `username` | `VARCHAR(50)` | 否 | 否 | — |
| `email` | `VARCHAR(255)` | 否 | 否 | — |
| `hashed_password` | `VARCHAR(255)` | 否 | 否 | — |
| `role` | `VARCHAR(10)` | 否 | 否 | 应用默认：UserRole.JOB_SEEKER |
| `is_active` | `BOOLEAN` | 否 | 否 | 应用默认：True |
| `created_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |
| `updated_at` | `DATETIME` | 否 | 否 | 数据库默认：now() |

唯一约束：除主键外无表级唯一约束。

索引：`唯一索引 ix_users_email(email)`；`唯一索引 ix_users_username(username)`。

枚举 `role`：`HR` / `JOB_SEEKER`。


## `work_experiences`

| 字段 | ORM 类型 | 主键 | 可空 | 默认值或外键 |
|---|---|---|---|---|
| `id` | `INTEGER` | 是 | 否 | — |
| `resume_id` | `CHAR(32)` | 否 | 否 | FK → `resumes.id` |
| `company` | `VARCHAR(255)` | 否 | 否 | — |
| `title` | `VARCHAR(255)` | 否 | 否 | — |
| `description` | `TEXT` | 否 | 是 | — |
| `start_date` | `DATE` | 否 | 是 | — |
| `end_date` | `DATE` | 否 | 是 | — |
| `is_current` | `BOOLEAN` | 否 | 否 | 应用默认：False |

唯一约束：除主键外无表级唯一约束。

索引：`普通索引 ix_work_experiences_resume_id(resume_id)`。


## 字段解释注意事项

`UUID` 在 SQLite 中通常以字符类型存储，在 PostgreSQL 中使用对应 UUID 类型；上表显示 ORM 声明的通用类型。
`saved_jobs.stage` 是 `VARCHAR(20)`，允许值由 Pydantic 请求模型校验，不是数据库枚举。
`Resume` 的教育、技能、经历等使用子表，AI 全量结果另存 `parsed_data`；报告全量结果使用 JSON 字段 `result_data`。
`certificates` 表已建模并可序列化，但当前 `_populate_resume_relations` 没有写入证书的循环，不能宣称证书自动提取已完成。
`file_path` 保存上传文件位置；图片和原文件不作为数据库二进制字段保存。
业务关系由 ORM 的级联设置维护；SQLite 引擎当前没有显式设置 `PRAGMA foreign_keys=ON`，不要把 ORM 删除行为写成所有数据库环境均已强制启用外键级联。
