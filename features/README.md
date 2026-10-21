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

目前尚未建立任何 Gherkin Feature。

本 Sample 的 `feature-index.csv` 只保留 CSV 標題列。

未來由 AI Analyst 根據已核准的規格建立 Feature 草稿，並同步更新本清單。