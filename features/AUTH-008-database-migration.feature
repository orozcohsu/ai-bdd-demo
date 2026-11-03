@AUTH-008
Feature: AUTH-008 SQLite 至 MariaDB 資料遷移相容性
  將隔離 SQLite 的全部應用資料移至隔離 MariaDB 後，會員、鎖定與登入狀態維持原有語意。
  所有遷移情境只操作隔離測試資料，不使用正式資料或正式憑證。

  # specs/technical/technical-spec.md v1.2: TECH-002、DEPLOY-004 第 4～6 項、第 9.2、9.4 節
  # docs/system-standard.md v0.2: 第 10.1、10.3 節
  Scenario: 全量遷移保留全部應用資料及原有欄位值
    Given 隔離 SQLite 來源含有會員、密碼雜湊、失敗次數、鎖定期限及 Session 資料
    And Session 資料同時包含尚未到期及已過期的記錄
    And 已備份來源並記錄全部應用資料表的資料筆數與欄位值
    And 隔離 MariaDB 目標已準備必要結構且沒有待遷移資料
    When 停止來源寫入並執行 SQLite 至 MariaDB 的全量遷移
    Then 全部應用資料表對應的資料均已搬移至 MariaDB
    And 目標資料筆數與對應欄位值均與來源記錄一致
    And 會員與 Session 的資料關聯維持一致
    And 已過期的 Session 記錄也保留原有資料
    And 來源 SQLite 資料與備份未被刪除或改寫

  # specs/technical/technical-spec.md v1.2: SEC-001 第 5 項、TECH-004 第 9 項、第 9.2 節
  # specs/business/business-rules.md v1.1: BR-AUTH-001 第 1～2 項
  # docs/system-standard.md v0.2: 第 10.1、10.3 節
  Scenario: 遷移後既有會員可用原密碼登入
    Given 隔離 SQLite 中有一個未鎖定的會員及其有效密碼雜湊
    And 已記錄該會員原本的密碼雜湊
    When 將來源資料完整遷移並切換應用至隔離 MariaDB
    Then 該會員儲存的密碼雜湊與遷移前完全相同
    When 使用者以原帳號與原正確密碼登入
    Then 系統允許登入
    And 系統導向 Welcome 頁面

  # specs/technical/technical-spec.md v1.2: SEC-003 第 6 項、第 9.2 節
  # specs/business/business-rules.md v1.1: BR-AUTH-002 第 2～4 項
  # docs/system-standard.md v0.2: 第 10.1 節
  Scenario: 遷移保留失敗次數且下一次錯誤仍觸發原鎖定規則
    Given 隔離 SQLite 中有一個未鎖定且連續登入失敗次數為 2 的會員帳號
    When 將來源資料完整遷移並切換應用至隔離 MariaDB
    Then 該會員的連續登入失敗次數仍為 2
    When 使用者以該帳號與錯誤密碼登入
    Then 該帳號立即被鎖定
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」

  # specs/technical/technical-spec.md v1.2: SEC-003 第 3、6 項、第 9.2、9.3 節
  # specs/business/business-rules.md v1.1: BR-AUTH-002 第 5～8 項
  # docs/system-standard.md v0.2: 第 6、10.1、10.3 節
  Scenario: 遷移不提前解除鎖定也不延長原鎖定期限
    Given 隔離 SQLite 中一個會員在時間 T 因第三次連續登入失敗被鎖定
    When 在時間 T 後 30 秒完成遷移並切換應用至隔離 MariaDB
    And 該帳號在時間 T 後 59 秒以正確密碼登入
    Then 系統拒絕登入
    And 登入頁面顯示「登入暫時受限，請於 1 分鐘後再試」
    When 該帳號在時間 T 後 60 秒以正確密碼登入
    Then 系統允許登入
    And 系統導向 Welcome 頁面

  # specs/technical/technical-spec.md v1.2: SEC-002 第 6 項、第 9.2 節
  # specs/functional/functional-spec.md v1.1: FUNC-009、FUNC-017
  # docs/system-standard.md v0.2: 第 10.2 節
  Scenario: 遷移後原瀏覽器可沿用尚未到期的 Session
    Given 隔離 SQLite 中已有一個成功登入會員的有效 Session
    And 已記錄該 Session 原本的到期時間 E
    And 遷移期間保留原有 Cookie 行為與必要應用機密設定
    When 在時間 E 之前完成遷移並切換應用至隔離 MariaDB
    And 在時間 E 之前使用原瀏覽器的 Session 存取 Welcome 頁面且未重新登入
    Then 系統允許存取 Welcome 頁面
    And 該登入狀態的到期時間仍為 E
    When 時間到達 E 並使用同一 Session 存取 Welcome 頁面
    Then 系統不允許存取 Welcome 頁面
    And 系統導向登入首頁

  # specs/technical/technical-spec.md v1.2: SEC-002 第 4 項、第 9.2 節
  # docs/system-standard.md v0.2: 第 10.1 第 6 項、第 10.2 第 5 項
  Scenario: 已過期的 Session 遷移後不會恢復有效登入
    Given 隔離 SQLite 中已有一筆到期時間已過的會員 Session
    When 將來源資料完整遷移並切換應用至隔離 MariaDB
    Then 目標保留該 Session 記錄及原本的到期時間
    When 使用該 Session 的瀏覽器存取 Welcome 頁面
    Then 系統不允許存取 Welcome 頁面
    And 系統導向登入首頁

  # specs/technical/technical-spec.md v1.2: DEPLOY-004 第 5 項、第 9.2 第 7 項
  # docs/system-standard.md v0.2: 第 10.3 第 5 項
  Scenario: 目標存在同名會員時不直接覆寫原有資料
    Given 隔離 SQLite 來源與隔離 MariaDB 目標存在同名會員
    And 已記錄目標既有會員的資料內容
    When 請求將來源會員資料遷移至目標
    Then 系統回報目標資料衝突
    And 目標既有會員的資料內容未被刪除或覆寫
