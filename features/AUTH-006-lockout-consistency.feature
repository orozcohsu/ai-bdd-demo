@AUTH-006
Feature: AUTH-006 帳號鎖定資料持久化與一致性
  連續失敗次數與鎖定時間由伺服器持久化管理。

  # specs/technical/technical-spec.md: TECH-002 第 1、4 項
  # specs/business/business-rules.md: BR-AUTH-002 第 1～4 項
  Scenario: 應用程式重新啟動後保留連續登入失敗次數
    Given 隔離測試環境中有一個未鎖定且連續登入失敗次數為 2 的會員帳號
    When 應用程式重新啟動並使用原本的隔離 SQLite 資料庫
    And 使用者以該帳號與錯誤密碼登入
    Then 該帳號立即被鎖定
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

  # specs/technical/technical-spec.md: TECH-002 第 4 項、SEC-003 第 1、3 項
  # specs/business/business-rules.md: BR-AUTH-002 第 5～8 項
  Scenario: 應用程式重新啟動後保留原鎖定期限
    Given 隔離測試環境中一個帳號在時間 T 因第三次連續失敗被鎖定
    When 應用程式在時間 T 後 30 秒重新啟動並使用原本的隔離 SQLite 資料庫
    And 該帳號在時間 T 後 59 秒以正確密碼登入
    Then 系統拒絕登入
    When 該帳號在時間 T 後 60 秒以正確密碼登入
    Then 系統允許登入

  # specs/technical/technical-spec.md: SEC-003 第 1、4 項
  # specs/business/business-rules.md: BR-AUTH-002 第 5 項
  Scenario: 瀏覽器端狀態不能解除伺服器鎖定
    Given 一個會員帳號仍在伺服器判定的鎖定期間
    When 使用者以未保存該帳號本地狀態的新瀏覽器提交正確帳號與密碼
    Then 系統拒絕登入
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

  # specs/technical/technical-spec.md: SEC-003 第 5 項
  # specs/business/business-rules.md: BR-AUTH-002 第 1～4 項
  Scenario: 同帳號的並行失敗不遺失累計次數
    Given 一個未鎖定的會員帳號連續登入失敗次數為 0
    When 該帳號同時送出 2 個錯誤密碼登入請求且均處理完成
    Then 該帳號的連續登入失敗次數為 2
    And 該帳號未被鎖定
    When 該帳號再送出 1 個錯誤密碼登入請求
    Then 該帳號立即被鎖定
