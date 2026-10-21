@AUTH-003
Feature: AUTH-003 鎖定到期與失敗次數重設
  鎖定自第三次失敗起持續六十秒，到期後可再次嘗試登入。

  # specs/functional/functional-spec.md: FUNC-012～FUNC-013
  # specs/business/business-rules.md: BR-AUTH-002 第 5、7～8 項、BR-AUTH-003 第 2 項
  Scenario: 鎖定到期前仍拒絕正確密碼登入
    Given 一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定
    When 該帳號在時間 T 後 59 秒以正確密碼登入
    Then 系統拒絕登入
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

  # specs/functional/functional-spec.md: FUNC-013～FUNC-014
  # specs/business/business-rules.md: BR-AUTH-002 第 7～8 項
  Scenario Outline: 鎖定滿六十秒或之後可再次登入
    Given 一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定
    When 時間到達 T 後 <秒數> 秒且期間沒有其他登入嘗試
    Then 該帳號已自動解除鎖定
    And 該帳號的連續登入失敗次數為 0
    When 使用者以該帳號與正確密碼登入
    Then 系統允許登入
    And 系統導向 Welcome 頁面

    Examples:
      | 秒數 |
      | 60   |
      | 61   |

  # specs/functional/functional-spec.md: FUNC-010、FUNC-013～FUNC-014
  # specs/business/business-rules.md: BR-AUTH-002 第 8～9 項
  Scenario: 鎖定到期後的錯誤密碼從第一次失敗重新累計
    Given 一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定
    When 該帳號在時間 T 後 60 秒以錯誤密碼登入
    Then 系統拒絕登入
    And 登入頁面顯示「帳號或密碼錯誤」
    And 該帳號的連續登入失敗次數為 1
    And 該帳號未被鎖定
