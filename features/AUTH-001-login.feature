@AUTH-001
Feature: AUTH-001 會員登入與登入首頁
  會員透過登入表單提交憑證，系統依驗證結果提供一致的回應。

  # specs/functional/functional-spec.md: FUNC-001～FUNC-004
  Scenario: 登入首頁提供登入表單
    Given 使用者尚未登入
    When 使用者開啟登入首頁
    Then 頁面提供帳號輸入欄位
    And 頁面提供密碼輸入欄位
    And 頁面提供登入按鈕

  # specs/functional/functional-spec.md: FUNC-005～FUNC-007、FUNC-009
  # specs/business/business-rules.md: BR-AUTH-001 第 1～2 項
  Scenario: 正確的帳號與密碼可成功登入
    Given 存在一個未鎖定的會員帳號
    And 使用者位於登入首頁
    When 使用者透過登入表單提交該帳號與正確密碼
    Then 系統成功驗證會員
    And 系統建立該會員的登入狀態
    And 系統導向 Welcome 頁面

  # specs/functional/functional-spec.md: FUNC-005、FUNC-006、FUNC-008
  # specs/business/business-rules.md: BR-AUTH-001 第 3～4 項、BR-AUTH-002 第 2 項
  Scenario: 既有帳號第一次輸入錯誤密碼
    Given 存在一個未鎖定且連續登入失敗次數為 0 的會員帳號
    When 使用者透過登入表單提交該帳號與錯誤密碼
    Then 系統拒絕登入
    And 登入頁面顯示「帳號或密碼錯誤」

  # specs/functional/functional-spec.md: FUNC-006、FUNC-008
  # specs/business/business-rules.md: BR-AUTH-001 第 4 項、BR-AUTH-003 第 3 項
  Scenario: 不存在的帳號顯示相同的驗證失敗訊息
    Given 使用者輸入的帳號不存在
    When 使用者透過登入表單首次提交該帳號與密碼
    Then 系統拒絕登入
    And 登入頁面顯示「帳號或密碼錯誤」
    And 頁面不顯示專屬的「帳號不存在」訊息

  # specs/functional/functional-spec.md: FUNC-014
  # specs/business/business-rules.md: BR-AUTH-001 第 5 項、BR-AUTH-002 第 2～4 項
  Scenario: 成功登入重設連續失敗次數
    Given 存在一個未鎖定且連續登入失敗次數為 2 的會員帳號
    When 使用者以該帳號與正確密碼登入
    Then 系統允許登入
    And 該帳號的連續登入失敗次數為 0
    When 該帳號接著發生一次錯誤密碼登入嘗試
    Then 該帳號的連續登入失敗次數為 1
    And 該帳號未被鎖定
    And 登入頁面顯示「帳號或密碼錯誤」
