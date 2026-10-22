# Feature Index 管理規則

**專案名稱：** AI-BDD-DEMO  
**文件版本：** 1.4  
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

目前 CSV 使用小寫 `approved`，第 6 章沿用相同值，不為調整顯示而改寫 CSV。

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

本次 README 修訂不變更上述 Gherkin、Feature ID、檔名或 CSV 狀態。

## 7. G1 核准與追溯

### 7.1 G1 的檢查範圍

G1 分為兩部分：

1. 自動檢查：
   Gherkin 語法、Feature ID 唯一性，以及檔案、CSV、README 清單一致性。
2. 人工核准紀錄驗證：
   確認來源規格與 Gherkin 已經 Human Reviewer 核准，且紀錄適用於目前內容。

兩部分必須分開回報。

不要求每次 Actions 執行時重新核准未變更的內容，也不以 `requirements-review` Environment 作為 G1 必要機制。

G7 部署核准另依部署政策處理。

### 7.2 已查證的 Gherkin 核准紀錄

以下紀錄已由
[Actions Run 39753915856](https://github.com/orozcohsu/ai-bdd-demo/actions/runs/39753915856)
的 G1 檢查核對。

| 項目 | 紀錄 |
|---|---|
| 核准範圍 | AUTH-001～AUTH-007 的對應 Gherkin 內容 |
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

上述紀錄只適用於對應內容，不代表未來變更自動獲得核准。

Actions artifact 有保存期限；即使報告到期，仍應能透過 PR、commit 與 Git blob 重新核對，不得僅憑本表宣稱核准成立。

### 7.3 來源規格目前的核准證據缺口

相關來源規格：

| 規格 | 檔案 |
|---|---|
| 功能規格 | [functional-spec.md](../specs/functional/functional-spec.md) |
| 業務規則 | [business-rules.md](../specs/business/business-rules.md) |
| 技術規格 | [technical-spec.md](../specs/technical/technical-spec.md) |

來源需求編號與情境的對應，見各 Feature 檔案中的註解。

Actions Run 39753915856 尚未找到上述三份規格目前內容所對應的完整人類合併 PR 證據。

這表示「核准紀錄尚未驗證」，不表示規格一定未經人類閱讀或同意。

目前應如實區分：

- Gherkin 語法與索引一致性：已通過該次檢查。
- AUTH-001～AUTH-007 的核准紀錄：已驗證。
- 三份來源規格的核准紀錄：尚待補正。
- G1 整體：尚未全部通過。

技術規格若同時存在 Approved 與 Pending Review 等不同紀錄，必須確認各紀錄適用的版本與範圍，不自行選擇其中一項作為核准結論。

### 7.4 歷史規格核准的補正流程

歷史規格若已存在於 main，但未透過可追溯的核准 PR 建立，可提出以下補正方式供 Human Reviewer 核准：

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

### 7.5 來源規格核准追溯紀錄

以下是提交 Human Reviewer 審查的固定內容快照，尚未取得本次核准。
本次僅補追溯資料，不修改來源規格，也不將文件頁首 Approved 當作已完成核准的證據。

<!-- G1-SPEC-TRACE-V1：欄位及範圍由驗證程式檢查；人工核准另查實際合併紀錄。 -->
| 規格路徑 | 文件版本 | 內容 commit | Git blob SHA | 固定版本連結 | 提交核准範圍 | 提交狀態 |
|---|---|---|---|---|---|---|
| specs/functional/functional-spec.md | 1.1 | bbf1107c9680ee58ae3f43f2d540bb749065bcee | 51ca6c39bc4158822f3dcccd4c54d1b9b5e6ce2e | [固定版本](https://github.com/orozcohsu/ai-bdd-demo/blob/bbf1107c9680ee58ae3f43f2d540bb749065bcee/specs/functional/functional-spec.md) | 整份文件（含核准紀錄狀態差異，請以本次審查確認） | Pending Review |
| specs/business/business-rules.md | 1.1 | bbf1107c9680ee58ae3f43f2d540bb749065bcee | f54904222fe2d41d594627525d3f26e0ba5142a4 | [固定版本](https://github.com/orozcohsu/ai-bdd-demo/blob/bbf1107c9680ee58ae3f43f2d540bb749065bcee/specs/business/business-rules.md) | 整份文件（含核准紀錄狀態差異，請以本次審查確認） | Pending Review |
| specs/technical/technical-spec.md | 1.1 | bbf1107c9680ee58ae3f43f2d540bb749065bcee | 3cb7367e4a01bc46ed3b620c08f02a6a78663ad3 | [固定版本](https://github.com/orozcohsu/ai-bdd-demo/blob/bbf1107c9680ee58ae3f43f2d540bb749065bcee/specs/technical/technical-spec.md) | 整份文件（含核准紀錄狀態差異，請以本次審查確認） | Pending Review |

#### 本次需確認的核准範圍與差異

- 功能與業務規格：本次提交上述固定版本整份文件；既有文件內的 v1.1／Approved 文字不代替 GitHub 核准追溯。
- 技術規格：頁首為 v1.1／Approved，第 237～239 行為 v1.0 的歷史核准，第 245～249 行仍是 v1.1／Pending Review。請明確確認本表固定內容的整份 v1.1 是否核准；本次不修改或抹除歷史紀錄。
- 若 Human Reviewer 尚不同意整份文件或無法確認狀態差異，請先要求修訂，不合併本次核准紀錄。不得由 AI 推定核准成立。
- 若僅核准部分章節，必須先明確記錄範圍並調整驗證方式；目前表格提交的是整份文件，不能將部分同意解讀為整份核准。

#### 核准資訊的取得與延續

- 本表的 Pending Review 是「提交時狀態」，不會預填未發生的核准。
- 本次 PR 必須明確聲明同時提交此表所列固定規格版本供人類核准。
- 核准 PR 編號、人類合併帳號、合併時間與合併 commit，由 G1 查詢 GitHub 實際紀錄，不由 AI 預填。
- 僅當人類合併的 PR 實際新增或更新對應追溯列、合併版本內的紀錄有效，而且受測規格 blob 與表列版本一致，才能認定該列核准有效。
- 單純修改 README 其他章節、保留舊表，不能成為新的規格核准證據。
- 合併後可以保留本表的提交時狀態；實際核准結果以 CI 查得的 PR 與內容證據為準，避免為更新狀態再製造一次核准循環。
- PR 未合併時，追溯結構與雜湊檢查可先通過，但人工核准仍未完成，G1 整體不得宣稱 PASS。
- 本次內容未經人工合併前，不宣稱核准補正已完成；後續規格內容變更將使舊內容比對失效。

### 7.6 核准延續與變更

1. 內容未變且仍對應有效核准紀錄時，可以沿用既有核准。
2. 主程式、測試、CI 或本文件的純紀錄維護，不要求重新核准未變更的 Gherkin。
3. 需求或 Gherkin 的受影響內容變更後，必須重新提交審查。
4. 不相關程式或 CI PR 的合併，不取代規格或 Gherkin 核准。
5. PR 合併前的語法檢查，不得等待同一 PR 已合併才執行。
6. 待審查內容可以通過語法檢查，但不能因此宣稱人工核准已完成。
7. 人類合併 PR，不會讓失敗或未執行的自動檢查變成 PASS。
8. 不得要求 AI 自行核准、合併或製造核准證據。

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