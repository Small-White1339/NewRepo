# REST 接口目录

代码基线：`e92e561`。由 `scripts/export-engineering-reference.py` 自动生成。只读取 ORM、路由和测试源代码，不连接业务数据库，不导出账号、简历或密钥。


权限列描述后端依赖；资源归属、岗位状态等业务检查详见正文和函数实现。前端入口可能比后端读取权限更窄。

| 方法 | 路径 | 权限依赖 | 实现位置 |
|---|---|---|---|
| `GET` | `/health` | 未登录可访问 | [backend/app/main.py:71](../../../backend/app/main.py#L71) `health_check` |
| `POST` | `/api/v1/auth/register` | 未登录可访问 | [backend/app/api/v1/auth.py:27](../../../backend/app/api/v1/auth.py#L27) `register` |
| `POST` | `/api/v1/auth/login` | 未登录可访问 | [backend/app/api/v1/auth.py:75](../../../backend/app/api/v1/auth.py#L75) `login` |
| `GET` | `/api/v1/users/me` | 登录用户 | [backend/app/api/v1/users.py:16](../../../backend/app/api/v1/users.py#L16) `get_current_user_profile` |
| `PUT` | `/api/v1/users/me` | 登录用户 | [backend/app/api/v1/users.py:27](../../../backend/app/api/v1/users.py#L27) `update_current_user_profile` |
| `POST` | `/api/v1/resumes/upload` | 登录用户 | [backend/app/api/v1/resumes.py:130](../../../backend/app/api/v1/resumes.py#L130) `upload_resume` |
| `GET` | `/api/v1/resumes/` | 登录用户 | [backend/app/api/v1/resumes.py:248](../../../backend/app/api/v1/resumes.py#L248) `list_resumes` |
| `GET` | `/api/v1/resumes/{resume_id}` | 登录用户 | [backend/app/api/v1/resumes.py:268](../../../backend/app/api/v1/resumes.py#L268) `get_resume` |
| `GET` | `/api/v1/resumes/{resume_id}/file` | 登录用户；文件预览兼容查询令牌 | [backend/app/api/v1/resumes.py:296](../../../backend/app/api/v1/resumes.py#L296) `get_resume_file` |
| `PUT` | `/api/v1/resumes/{resume_id}` | 登录用户 | [backend/app/api/v1/resumes.py:356](../../../backend/app/api/v1/resumes.py#L356) `update_resume` |
| `DELETE` | `/api/v1/resumes/{resume_id}` | 登录用户 | [backend/app/api/v1/resumes.py:399](../../../backend/app/api/v1/resumes.py#L399) `delete_resume` |
| `POST` | `/api/v1/resumes/{resume_id}/analyze` | 登录用户 | [backend/app/api/v1/resumes.py:422](../../../backend/app/api/v1/resumes.py#L422) `analyze_resume` |
| `POST` | `/api/v1/jobs/` | HR | [backend/app/api/v1/jobs.py:26](../../../backend/app/api/v1/jobs.py#L26) `create_job` |
| `GET` | `/api/v1/jobs/` | 登录用户 | [backend/app/api/v1/jobs.py:51](../../../backend/app/api/v1/jobs.py#L51) `list_jobs` |
| `GET` | `/api/v1/jobs/{job_id}` | 登录用户 | [backend/app/api/v1/jobs.py:77](../../../backend/app/api/v1/jobs.py#L77) `get_job` |
| `PUT` | `/api/v1/jobs/{job_id}` | HR | [backend/app/api/v1/jobs.py:98](../../../backend/app/api/v1/jobs.py#L98) `update_job` |
| `POST` | `/api/v1/jobs/{job_id}/analyze` | HR | [backend/app/api/v1/jobs.py:132](../../../backend/app/api/v1/jobs.py#L132) `analyze_job` |
| `DELETE` | `/api/v1/jobs/{job_id}` | HR | [backend/app/api/v1/jobs.py:248](../../../backend/app/api/v1/jobs.py#L248) `delete_job` |
| `POST` | `/api/v1/matches/analyze` | HR | [backend/app/api/v1/matches.py:29](../../../backend/app/api/v1/matches.py#L29) `analyze_match` |
| `GET` | `/api/v1/matches/` | 登录用户 | [backend/app/api/v1/matches.py:142](../../../backend/app/api/v1/matches.py#L142) `list_matches` |
| `GET` | `/api/v1/matches/{report_id}` | 登录用户 | [backend/app/api/v1/matches.py:159](../../../backend/app/api/v1/matches.py#L159) `get_match_report` |
| `POST` | `/api/v1/imports/jobs` | HR | [backend/app/api/v1/imports.py:42](../../../backend/app/api/v1/imports.py#L42) `import_jobs` |
| `POST` | `/api/v1/imports/resumes` | HR | [backend/app/api/v1/imports.py:66](../../../backend/app/api/v1/imports.py#L66) `import_resumes` |
| `GET` | `/api/v1/career/jobs` | 求职者 | [backend/app/api/v1/career.py:61](../../../backend/app/api/v1/career.py#L61) `browse_jobs` |
| `GET` | `/api/v1/career/jobs/{job_id}` | 求职者 | [backend/app/api/v1/career.py:89](../../../backend/app/api/v1/career.py#L89) `get_career_job` |
| `GET` | `/api/v1/career/saved` | 求职者 | [backend/app/api/v1/career.py:108](../../../backend/app/api/v1/career.py#L108) `list_saved` |
| `PUT` | `/api/v1/career/saved/{job_id}` | 求职者 | [backend/app/api/v1/career.py:122](../../../backend/app/api/v1/career.py#L122) `save_job` |
| `DELETE` | `/api/v1/career/saved/{job_id}` | 求职者 | [backend/app/api/v1/career.py:147](../../../backend/app/api/v1/career.py#L147) `remove_saved` |
| `POST` | `/api/v1/career/analyze` | 求职者 | [backend/app/api/v1/career.py:160](../../../backend/app/api/v1/career.py#L160) `analyze_career_match` |
| `GET` | `/api/v1/career/reports` | 求职者 | [backend/app/api/v1/career.py:201](../../../backend/app/api/v1/career.py#L201) `list_career_reports` |

共 **30 个方法与路径组合**，包含健康检查，不包含框架自带的文档页面。

登录响应提供 access_token 和 refresh_token，但当前没有 refresh 端点；不要把令牌自动刷新写成已实现功能。
`/users/me` 的修改资料接口已存在，当前前端没有独立的个人资料编辑页面。
`/jobs` 与 `/matches` 的部分 GET 依赖是登录用户，查询仍按用户资源归属过滤；求职者专用入口使用 `/career`。
本目录是代码参考，运行时完整请求 / 响应 Schema 可在本地 `/docs` 查看。
