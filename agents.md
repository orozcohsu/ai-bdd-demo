# AI-BDD-DEMO — AI Agent 工作規範

**文件版本：** 1.0  
**文件狀態：** Approved（已核准） 

## 1. 專案說明

AI-BDD-DEMO 是一個使用 AI 輔助行為驅動開發（AI-BDD）的練習專案。

本專案是一個會員登入網站，採用以下技術：

- Python + FastAPI
- Jinja2 + HTML + CSS
- SQLite
- pytest + pytest-bdd
- GitHub Actions
- Raspberry Pi Ubuntu + systemd

所有開發必須以經過 Human Reviewer 核准的規格與 Gherkin 為依據。

## 2. 規格文件

本專案的主要規格如下：

| 檔案 | 用途 |
|---|---|
| `specs/functional-spec.md` | 功能範圍與功能需求 |
| `specs/business-rules.md` | 業務規則與判斷條件 |
| `specs/technical-spec.md` | 技術架構、安全性與部署要求 |
| `features/*.feature` | Gherkin 驗收情境 |
| `features/feature-index.csv` | Feature ID 與狀態索引 |
| `features/README.md` | Feature 清單 |

AI 在進行工作前，必須讀取與任務相關的規格。

如果規格互相衝突、缺少必要條件或存在未確認的業務規則，必須詢問 Human Reviewer，不得自行決定。

## 3. AI 角色與修改權限

| 角色 | 主要職責 | 預設可修改範圍 |
|---|---|---|
| Human Reviewer | 核准需求、業務規則、技術規格及 Gherkin | 規格與 Gherkin |
| AI Analyst | 分析需求、詢問業務規則、整理規格、產生 Gherkin 草稿 | `specs/` 草稿、未核准的 `features/`、Feature 索引 |
| AI Test Engineer | 依據已核准 Gherkin 建立 pytest-bdd、fixtures 與回歸測試 | `tests/` |
| AI Developer | 依據已核准規格實作應用程式 | `src/` |
| AI Failure Analyst | 分析測試失敗原因並提出修正建議 | 原則上唯讀 |
| AI DevOps | 維護品質關卡、CI/CD 與部署設定 | `.github/`、`deploy/`、`pyproject.toml` |

角色權限是工作範圍約束，並非作業系統強制權限。超出範圍的修改必須經 Human Reviewer 授權。

## 4. Agent 執行規則

1. 每次執行任務前，必須先確認目前被指派的角色。
2. 先讀取本文件 `AGENTS.md`。
3. 再讀取對應角色的 `agents/*.md`。
4. 讀取相關的已核准規格。
5. 確認允許修改的檔案範圍。
6. 只修改本次任務必要的檔案。
7. 完成後回報修改內容與測試結果。
8. 未明確指派角色時，應先詢問，不得直接修改檔案。

AI 角色是工作分工，不代表 Codex 會自動啟動多個 Agent。執行時必須明確指定角色及其指示文件。

## 5. 標準 AI-BDD 工作流程

1. Human Reviewer 提出需求。
2. AI Analyst 分析需求並提出需要釐清的問題。
3. AI Analyst 建立或修改規格草稿。
4. Human Reviewer 核准規格。
5. AI Analyst 產生或更新 Gherkin 草稿。
6. Human Reviewer 核准 Gherkin（G1）。
7. AI Test Engineer 建立自動化測試。
8. AI Developer 實作功能。
9. GitHub Actions 執行 G2～G6。
10. 測試失敗時，由 AI Failure Analyst 分析原因並建議負責角色修正。
11. 全部必要品質關卡通過後，才允許部署。

## 6. 品質關卡

| Gate | 檢查內容 | 必須通過 |
|---|---|---|
| G1 | Gherkin 語法檢查與 Human Reviewer 核准 | 是 |
| G2 | pytest-bdd 驗收測試 | 是 |
| G3 | Regression Tests | 是 |
| G4 | Ruff / Mypy | 是 |
| G5 | Bandit / pip-audit | 是 |
| G6 | Build / Integration Tests | 是 |
| G7 | Deployment Approval | 依環境 |

G1 的人工核准必須有可查證的紀錄，不能只依賴 AI 自行將狀態改成 Approved。

G2～G6 全部通過後，才允許執行 CD。

## 7. 規格變更管理

1. AI 不得自行發明業務規則。
2. 已核准的業務規則不得未經授權修改。
3. 已核准的 Gherkin 不得未經授權修改。
4. 既有 Feature ID 不得任意重新編號。
5. 新 Feature ID 必須唯一。
6. `features/feature-index.csv` 由 AI Analyst 維護。
7. `features/README.md` 必須與 Feature 索引一致。
8. 修復 Bug 時，不得擅自改變已核准的業務行為。
9. 重構程式時，不得改變外部可觀察的業務行為。
10. 不得為了通過測試而刪除、停用或弱化測試。
11. 技術限制變更必須經 Human Reviewer 核准。

## 8. 測試失敗處理

當 G2～G6 失敗時：

1. AI Failure Analyst 分析失敗報告。
2. 判斷失敗原因與受影響範圍。
3. 建議由適當角色進行修正。
4. 修正角色只能修改授權範圍內的檔案。
5. 修正後重新執行相關測試及所有必要品質關卡。
6. 未經核准不得修改業務規則或 Gherkin 以取得 PASS。

## 9. 部署規則

1. 部署目標為 Raspberry Pi Ubuntu。
2. 目標機器預先安裝必要系統套件。
3. 使用 Python 虛擬環境及 systemd 執行網站。
4. 使用 GitHub Actions 透過 SSH 進行部署。
5. 部署前必須確認 G1～G6 全部通過。
6. G7 人工核准依環境設定。
7. CD 不執行部署後自動化測試。
8. 部署不得覆蓋 SQLite 資料庫及機密設定。
9. 部署完成後，由 Human Reviewer 自行進行功能驗證。

## 10. 核心原則

**人類決定需求與驗收標準，AI 負責在核准的規格範圍內產生測試、實作程式與維護自動化流程。**

當規格不明確時，先詢問，不得猜測。

當測試失敗時，先分析原因，不得透過修改驗收標準掩蓋問題。

---
