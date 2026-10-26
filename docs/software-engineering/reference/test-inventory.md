# 自动化测试清单

代码基线：`e92e561`。由 `scripts/export-engineering-reference.py` 自动生成。只读取 ORM、路由和测试源代码，不连接业务数据库，不导出账号、简历或密钥。


本清单仅证明测试函数存在。实际执行结果见 [验证记录](../verification.md)，不代表覆盖率达到某一百分比。

| 编号 | 测试函数 | 源文件 |
|---|---|---|
| T01 | `test_missing_key_reports_configuration_error` | [backend/tests/test_agents.py:13](../../../backend/tests/test_agents.py#L13) |
| T02 | `test_first_llm_initialization_and_fenced_json` | [backend/tests/test_agents.py:19](../../../backend/tests/test_agents.py#L19) |
| T03 | `test_invalid_json_retries_and_never_returns_empty_success` | [backend/tests/test_agents.py:37](../../../backend/tests/test_agents.py#L37) |
| T04 | `test_network_failure_has_actionable_error` | [backend/tests/test_agents.py:54](../../../backend/tests/test_agents.py#L54) |
| T05 | `test_same_filename_is_independent_and_owner_is_checked` | [backend/tests/test_api.py:61](../../../backend/tests/test_api.py#L61) |
| T06 | `test_upload_limit_and_invalid_filter` | [backend/tests/test_api.py:76](../../../backend/tests/test_api.py#L76) |
| T07 | `test_docx_preview_escapes_html_and_download_has_filename` | [backend/tests/test_api.py:88](../../../backend/tests/test_api.py#L88) |
| T08 | `test_resume_reanalysis_replaces_relations_and_update_serializes` | [backend/tests/test_api.py:104](../../../backend/tests/test_api.py#L104) |
| T09 | `test_job_reanalysis_refreshes_requirements` | [backend/tests/test_api.py:120](../../../backend/tests/test_api.py#L120) |
| T10 | `test_job_seeker_cannot_write_recruitment_data` | [backend/tests/test_api.py:138](../../../backend/tests/test_api.py#L138) |
| T11 | `test_no_key_returns_503_and_preserves_previous_analysis` | [backend/tests/test_api.py:159](../../../backend/tests/test_api.py#L159) |
| T12 | `test_match_success_deduplicates_and_failure_is_persisted` | [backend/tests/test_api.py:176](../../../backend/tests/test_api.py#L176) |
| T13 | `test_seed_admin_uses_session_factory_and_is_idempotent` | [backend/tests/test_api.py:205](../../../backend/tests/test_api.py#L205) |
| T14 | `test_catalog_only_active_search_and_source_dedup` | [backend/tests/test_career.py:16](../../../backend/tests/test_career.py#L16) |
| T15 | `test_saved_progress_is_private_persistent_and_closed_job_readable` | [backend/tests/test_career.py:46](../../../backend/tests/test_career.py#L46) |
| T16 | `test_progress_input_validated_and_roles_enforced` | [backend/tests/test_career.py:71](../../../backend/tests/test_career.py#L71) |
| T17 | `test_match_own_resume_against_public_job_and_history_isolation` | [backend/tests/test_career.py:88](../../../backend/tests/test_career.py#L88) |
| T18 | `test_cannot_match_foreign_resume_closed_job_or_missing_key` | [backend/tests/test_career.py:131](../../../backend/tests/test_career.py#L131) |
| T19 | `test_failed_ai_does_not_fabricate_score_or_leak_error` | [backend/tests/test_career.py:156](../../../backend/tests/test_career.py#L156) |
| T20 | `test_hr_deletion_cascades_saved_records_and_reports` | [backend/tests/test_career.py:178](../../../backend/tests/test_career.py#L178) |
| T21 | `test_orchestrator_uses_career_coach_only_for_job_seekers` | [backend/tests/test_career.py:193](../../../backend/tests/test_career.py#L193) |
| T22 | `test_photo_upload_runs_ocr_and_auto_ai` | [backend/tests/test_images_and_sources.py:28](../../../backend/tests/test_images_and_sources.py#L28) |
| T23 | `test_invalid_and_blank_photo_do_not_create_resume` | [backend/tests/test_images_and_sources.py:55](../../../backend/tests/test_images_and_sources.py#L55) |
| T24 | `test_real_ocr_engine_recognizes_text` | [backend/tests/test_images_and_sources.py:70](../../../backend/tests/test_images_and_sources.py#L70) |
| T25 | `test_public_resume_preserves_facts_and_removes_contacts` | [backend/tests/test_images_and_sources.py:78](../../../backend/tests/test_images_and_sources.py#L78) |
| T26 | `test_job_import_attribution_dedup_and_cooldown` | [backend/tests/test_images_and_sources.py:101](../../../backend/tests/test_images_and_sources.py#L101) |
| T27 | `test_resume_import_without_llm_and_isolation` | [backend/tests/test_images_and_sources.py:131](../../../backend/tests/test_images_and_sources.py#L131) |
| T28 | `test_imports_are_hr_only_and_fail_without_fake_fallback` | [backend/tests/test_images_and_sources.py:155](../../../backend/tests/test_images_and_sources.py#L155) |
| T29 | `test_upgrade_existing_jobs_and_downgrade` | [backend/tests/test_migrations.py:11](../../../backend/tests/test_migrations.py#L11) |

当前共 **29 个测试函数**。测试使用临时数据库，模型服务主要使用模拟响应；OCR 另有真实本地引擎测试。
