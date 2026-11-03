# Gherkin → 測試對應

所有 Outline 的 Examples 由 pytest-bdd 逐列參數化，不自行複製 Feature。

| Feature | Scenario / Outline | 測試檔案與函式 |
|---|---|---|
| AUTH-001 | 登入首頁提供登入表單 | [test_auth_001.py::test_form](bdd/test_auth_001.py) |
| AUTH-001 | 重設清空帳號與密碼並將鍵盤輸入焦點移至帳號欄 | [test_auth_001.py::test_reset](bdd/test_auth_001.py) |
| AUTH-001 | 正確的帳號與密碼可成功登入 | [test_auth_001.py::test_valid_login](bdd/test_auth_001.py) |
| AUTH-001 | 既有帳號第一次輸入錯誤密碼 | [test_auth_001.py::test_invalid_login](bdd/test_auth_001.py) |
| AUTH-001 | 不存在的帳號顯示相同的驗證失敗訊息 | [test_auth_001.py::test_missing_account](bdd/test_auth_001.py) |
| AUTH-001 | 不存在帳號重複登入不適用既有會員鎖定規則 | [test_auth_001.py::test_repeat_missing](bdd/test_auth_001.py) |
| AUTH-001 | 成功登入重設連續失敗次數 | [test_auth_001.py::test_reset_counter](bdd/test_auth_001.py) |
| AUTH-002 | 前兩次連續失敗只累計次數而不鎖定 | [test_auth_002.py::test_first_two_failures](bdd/test_auth_002.py) |
| AUTH-002 | 第三次連續失敗立即鎖定六十秒 | [test_auth_002.py::test_third_failure](bdd/test_auth_002.py) |
| AUTH-002 | 鎖定期間無論密碼是否正確均拒絕登入 | [test_auth_002.py::test_locked_passwords](bdd/test_auth_002.py) |
| AUTH-002 | 鎖定期間的登入嘗試不延長原鎖定期限 | [test_auth_002.py::test_fixed_deadline](bdd/test_auth_002.py) |
| AUTH-002 | 不同帳號的失敗次數分別計算 | [test_auth_002.py::test_separate_counts](bdd/test_auth_002.py) |
| AUTH-002 | 一個帳號被鎖定不影響另一帳號登入 | [test_auth_002.py::test_separate_locks](bdd/test_auth_002.py) |
| AUTH-003 | 鎖定到期前仍拒絕正確密碼登入 | [test_auth_003.py::test_before_expiry](bdd/test_auth_003.py) |
| AUTH-003 | 鎖定滿六十秒或之後可再次登入 | [test_auth_003.py::test_at_or_after_expiry](bdd/test_auth_003.py) |
| AUTH-003 | 鎖定到期後的錯誤密碼從第一次失敗重新累計 | [test_auth_003.py::test_failure_after_expiry](bdd/test_auth_003.py) |
| AUTH-004 | 登入成功後顯示歡迎訊息 | [test_auth_004.py::test_welcome_message](bdd/test_auth_004.py) |
| AUTH-004 | 成功登入後維持登入狀態以存取 Welcome 頁面 | [test_auth_004.py::test_session_access](bdd/test_auth_004.py) |
| AUTH-004 | 未登入的使用者直接存取 Welcome 頁面 | [test_auth_004.py::test_anonymous_access](bdd/test_auth_004.py) |
| AUTH-004 | 登入失敗後仍不得直接存取 Welcome 頁面 | [test_auth_004.py::test_failed_login_access](bdd/test_auth_004.py) |
| AUTH-005 | 密碼輸入不以明文顯示 | [test_auth_005.py::test_masked_password](bdd/test_auth_005.py) |
| AUTH-005 | 儲存的會員密碼使用安全雜湊 | [test_auth_005.py::test_password_hash](bdd/test_auth_005.py) |
| AUTH-005 | 登入處理不將密碼寫入日誌 | [test_auth_005.py::test_password_logs](bdd/test_auth_005.py) |
| AUTH-005 | HTTPS 登入後的 Session Cookie 具備保護屬性 | [test_auth_005.py::test_secure_cookie](bdd/test_auth_005.py) |
| AUTH-005 | 無有效 CSRF 證明的登入請求受到阻擋 | [test_auth_005.py::test_csrf](bdd/test_auth_005.py) |
| AUTH-005 | 登入處理發生內部錯誤時不洩漏系統細節 | [test_auth_005.py::test_internal_error](bdd/test_auth_005.py) |
| AUTH-006 | 應用程式重新啟動後保留連續登入失敗次數 | [test_auth_006.py::test_persist_count](bdd/test_auth_006.py) |
| AUTH-006 | 應用程式重新啟動後保留原鎖定期限 | [test_auth_006.py::test_persist_deadline](bdd/test_auth_006.py) |
| AUTH-006 | 瀏覽器端狀態不能解除伺服器鎖定 | [test_auth_006.py::test_fresh_browser](bdd/test_auth_006.py) |
| AUTH-006 | 同帳號的並行失敗不遺失累計次數 | [test_auth_006.py::test_concurrent_count](bdd/test_auth_006.py) |
| AUTH-007 | 登入首頁回應包含伺服器產生的表單 HTML | [test_auth_007.py::test_ssr_login](bdd/test_auth_007.py) |
| AUTH-007 | Welcome 頁回應包含伺服器產生的歡迎訊息 | [test_auth_007.py::test_ssr_welcome](bdd/test_auth_007.py) |

| AUTH-004 | 應用程式重新啟動後保留尚未到期的登入狀態 | [test_auth_004.py::test_session_survives_restart](bdd/test_auth_004.py) |
| AUTH-008 | 全量遷移保留全部應用資料及原有欄位值 | [test_auth_008.py::test_all_data](bdd/test_auth_008.py) |
| AUTH-008 | 遷移後既有會員可用原密碼登入 | [test_auth_008.py::test_original_password](bdd/test_auth_008.py) |
| AUTH-008 | 遷移保留失敗次數且下一次錯誤仍觸發原鎖定規則 | [test_auth_008.py::test_retained_failures](bdd/test_auth_008.py) |
| AUTH-008 | 遷移不提前解除鎖定也不延長原鎖定期限 | [test_auth_008.py::test_original_lock_deadline](bdd/test_auth_008.py) |
| AUTH-008 | 遷移後原瀏覽器可沿用尚未到期的 Session | [test_auth_008.py::test_original_session](bdd/test_auth_008.py) |
| AUTH-008 | 已過期的 Session 遷移後不會恢復有效登入 | [test_auth_008.py::test_expired_session](bdd/test_auth_008.py) |
| AUTH-008 | 目標存在同名會員時不直接覆寫原有資料 | [test_auth_008.py::test_target_conflict](bdd/test_auth_008.py) |

## 2026-10-22 審查補強

- AUTH-004 兩個「顯示歡迎訊息」情境：`bdd/steps.py::welcome_message` 增加真實瀏覽器可見性／非空文字斷言；Scenario 函式不變。
- AUTH-005 Cookie 情境：`bdd/steps.py::opaque_session` 接上 `assertions.py::assert_cookie_has_no_sensitive_data`。
- AUTH-001／002／003 的兩種錯誤文案：原 HTTP 逐情境斷言保留，補充 `integration/test_visible_errors.py::test_login_error_is_visible` 的錯誤密碼／第三次鎖定瀏覽器案例。
- AUTH-007：保留原始 HTTP HTML SSR 檢查，不以瀏覽器 DOM 取代。
- `regression/test_review_assertions.py` 的 16 案例只覆蓋斷言缺口，不列為新增 Feature 或產品驗收通過。

## MariaDB 增量覆蓋（2026-11-03）

依技術規格 v1.2、共用介面 v0.2、PR #14 head 77352e16af0c5193602248c320a171e0072ee6d2，以及本次對話明確核准。
共 40 個 Scenario／Outline、49 組展開案例；全部 Examples 保留。上表與實際 decorator 由既有 G1 靜態檢查交叉核對。
AUTH-001／002／003／005／007 的 Scenario 函式與斷言不變；共用 fixture 改用 MariaDB。

| 測試／情境 | 關鍵斷言與操作（相對 tests/） |
|---|---|
| test_auth_004::test_session_survives_restart | migration_steps.remember_expiry／access_before_expiry／unchanged_expiry：同 Cookie、新 lifespan、HTTP 200、原 expires_at；steps.welcome_message 真實瀏覽器可見 |
| test_auth_006::test_persist_count | steps.restart、count、is_locked、alert；重啟後原 2 次持久化，第三次真實錯誤登入鎖定 |
| test_auth_006::test_persist_deadline | steps.timed_restart、timed_login、lock_deadline；保留 T+60，T+59 拒絕，T+60 成功 |
| test_auth_006::test_fresh_browser | steps.clean_browser／assert_rejected／alert；全新真實瀏覽器不能解除鎖定 |
| test_auth_006::test_concurrent_count | steps.concurrent_failures／count／is_locked；兩個獨立 Client／CSRF、Barrier 同步、真實請求與累計狀態 |
| test_auth_008::test_all_data | MigrationSnapshot.assert_all_rows：全應用表 mapping、逐欄／逐列及數量；relationships 外鍵語意；expired_rows；來源及備份 SHA-256 不變 |
| test_auth_008::test_original_password | unchanged_hash：原 Argon2 字串完全相同；original_login／Harness.assert_success：原密碼、真實 CSRF、303、有效 Session、Welcome 200 |
| test_auth_008::test_retained_failures | retained_count=2 並逐欄比對；既有 wrong_login／is_locked／alert：下一錯誤立即鎖定，原錯誤訊息 |
| test_auth_008::test_original_lock_deadline | migrate_at_thirty：原 UTC deadline 與全部原資料；既有 timed_login：T+59 拒絕／T+60 成功 |
| test_auth_008::test_original_session | original_cookie：沒有重新登入且原 token 不變、Welcome 200；original_e 原 E；expires_at_e 在 E 拒絕並回登入頁 |
| test_auth_008::test_expired_session | preserved_expired：SQL 保留原資料及期限；expired_cookie／denied_welcome：HTTP 303、/login |
| test_auth_008::test_target_conflict | 真實 MigrationConflictError；target_unchanged：全部既有應用表原值、原雜湊、原計數，不只驗證回報旗標 |

其他既有情境的主要斷言：AUTH-001 form_fields、reset／focused／typed_username、success、all_errors、count；AUTH-002 count、is_locked、lock_deadline、named_count、a_still_locked；AUTH-003 timed_login、unlocked、count、success；AUTH-004 redirect_welcome、welcome_message、denied_welcome；AUTH-005 masked、real_hash、safe_logs、opaque_session、cookie_attribute、csrf_rejected、generic_error；AUTH-007 form_fields、submit_button、ssr_welcome。完整 Scenario 與函式一對一關係見上表，Steps 實作在 bdd/steps.py。

integration/test_contract.py 的雙應用隔離改為兩個真實 MariaDB 資料庫，同時驗證會員、帳號狀態、Session 與 HTTP 不洩漏；另兩項 Session TTL／CSRF 斷言保留。
regression/test_database_guards.py 有 6 組測試基礎設施安全案例，不是產品或 MariaDB 行為驗收。
