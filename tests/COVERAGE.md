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

## 2026-10-22 審查補強

- AUTH-004 兩個「顯示歡迎訊息」情境：`bdd/steps.py::welcome_message` 增加真實瀏覽器可見性／非空文字斷言；Scenario 函式不變。
- AUTH-005 Cookie 情境：`bdd/steps.py::opaque_session` 接上 `assertions.py::assert_cookie_has_no_sensitive_data`。
- AUTH-001／002／003 的兩種錯誤文案：原 HTTP 逐情境斷言保留，補充 `integration/test_visible_errors.py::test_login_error_is_visible` 的錯誤密碼／第三次鎖定瀏覽器案例。
- AUTH-007：保留原始 HTTP HTML SSR 檢查，不以瀏覽器 DOM 取代。
- `regression/test_review_assertions.py` 的 16 案例只覆蓋斷言缺口，不列為新增 Feature 或產品驗收通過。
