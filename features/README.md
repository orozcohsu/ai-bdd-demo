# Feature Index 管理規則

**專案名稱：** AI-BDD-DEMO  
**文件版本：** 1.3  
**文件狀態：** Approved

## 1. Feature Index 用途

本目錄管理 Gherkin Feature 的分類、唯一識別碼、檔案名稱、審核狀態及核准追溯資訊。

- `feature-index.csv`：Feature 索引的主要資料來源。
- `README.md`：管理規則、Feature 清單及核准追溯資訊。
- `*.feature`：Gherkin 驗收情境。

本目錄遵守根目錄 `agents.md` 及 `agents/analyst.md`。

本文件的狀態代表本次 README 修訂是否核准，不代表既有 Feature 的核准被取消或自動重新成立。

## 2. Feature Index 管理規則

1. AI Analyst 根據已核准規格，依業務意義分類 Domain。
2. 每個 Feature 必須有唯一且固定的 Feature ID。
3. 新增前搜尋既有檔案、索引與相關未合併 PR，避免重複建立或分配編號。
4. 已存在或已移除的 Feature ID，不得任意重新編號或重複使用。
5. 新增、修改或移除 Feature 時，必須同步更新 `feature-index.csv`。
6. 本文件第 6 章的 Feature 清單必須與 CSV 一致。
7. 核准狀態必須有適用的證據，AI 不得自行宣告 Approved。
8. 需求變更只更新受影響內容，不重新產生所有 Feature。
9. 工作分支編號與 Feature ID 分開管理。
10. 文件引用路徑與實際目錄不同時，核對實際檔案，不得假設內容。
11. 本文件不放置共通 Agent 工作規範；共通規範由根目錄 `agents.md` 維護。

## 3. Feature ID 與檔名

Feature ID 格式：

`DOMAIN-NNN`

例如：

- `AUTH-001`
- `AUTH-002`
- `MEMBER-001`

Gherkin 檔案放在本目錄，檔名使用：

`<Feature_ID>-<英文語意短名>.feature`

例如：

`AUTH-001-login.feature`

既有 Feature 不因排序、文件修正或其他 Feature 移除而重新編號，也不任意更名。

## 4. CSV 欄位定義

`feature-index.csv` 使用以下欄位：

| 欄位 | 說明 |
|---|---|
| Feature_ID | 唯一 Feature ID |
| Domain | 業務分類 |
| Description | 功能名稱或簡要說明 |
| Filename | Feature 檔名，不含上層目錄 |
| Status | 審核狀態 |

CSV 標題列：

```csv
Feature_ID,Domain,Description,Filename,Status
```

Feature ID 與檔名不得重複，索引必須與實際 Feature 檔案對應。

核准追溯資訊記錄於第 7 章，不因本次 README 修訂新增 CSV 欄位。

## 5. Feature 審核狀態

| 狀態 | 說明 |
|---|---|
| Draft | 正在整理的草稿 |
| Pending Review | 已提交 Human Reviewer 審查 |
| Approved | 已有適用於該內容的人類核准紀錄 |

目前 CSV 使用小寫 `approved`，第 6 章沿用相同值，不為了調整顯示而任意改寫 CSV。

規則：

1. 新增或修訂內容先標記為 Draft，提交審查時標記為 Pending Review。
2. Human Reviewer 審查並合併對應規格／Gherkin PR，留下人工核准紀錄。
3. AI Analyst 依有效紀錄與任務授權，同步索引及清單。
4. 已核准 Gherkin 行為變更後，受影響內容必須重新審查。
5. 狀態文字本身不取代核准證據，也不代表自動檢查已通過。
6. 索引狀態與有效核准紀錄不一致時，回報具體差異，不自行推定結論。

## 6. Feature 清單

以下清單依現有 `feature-index.csv` 同步。

| Feature_ID | Domain | Description | Filename | Status |
|---|---|---|---|---|
| AUTH-001 | AUTH | 會員登入與登入首頁（含重設焦點及不存在帳號規則） | [AUTH-001-login.feature](AUTH-001-login.feature) | approved |
| AUTH-002 | AUTH | 連續登入失敗與帳號鎖定 | [AUTH-002-account-lockout.feature](AUTH-002-account-lockout.feature) | approved |
| AUTH-003 | AUTH | 鎖定到期與失敗次數重設 | [AUTH-003-lockout-expiry.feature](AUTH-003-lockout-expiry.feature) | approved |
| AUTH-004 | AUTH | Welcome 頁面與登入狀態 | [AUTH-004-welcome-access.feature](AUTH-004-welcome-access.feature) | approved |
| AUTH-005 | AUTH | 登入安全與 Session 保護 | [AUTH-005-login-security.feature](AUTH-005-login-security.feature) | approved |
| AUTH-006 | AUTH | 帳號鎖定資料持久化與一致性 | [AUTH-006-lockout-consistency.feature](AUTH-006-lockout-consistency.feature) | approved |
| AUTH-007 | AUTH | 登入頁與 Welcome 頁的伺服器端呈現 | [AUTH-007-login-presentation.feature](AUTH-007-login-presentation.feature) | approved |

本次 README 修訂不變更上述 Gherkin、Feature ID、檔名或 CSV 狀態。

## 7. G1 核准與追溯

### 7.1 G1 的兩個部分

G1 包含：

1. Gherkin 語法、Feature ID 及索引一致性的自動檢查。
2. Human Reviewer 對需求與 Gherkin 的人工核准，以及核准紀錄有效性的驗證。

人工核准依根目錄 `agents.md`，透過 Human Reviewer 審查並合併對應規格／Gherkin PR 留下紀錄。

不要求每次 Actions 執行都重新核准相同內容，也不以 `requirements-review` Environment 作為 G1 必要機制。

G7 部署核准另依部署政策處理。

### 7.2 已查證的 Gherkin 核准紀錄

以下紀錄已由 [Actions Run 39748776268](https://github.com/orozcohsu/ai-bdd-demo/actions/runs/39748776268) 的 G1 檢查核對。

| 項目 | 紀錄 |
|---|---|
| 核准範圍 | AUTH-001～AUTH-007 的目前 Gherkin 內容 |
| 核准 PR | [PR #2](https://github.com/orozcohsu/ai-bdd-demo/pull/2) |
| 人類合併帳號 | `orozcohsu` |
| 合併 commit | `240d5eb7c576a5da2664e3e23bdd5a9f05ec338f` |
| 驗證方式 | PR 變更檔案、合併帳號、版本祖先關係及 Git blob 內容比對 |
| 證據位置 | 該 Run 的 G1 artifact：`G1-approval.json` |

已核對的檔案內容版本如下：

| 檔案 | Git blob SHA |
|---|---|
| `AUTH-001-login.feature` | `dcfa4c8dea2baae286e3771f6bcad3fb448c1682` |
| `AUTH-002-account-lockout.feature` | `2209169a282c06ade0cc862646d5f55a27c7c094` |
| `AUTH-003-lockout-expiry.feature` | `62ac48f85c7ec36930c6b84454368f3d521eb44a` |
| `AUTH-004-welcome-access.feature` | `e30338419ae9b8545207de14298bb3ecc9aa3fd0` |
| `AUTH-005-login-security.feature` | `0046c9ea500b57881c28596a23d388d952c1f8f0` |
| `AUTH-006-lockout-consistency.feature` | `afb2a799f5fb2b13a649e5b46a8b2b886d3aae85` |
| `AUTH-007-login-presentation.feature` | `ded20fe9a0099b052dc7296657b29e7ecf4ad588` |

上述紀錄只適用於對應內容，不代表未來變更自動獲得核准。

Actions artifact 有保存期限；即使 artifact 到期，仍應能透過 PR、commit 與 Git blob 重新核對，不得僅依本表宣稱核准成立。

### 7.3 來源規格與待補正證據

相關來源規格：

- [功能規格](../specs/functional/functional-spec.md)
- [業務規則](../specs/business/business-rules.md)
- [技術規格](../specs/technical/technical-spec.md)

Gherkin 的來源需求編號見各 Feature 檔案中的註解。

本次 Runner 尚未找到三份來源規格「目前內容與人類合併 PR 相符」的完整證據。因此：

1. 不宣稱 G1 已全部通過。
2. 不否定 Human Reviewer 先前已進行的審查。
3. 由 AI Analyst 整理目前版本、歷史提交與既有核准資訊。
4. 由 Human Reviewer 確認歷史核准的補正方式。
5. AI DevOps 再依已確認的紀錄方式實作驗證。
6. 不為製造 PR 差異而重新改寫業務規則，不虛構核准日期或版本。

修正本 README 的清單，只能解決清單一致性問題，不能自動補足來源規格的核准證據。

### 7.4 核准延續

1. 內容未變且仍對應有效核准紀錄時，可以沿用既有核准。
2. 主程式、測試、CI 或本文件的純紀錄維護，不要求重新核准未變更的 Gherkin。
3. 需求或 Gherkin 的受影響內容變更後，必須重新提交審查。
4. 不相關程式或 CI PR 的合併，不取代規格／Gherkin 核准。
5. PR 合併前的語法檢查不得等待同一 PR 已合併才執行。
6. 人類合併 PR，不會讓失敗或未執行的自動檢查變成 PASS。

## 8. 交接與驗證限制

| 角色 | 責任 |
|---|---|
| Human Reviewer | 審查需求與 Gherkin，確認核准範圍並決定合併 |
| AI Analyst | 維護草稿、索引、清單及核准追溯資訊 |
| AI Test Engineer | 依已核准情境建立測試 |
| AI Developer | 依規格、共用介面與測試實作程式 |
| AI DevOps | 執行自動檢查，驗證核准紀錄與受測版本 |

語法、索引與核准證據應分開回報。

Gherkin 語法通過，不代表測試、主程式、安全檢查、建置或部署已通過。

技術選型、程式結構、型別、工具與部署限制，由相應角色及品質檢查驗證，不強行轉成 Gherkin。

缺少明確驗收尺度的視覺、瀏覽器相容性或其他要求，列為待確認事項，不自行補值。

本次文件修訂不會自動更新 workflow 或重跑 Actions；須在文件審查及必要設定完成後，驗證新的受測版本。

---