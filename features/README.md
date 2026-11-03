# Feature Index 管理規則

**專案名稱：** AI-BDD-DEMO  
**文件版本：** 1.5
**文件狀態：** Approved

## 1. 用途與適用範圍

本目錄管理 Gherkin Feature 的分類、唯一識別碼、檔案名稱、審核狀態及核准追溯資訊。

- `feature-index.csv`：Feature 索引的主要資料來源。
- `README.md`：管理規則、Feature 清單及核准追溯資訊。
- `*.feature`：Gherkin 驗收情境。

本目錄遵守根目錄 `agents.md` 與 `agents/analyst.md`。

本文件的核准狀態只代表本文件修訂的狀態，不會自動變更規格或 Gherkin 的核准狀態。

## 2. Feature Index 管理規則

1. AI Analyst 根據已核准規格，依業務意義分類 Domain。
2. 每個 Feature 必須有唯一且固定的 Feature ID。
3. 新增前，必須搜尋既有檔案、索引及相關未合併 PR，避免重複建立。
4. 既有或已移除的 Feature ID，不得任意重新編號或重複使用。
5. 新增、修改或移除 Feature 時，必須同步更新 `feature-index.csv`。
6. 本文件第 6 章的 Feature 清單必須與 CSV 一致。
7. 核准狀態必須有適用的證據，AI 不得自行宣告 Approved。
8. 需求變更只更新受影響內容，不重新產生所有 Feature。
9. 工作分支編號與 Feature ID 分開管理。
10. 文件引用路徑與實際目錄不同時，必須核對實際檔案。
11. 共通 Agent 工作規範由根目錄 `agents.md` 維護，不在本文件重複定義。

## 3. Feature ID 與檔名

Feature ID 格式：

`DOMAIN-NNN`

例如：

- `AUTH-001`
- `AUTH-002`
- `MEMBER-001`

Feature 檔案放在 `features/`，檔名使用：

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

規則：

1. Feature ID 與檔名不得重複。
2. CSV 必須與實際 Feature 檔案對應。
3. README 清單必須與 CSV 一致。
4. 核准追溯資訊記錄於第 7 章，不因本次修訂新增 CSV 欄位。

## 5. Feature 審核狀態

| 狀態 | 說明 |
|---|---|
| Draft | 正在整理的草稿 |
| Pending Review | 已提交 Human Reviewer 審查 |
| Approved | 已有適用於該內容的人類核准紀錄 |

未變更 Feature 沿用 CSV 的小寫 `approved`；本次候選修訂 AUTH-004、AUTH-006 與新增 AUTH-008 使用 `Pending Review`。第 6 章與 CSV 同步，不代表 AI 已核准新內容。

狀態管理規則：

1. 新增或修訂內容先標記為 Draft，提交審查時標記為 Pending Review。
2. Human Reviewer 審查對應內容，留下可追溯的核准紀錄。
3. AI Analyst 依有效紀錄及任務授權，同步索引與清單。
4. 已核准 Gherkin 的行為變更後，受影響內容必須重新審查。
5. 狀態文字本身不取代核准證據，也不代表自動檢查已通過。
6. 索引與有效核准紀錄不一致時，回報差異，不自行推定核准成立。
7. 本文件修訂不會取消未變更 Gherkin 的既有有效核准。

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
| AUTH-008 | AUTH | SQLite 至 MariaDB 資料遷移相容性 | [AUTH-008-database-migration.feature](AUTH-008-database-migration.feature) | approved |

本次保留全部既有 Feature ID 與檔名；只修訂 AUTH-004、AUTH-006，新增 AUTH-008。AUTH-001、002、003、005、007 的 Feature 內容與狀態維持不變。

## 7. G1 核准與追溯

### 7.1 自動檢查與人類審查分開回報

依本次技術規格 v1.2 的 QA-001 與共用介面 v0.2：

1. G1 自動檢查 Gherkin 語法、Feature ID、檔案／CSV／README 及既有需求／Scenario 追溯一致性。
2. 需求與 Gherkin 的人類審查另由 Human Reviewer 進行，語法通過不代表新情境已核准。
3. 不要求重複核准未變更內容，不建立 `requirements-review` Environment 等待點。
4. 不以本次 PR 尚未合併或缺少特定格式的歷史核准 PR，讓自動檢查必然失敗。
5. 以下歷史核准與補正資料保留背景用途，不作為本次新增的 CI 前提；不得冒用歷史核准宣稱候選修訂已核准。
6. G7 部署授權另依政策處理，本次不部署或遷移正式資料。

### 7.2 已查證的 Gherkin 核准紀錄

以下紀錄已由
[Actions Run 39753915856](https://github.com/orozcohsu/ai-bdd-demo/actions/runs/39753915856)
的 G1 檢查核對。

| 項目 | 紀錄 |
|---|---|
| 歷史核准範圍 | PR #2 合併版本的 AUTH-001～AUTH-007；不涵蓋本次 AUTH-004／006 修訂或 AUTH-008 |
| 核准 PR | [PR #2](https://github.com/orozcohsu/ai-bdd-demo/pull/2) |
| 人類合併帳號 | `orozcohsu` |
| 合併 commit | `240d5eb7c576a5da2664e3e23bdd5a9f05ec338f` |
| 驗證方式 | PR 變更檔案、合併帳號、版本祖先關係及 Git blob 內容比對 |
| 執行證據 | 該 Run 的 G1 報告 `G1-approval.json` |

對應內容版本：

| 檔案 | Git blob SHA |
|---|---|
| `AUTH-001-login.feature` | `dcfa4c8dea2baae286e3771f6bcad3fb448c1682` |
| `AUTH-002-account-lockout.feature` | `2209169a282c06ade0cc862646d5f55a27c7c094` |
| `AUTH-003-lockout-expiry.feature` | `62ac48f85c7ec36930c6b84454368f3d521eb44a` |
| `AUTH-004-welcome-access.feature` | `e30338419ae9b8545207de14298bb3ecc9aa3fd0` |
| `AUTH-005-login-security.feature` | `0046c9ea500b57881c28596a23d388d952c1f8f0` |
| `AUTH-006-lockout-consistency.feature` | `afb2a799f5fb2b13a649e5b46a8b2b886d3aae85` |
| `AUTH-007-login-presentation.feature` | `ded20fe9a0099b052dc7296657b29e7ecf4ad588` |

Actions artifact 有保存期限；即使報告到期，仍應能透過 PR、commit 與 Git blob 重新核對，不得僅憑本表宣稱核准成立。

### 7.3 歷史來源規格證據查詢結果

相關來源規格：

| 規格 | 檔案 |
|---|---|
| 功能規格 | [functional-spec.md](../specs/functional/functional-spec.md) |
| 業務規則 | [business-rules.md](../specs/business/business-rules.md) |
| 技術規格 | [technical-spec.md](../specs/technical/technical-spec.md) |

來源需求編號與情境的對應，見各 Feature 檔案中的註解。

Actions Run 39753915856 尚未找到上述三份規格目前內容所對應的完整人類合併 PR 證據。

這表示「核准紀錄尚未驗證」，不表示規格一定未經人類閱讀或同意。

以下僅描述 Run 39753915856 當時的結果，不代表目前分支的核准判定：

- Gherkin 語法與索引一致性：已通過該次檢查。
- AUTH-001～AUTH-007 的核准紀錄：已驗證。
- 三份來源規格的核准紀錄：尚待補正。
- G1 整體：尚未全部通過。

技術規格若同時存在 Approved 與 Pending Review 等不同紀錄，必須確認各紀錄適用的版本與範圍，不自行選擇其中一項作為核准結論。

### 7.4 舊版歷史核准補正說明（保留參考）

以下為舊版提出的歷史補正說明。本次不啟動此流程、不要求補正 PR 作為 G1 通過前提；只有日後 Human Reviewer 另行要求時才適用：

1. AI Analyst 整理三份規格的實際路徑、文件版本、固定 commit 及 Git blob SHA。
2. 列出既有核准資訊、缺漏或互相矛盾的紀錄。
3. 在本文件第 7.5 節建立明確的核准範圍表，提交獨立的核准紀錄補正 PR。
4. 該 PR 必須提供固定 commit 的規格連結，讓 Human Reviewer 能確認實際被核准的內容。
5. Human Reviewer 審查補正紀錄及對應規格內容，明確確認核准範圍，再決定是否合併。
6. AI DevOps 依已核准的補正方式，完善 G1 驗證。
7. 重新執行 G1，確認紀錄及目前內容一致。

補正限制：

- 不為製造 PR 差異而改寫業務規則。
- 不虛構過去的核准日期、帳號或 PR。
- 現在進行的核准，使用現在實際留下的紀錄，不回填成過去已完成。
- 核准表必須綁定規格內容版本，不能只寫文件名稱或 Approved。
- PR 審查期間若規格內容改變，必須重新確認適用版本。
- 補正 PR 尚未經人類核准前，不得宣稱補正已完成。
- 本流程須經 Human Reviewer 核准後採用；不得與根目錄 `agents.md` 衝突。
- 若現有 workflow 尚未支援這種補正紀錄，必須由 DevOps 修改驗證方式後再執行，不能只更新本文件就宣稱 G1 通過。

補正 PR 可以只修改核准追溯紀錄，不必修改被核准的規格內容；但必須清楚指出其審查及核准的是哪些固定版本的規格。

### 7.5 歷史追溯欄位說明（保留參考）

本次不新增歷史核准補正表。以下僅保留舊版欄位說明，不代表新版來源規格仍未核准。

AI Analyst 應先查證，再填入以下資料；未知欄位不得推測。

| 必要資料 | 說明 |
|---|---|
| 規格路徑 | 實際存在的完整 Repo 相對路徑 |
| 文件版本 | 被審查的文件版本 |
| 內容 commit | 包含該規格內容的完整 Git commit SHA |
| Git blob SHA | 該規格檔案的內容識別值 |
| 固定版本連結 | 指向該 commit 中規格檔案的連結 |
| 核准範圍 | 整份文件，或明確列出的章節與要求 |
| 核准紀錄 PR | 實際提交並經人類審查的補正 PR |
| 核准人及時間 | 從實際 GitHub 紀錄查證 |
| 驗證結果 | 尚未驗證、已驗證，或不再適用 |

PR 編號、合併帳號與時間，應從 GitHub 實際紀錄取得。

若補正 PR 的合併資訊在合併前尚不存在，不必預先填造；可以由 CI 在合併後查詢並驗證。

### 7.6 核准延續與變更

1. 內容未變且仍對應有效核准紀錄時，可以沿用既有核准。
2. 主程式、測試、CI 或本文件的純紀錄維護，不要求重新核准未變更的 Gherkin。
3. 需求或 Gherkin 的受影響內容變更後，必須重新提交審查。
4. 不相關程式或 CI PR 的合併，不取代規格或 Gherkin 核准。
5. PR 合併前的語法檢查，不得等待同一 PR 已合併才執行。
6. 待審查內容可以通過語法檢查，但不能因此宣稱人工核准已完成。
7. 人類合併 PR，不會讓失敗或未執行的自動檢查變成 PASS。
8. 不得要求 AI 自行核准、合併或製造核准證據。

### 7.7 本次 MariaDB 候選修訂

來源為 `copy-main` 的技術規格 v1.2 與共用介面 v0.2（頁首均為 Approved）。Human Reviewer 已修正介面文件的 Draft 狀態矛盾；本次候選 Gherkin 仍待獨立審查，不自行變更來源規格。

| Feature | 候選差異 | 來源 |
|---|---|---|
| `AUTH-004` | 保留原 4 情境；新增應用重啟後保留尚未到期 Session 及原到期時間 | TECH-002、SEC-002、QA-002；介面第 6.1 節 |
| `AUTH-006` | 保留原 4 情境與鎖定邊界；兩個重啟步驟改用原隔離 MariaDB，並更新交易／並行追溯 | TECH-002、TECH-004、SEC-003、QA-002；介面第 5.1、6、9 節 |
| `AUTH-008` | 新增 7 個遷移情境：全量資料與過期 Session 記錄、原密碼、失敗次數、原鎖定期限、有效 Session 及原到期時間、過期 Session 不恢復登入、目標衝突不覆寫 | SEC-001～003、DEPLOY-004、第 9.2～9.4 節；介面第 10 章 |

AUTH-008 的必要性：資料跨引擎搬移具有獨立前置條件與操作，既有應用重啟情境無法證實資料搬移完整性；沿用 AUTH 分類並分配未使用的 008，不重新編號既有 Feature。

目前共 8 Features、40 個 Scenario／Outline，Examples 展開為 49 個案例。此數量是 Gherkin 定義，不表示測試程式已新增或產品測試已通過。

- Test Engineer：更新 MariaDB fixtures、AUTH-006 步驟綁定、AUTH-004／008 新情境及 COVERAGE.md；全量遷移使用隔離來源 SQLite 與隔離目標 MariaDB，不接觸正式資料。
- Developer：依介面 v0.2 實作連線、結構準備、交易及遷移工具，保持密碼雜湊、原期限與 Session 相容；遷移執行介面屬後續技術接合，不由 Analyst 虛構已存在的 CLI。
- DevOps：配置 MariaDB 11.8.6 測試服務、驅動與 wheel 驗證；現有 SQLite 執行環境的成功不能當作 MariaDB 驗證。
- 表格結構、型別與全部欄位映射、備份及回復方案、機密保護、權限與版本相容性另由適當測試／設定審查驗證，不強行全部改成 Gherkin。
- 本次未修改 tests/；現有測試綁定與覆蓋清單尚未支援全部候選情境。語法／索引通過與測試待接續分開回報，不刪除新情境或弱化預期讓舊檢查變綠。

## 8. 角色交接與驗證限制

| 角色 | 責任 |
|---|---|
| Human Reviewer | 審查需求與 Gherkin，確認核准範圍及歷史補正方式，決定是否合併 |
| AI Analyst | 維護草稿、索引、清單及規格與 Gherkin 的核准追溯資訊 |
| AI Test Engineer | 依已核准情境及共用介面約定建立測試 |
| AI Developer | 依規格、共用介面約定及測試實作程式 |
| AI DevOps | 執行自動檢查，驗證核准紀錄與實際受測版本 |

語法、索引及核准證據應分開回報。

Gherkin 語法通過，不代表主程式、測試、安全掃描、建置或部署已通過。

技術選型、程式結構、型別、工具與部署限制，由相關角色及品質檢查驗證，不強行轉成 Gherkin。

缺少明確驗收尺度的要求，應指出具體缺口，不自行補值。

本文件修訂不會自動更新 workflow、補足人工核准或重跑 Actions。必要紀錄及設定完成後，必須驗證新的受測版本。

---
