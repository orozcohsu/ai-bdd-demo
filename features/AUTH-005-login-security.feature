@AUTH-005
Feature: AUTH-005 登入安全與 Session 保護
  登入狀態由伺服器管理，避免密碼及機密資訊洩漏。

  # specs/technical/technical-spec.md: UI-002 第 2 項
  Scenario: 密碼輸入不以明文顯示
    Given 使用者位於登入首頁
    When 使用者在密碼欄位輸入測試密碼
    Then 密碼欄位不以明文顯示輸入內容

  # specs/technical/technical-spec.md: SEC-001 第 1～2 項
  Scenario: 儲存的會員密碼使用安全雜湊
    Given 隔離測試環境中有一個已建立的會員帳號
    When 檢查該帳號儲存的密碼驗證資料
    Then 資料不包含明文密碼
    And 密碼驗證資料使用安全的密碼雜湊演算法

  # specs/technical/technical-spec.md: SEC-001 第 3 項
  Scenario Outline: 登入處理不將密碼寫入日誌
    Given 存在一個未鎖定的會員帳號
    When 使用者以該帳號及<密碼類型>進行登入
    Then 本次處理產生的日誌不包含輸入的明文密碼

    Examples:
      | 密碼類型 |
      | 正確密碼 |
      | 錯誤密碼 |

  # specs/technical/technical-spec.md: SEC-002 第 1～3 項
  Scenario: HTTPS 登入後的 Session Cookie 具備保護屬性
    Given 隔離測試環境使用 HTTPS
    And 存在一個未鎖定的會員帳號
    When 使用者以該帳號與正確密碼登入
    Then 登入狀態由伺服器端 Session 管理
    And 瀏覽器僅保存不含敏感資料的 Session ID 作為登入憑證
    And Session Cookie 設定 HttpOnly
    And Session Cookie 設定 SameSite
    And Session Cookie 設定 Secure

  # specs/technical/technical-spec.md: SEC-004 第 2 項
  Scenario: 無有效 CSRF 證明的登入請求受到阻擋
    Given 存在一個未鎖定的會員帳號
    When 使用者提交正確帳號與密碼但未提供有效的 CSRF 證明
    Then 系統不接受該請求完成登入
    And 系統不建立該請求的登入狀態

  # specs/technical/technical-spec.md: SEC-004 第 5 項
  Scenario: 登入處理發生內部錯誤時不洩漏系統細節
    Given 登入處理過程發生可控制的內部系統錯誤
    When 系統回應使用者的登入請求
    Then 回應不包含機密資訊
    And 回應不包含詳細系統錯誤
