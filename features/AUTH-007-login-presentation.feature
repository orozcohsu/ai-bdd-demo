@AUTH-007
Feature: AUTH-007 登入頁與 Welcome 頁的伺服器端呈現
  網頁由伺服器產生 HTML，提供一致的登入體驗。

  # specs/technical/technical-spec.md: TECH-001 第 4～5 項
  Scenario: 登入首頁回應包含伺服器產生的表單 HTML
    Given 使用者尚未登入
    When 使用者請求登入首頁
    Then 伺服器回應的 HTML 包含帳號與密碼輸入欄位
    And 伺服器回應的 HTML 包含登入按鈕

  # specs/technical/technical-spec.md: TECH-001 第 4～5 項、UI-003
  # specs/business/business-rules.md: BR-AUTH-004 第 1～2 項
  Scenario: Welcome 頁回應包含伺服器產生的歡迎訊息
    Given 使用者已成功登入且登入狀態仍有效
    When 使用者請求 Welcome 頁面
    Then 伺服器回應的 HTML 包含歡迎訊息
