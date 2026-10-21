@AUTH-004
Feature: AUTH-004 Welcome 頁面與登入狀態
  只有成功登入的使用者可以存取 Welcome 頁面。

  # specs/functional/functional-spec.md: FUNC-007、FUNC-015～FUNC-016
  # specs/business/business-rules.md: BR-AUTH-004 第 1～2 項
  Scenario: 登入成功後顯示歡迎訊息
    Given 存在一個未鎖定的會員帳號
    When 使用者以該帳號與正確密碼登入
    Then 系統導向 Welcome 頁面
    And Welcome 頁面顯示歡迎訊息

  # specs/functional/functional-spec.md: FUNC-009、FUNC-015
  # specs/business/business-rules.md: BR-AUTH-004 第 1～3 項
  Scenario: 成功登入後維持登入狀態以存取 Welcome 頁面
    Given 使用者已成功登入且登入狀態仍有效
    When 使用者再次存取 Welcome 頁面
    Then 系統允許存取 Welcome 頁面
    And Welcome 頁面顯示歡迎訊息

  # specs/functional/functional-spec.md: FUNC-017
  # specs/business/business-rules.md: BR-AUTH-004 第 3～4 項
  Scenario: 未登入的使用者直接存取 Welcome 頁面
    Given 使用者尚未登入
    When 使用者直接存取 Welcome 頁面
    Then 系統不允許存取 Welcome 頁面
    And 系統導向登入首頁

  # specs/functional/functional-spec.md: FUNC-008、FUNC-017
  # specs/business/business-rules.md: BR-AUTH-001 第 3 項、BR-AUTH-004 第 3～4 項
  Scenario: 登入失敗後仍不得直接存取 Welcome 頁面
    Given 使用者尚未登入
    And 存在一個未鎖定且連續登入失敗次數為 0 的會員帳號
    When 使用者以該帳號與錯誤密碼登入
    Then 系統拒絕登入
    When 使用者直接存取 Welcome 頁面
    Then 系統不允許存取 Welcome 頁面
    And 系統導向登入首頁
