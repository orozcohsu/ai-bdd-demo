@AUTH-002
Feature: AUTH-002 連續登入失敗與帳號鎖定
  同一帳號第三次連續登入失敗立即鎖定，鎖定期間拒絕登入。

  # specs/functional/functional-spec.md: FUNC-008、FUNC-010～FUNC-011
  # specs/business/business-rules.md: BR-AUTH-002 第 1～3 項
  Scenario Outline: 前兩次連續失敗只累計次數而不鎖定
    Given 存在一個未鎖定且連續登入失敗次數為 <原次數> 的會員帳號
    When 使用者以該帳號與錯誤密碼登入
    Then 系統拒絕登入
    And 登入頁面顯示「帳號或密碼錯誤」
    And 該帳號的連續登入失敗次數為 <新次數>
    And 該帳號未被鎖定

    Examples:
      | 原次數 | 新次數 |
      | 0      | 1      |
      | 1      | 2      |

  # specs/functional/functional-spec.md: FUNC-010～FUNC-011
  # specs/business/business-rules.md: BR-AUTH-002 第 4、7 項、BR-AUTH-003 第 1 項
  Scenario: 第三次連續失敗立即鎖定六十秒
    Given 存在一個未鎖定且連續登入失敗次數為 2 的會員帳號
    When 該帳號在時間 T 以錯誤密碼登入
    Then 系統拒絕登入
    And 該帳號立即被鎖定
    And 鎖定期間從時間 T 開始持續 60 秒
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

  # specs/functional/functional-spec.md: FUNC-012
  # specs/business/business-rules.md: BR-AUTH-002 第 5 項、BR-AUTH-003 第 2 項
  Scenario Outline: 鎖定期間無論密碼是否正確均拒絕登入
    Given 一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定
    When 該帳號在時間 T 後 30 秒以<密碼類型>登入
    Then 系統拒絕登入
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

    Examples:
      | 密碼類型 |
      | 正確密碼 |
      | 錯誤密碼 |

  # specs/functional/functional-spec.md: FUNC-012～FUNC-013
  # specs/business/business-rules.md: BR-AUTH-002 第 6～8 項
  Scenario: 鎖定期間的登入嘗試不延長原鎖定期限
    Given 一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定
    When 該帳號在時間 T 後 30 秒以錯誤密碼登入
    Then 系統拒絕登入
    When 該帳號在時間 T 後 60 秒以正確密碼登入
    Then 系統允許登入
    And 系統導向 Welcome 頁面

  # specs/functional/functional-spec.md: FUNC-010～FUNC-012
  # specs/business/business-rules.md: BR-AUTH-002 第 10 項
  Scenario: 不同帳號的失敗次數分別計算
    Given 會員帳號 A 與 B 均未鎖定且連續登入失敗次數均為 0
    When 帳號 A 連續發生 2 次錯誤密碼登入嘗試
    And 帳號 B 發生 1 次錯誤密碼登入嘗試
    Then 帳號 A 的連續登入失敗次數為 2
    And 帳號 B 的連續登入失敗次數為 1
    And 帳號 A 與 B 均未被鎖定

  # specs/functional/functional-spec.md: FUNC-006、FUNC-010～FUNC-012
  # specs/business/business-rules.md: BR-AUTH-002 第 10 項
  Scenario: 一個帳號被鎖定不影響另一帳號登入
    Given 會員帳號 A 已被鎖定且仍在鎖定期間
    And 會員帳號 B 未鎖定且連續登入失敗次數為 0
    When 使用者以帳號 B 與正確密碼登入
    Then 系統允許帳號 B 登入
    And 帳號 A 仍維持原鎖定狀態
