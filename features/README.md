# Feature Index 管理規則

**專案名稱：** AI-BDD-DEMO  
**文件版本：** 1.0  
**文件狀態：** Approved（已核准）

## 1. Feature Index 用途

本目錄用於管理 Gherkin Feature 的分類、唯一識別碼、檔案名稱及審核狀態。

- `feature-index.csv`：Feature 索引的主要資料來源。
- `README.md`：Feature 管理規則及人類可閱讀的 Feature 清單。
- `*.feature`：Gherkin 驗收情境。

## 2. Feature Index 管理規則

1. AI Analyst 根據功能規格與業務規則，自動分類 Domain。
2. 每個 Feature 必須有唯一且固定的 Feature ID。
3. 新增 Feature 時，自動分配尚未使用的編號。
4. 已存在的 Feature ID 不得任意修改或重複使用。
5. 新增、修改或移除 Feature 時，必須同步更新 `features/feature-index.csv`。
6. `features/README.md` 必須根據 CSV 同步維護。
7. Feature 的狀態必須與實際審核狀態一致，AI 不得自行將 Draft 改為 Approved。
8. 完成後，列出新增、修改與移除的 Feature，供 Human Reviewer 審核。

## 3. Feature ID 格式

採用以下格式：

`DOMAIN-NNN`

例如：

- `AUTH-001`：登入相關功能。
- `AUTH-002`：帳號安全相關功能。
- `MEMBER-001`：會員管理相關功能。

Feature ID 一經建立，不得因排序或其他 Feature 刪除而重新編號。

## 4. CSV 欄位定義

`feature-index.csv` 使用以下欄位：

| 欄位 | 說明 |
|---|---|
| Feature_ID | 唯一 Feature ID |
| Domain | 功能分類 |
| Description | 功能名稱 |
| Filename | Gherkin 檔案名稱 |
| Status | 審核狀態 |

## 5. Feature 審核狀態

| 狀態 | 說明 |
|---|---|
| Draft | AI Analyst 建立的草稿 |
| Pending Review | 等待 Human Reviewer 審核 |
| Approved | 已取得 Human Reviewer 正式核准 |

只有取得可查證的 Human Reviewer 核准紀錄，才能將 Feature 狀態設定為 Approved。

已核准的 Feature 若需修改，必須重新取得核准。

## 6. Feature 清單

以下清單依 `feature-index.csv` 同步維護。全數為候選草稿，尚待 Human Reviewer 審核，不代表已通過 G1。

| Feature_ID | Domain | Description | Filename | Status |
|---|---|---|---|---|
| AUTH-001 | AUTH | 會員登入與登入首頁（含重設焦點及不存在帳號規則） | [AUTH-001-login.feature](AUTH-001-login.feature) | Pending Review |
| AUTH-002 | AUTH | 連續登入失敗與帳號鎖定 | [AUTH-002-account-lockout.feature](AUTH-002-account-lockout.feature) | Pending Review |
| AUTH-003 | AUTH | 鎖定到期與失敗次數重設 | [AUTH-003-lockout-expiry.feature](AUTH-003-lockout-expiry.feature) | Pending Review |
| AUTH-004 | AUTH | Welcome 頁面與登入狀態 | [AUTH-004-welcome-access.feature](AUTH-004-welcome-access.feature) | Pending Review |
| AUTH-005 | AUTH | 登入安全與 Session 保護 | [AUTH-005-login-security.feature](AUTH-005-login-security.feature) | Pending Review |
| AUTH-006 | AUTH | 帳號鎖定資料持久化與一致性 | [AUTH-006-lockout-consistency.feature](AUTH-006-lockout-consistency.feature) | Pending Review |
| AUTH-007 | AUTH | 登入頁與 Welcome 頁的伺服器端呈現 | [AUTH-007-login-presentation.feature](AUTH-007-login-presentation.feature) | Pending Review |

來源：`specs/functional/functional-spec.md` 與 `specs/business/business-rules.md` v1.1，以及 `specs/technical/technical-spec.md` v1.0；三份規格均有 2026-10-21 的 Approved 核准紀錄。情境上方註解標示來源路徑與需求編號。

AUTH-001～004 涵蓋功能及業務規則；AUTH-005～007 補充技術規格中的安全、持久化、並行一致性與 SSR 可驗證行為。本次依 v1.1 更新 AUTH-001：登入表單提供重設按鈕、清空兩欄後可直接在帳號欄輸入，以及不存在帳號第 2／3／4 次嘗試均維持一致錯誤回應且不套用會員鎖定。AUTH-002～007 相較 PR #1 完全不變，沒有新增或重新編號 Feature。

後續角色交接：淡藍色的色碼／設計樣本、支援的瀏覽器與螢幕尺寸、Session 有效期限與 SameSite 值、輸入驗證及 XSS 測試範圍，留待對應角色提出方案並經人類確認。本批不填入未核准值，也不宣稱完整覆蓋；不影響已明確情境的審查。

TECH-001 的工具選型、CODE-001／CODE-002 的結構與型別規範、QA-001／QA-002 的關卡與隔離要求，以及 DEPLOY-001／DEPLOY-002 的環境與部署限制，仍須由程式／設定審查與適當品質關卡驗證，不以 Gherkin 語法檢查取代。密碼演算法與正式機密不得硬編碼等要求亦須配合安全審查。

不存在帳號的回應及不適用會員鎖定已由 BR-AUTH-003 第 4 項明確定義，相關疑問已解除；本批不對未指定的內部計數或資料儲存策略新增要求。

時間 T 指第三次連續登入失敗的時刻；59／60／61 秒情境描述業務時間邊界，不要求測試實際等待。
