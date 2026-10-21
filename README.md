# AI-BDD-DEMO

以 AI 輔助行為驅動開發（AI-BDD）建立會員登入網站的示範專案。

本專案透過「規格 → Gherkin → 自動化測試 → 程式實作 → 品質檢查 → 部署」的流程，示範人類與不同 AI 角色如何分工協作。

## 專案狀態

目前已建立規格、AI 角色規範、Gherkin 草稿及 CI/CD 初始設定。

- `src/` 尚為預留目錄，尚未建立正式應用程式。
- `tests/` 各測試目錄尚為預留目錄。
- `deploy/` 尚未建立 systemd 服務設定。
- `pyproject.toml` 尚未完成套件探索與建置後端設定。
- 品質 workflow 目前僅手動觸發，不會因 Push／PR 自動執行。
- 全流程尚待實際驗證，不代表 G1～G7 已全部通過。

Feature 審核狀態請以 [Feature 索引](features/feature-index.csv)、
[Feature 清單](features/README.md) 及可查證的人工核准紀錄為準。

## 功能範圍

本版本包含：

- 會員登入表單與帳號、密碼驗證。
- 重設表單，清空帳號及密碼後將鍵盤焦點移至帳號欄。
- 登入成功後顯示 Welcome 頁面。
- 既有會員帳號第 3 次連續登入失敗，立即鎖定 60 秒。
- 鎖定期間拒絕登入，且再次嘗試不延長原鎖定期限。
- 登入成功或鎖定到期後，重設連續失敗次數。
- 不同帳號的失敗次數與鎖定狀態互相獨立。
- 不存在帳號一律顯示「帳號或密碼錯誤」。
- 未登入使用者不得直接存取 Welcome 頁面。

本版本不包含會員註冊、忘記密碼、第三方登入、多因素驗證或後台會員管理。

詳細行為以已核准規格為準，本 README 不取代規格文件。

## 技術選型

| 類別 | 技術 |
|---|---|
| 語言 | Python |
| Web Framework | FastAPI |
| Web Server | Uvicorn |
| 頁面呈現 | Jinja2、HTML、CSS |
| 資料儲存 | SQLite |
| 測試 | pytest、pytest-bdd |
| 程式品質 | Ruff、Mypy |
| 安全檢查 | Bandit、pip-audit |
| CI/CD | GitHub Actions |
| 目標環境 | Raspberry Pi Ubuntu |

Python 與套件需求記錄於 `pyproject.toml`。
遠端環境的實際版本由 Human Reviewer 手動維護，CI 環境需與其對齊。

## 目錄與檔案

| 目錄／檔案 | 功能說明 | 主要負責者 |
|---|---|---|
| `README.md` | 專案總覽、目錄說明與協作方式 | 人類審查與維護 |
| `agents.md` | 全專案共通流程、角色權限與品質規範 | Human Reviewer |
| `agents/` | 各 AI 角色的詳細工作規範 | Human Reviewer |
| `agents/analyst.md` | 需求分析、規格草稿與 Gherkin 管理 | AI Analyst |
| `agents/test-engineer.md` | 測試設計、fixtures 與測試驗證 | AI Test Engineer |
| `agents/developer.md` | 正式應用程式實作規範 | AI Developer |
| `agents/failure-analyst.md` | 失敗分析與修正建議規範 | AI Failure Analyst |
| `agents/devops.md` | 依賴、品質工具與 CI/CD 規範 | AI DevOps |
| `pyproject.toml` | Python 專案資訊、相依套件與工具設定 | AI DevOps |
| `specs/` | 專案規格文件 | Human Reviewer／AI Analyst |
| `specs/functional/functional-spec.md` | 功能範圍與需求 | Human Reviewer 定義與核准；AI Analyst 協助整理 |
| `specs/business/business-rules.md` | 登入、失敗次數、鎖定與錯誤訊息等業務規則 | AI Analyst 整理；Human Reviewer 核准 |
| `specs/technical/technical-spec.md` | 架構、安全、介面、測試與部署要求 | Human Reviewer 核准；相關 AI 角色提供建議 |
| `features/` | Gherkin 驗收標準 | AI Analyst |
| `features/feature-index.csv` | Feature ID、分類、檔名與審核狀態的主要索引 | AI Analyst |
| `features/README.md` | 依索引同步維護的人類可讀 Feature 清單 | AI Analyst |
| `features/AUTH-*.feature` | 登入相關 Given／When／Then 情境 | AI Analyst 產生；Human Reviewer 核准 |
| `src/` | 正式 Python 應用程式；目前僅有預留檔 | AI Developer |
| `tests/bdd/` | G2：依 Gherkin 建立 BDD 驗收測試；目前為預留目錄 | AI Test Engineer |
| `tests/regression/` | G3：回歸測試；目前為預留目錄 | AI Test Engineer |
| `tests/integration/` | G6：API、資料庫及 Session 等整合測試；目前為預留目錄 | AI Test Engineer |
| `deploy/` | 部署設定；目前僅有預留檔 | AI DevOps |
| `.github/workflows/quality-gates.yml` | 品質檢查 workflow；目前僅手動觸發，仍包含打包與上傳 jobs | AI DevOps |
| `.github/workflows/deploy.yml` | 承接指定品質 workflow 的部署驗證、G7 核准與檔案上傳 | AI DevOps |
| `docs/change-management.md` | 變更管理文件預留位置，目前為空檔 | 待 Human Reviewer 確認內容與責任 |

`src/ai_bdd_demo/`、`main.py`、`auth.py` 及
`deploy/ai-bdd-demo.service` 等檔案，應在後續任務依核准架構建立；
目前不視為已存在。

## 六個角色

| 角色 | 主要責任 | 預設修改範圍 |
|---|---|---|
| Human Reviewer | 決定需求、核准規格及驗收標準、審查交付 | 依專案管理權限 |
| AI Analyst | 分析需求、整理規格草稿、產生 Gherkin、維護索引 | 規格草稿、未核准 Feature、Feature 索引及清單 |
| AI Test Engineer | 依已核准 Gherkin 建立與維護測試 | `tests/` |
| AI Developer | 依規格及測試實作正式程式 | `src/` |
| AI Failure Analyst | 唯讀分析失敗原因、提出修正建議 | 原則上唯讀 |
| AI DevOps | 配置依賴、品質工具、CI/CD 與部署設定 | `.github/`、`deploy/`、`pyproject.toml` |

詳細權限以 `agents.md` 與對應角色文件為準。
超出預設範圍的修改須取得 Human Reviewer 授權。

AI 角色是工作分工，不代表工具會自動啟動多個 Agent。

## 開發流程

1. Human Reviewer 提出需求。
2. AI Analyst 分析並釐清需求，建立規格草稿。
3. Human Reviewer 核准規格。
4. AI Analyst 產生 Gherkin 草稿並執行語法檢查。
5. Human Reviewer 核准 Gherkin，完成 G1。
6. AI Test Engineer 建立測試，提供 Scenario 與測試的對應。
7. AI Developer 實作程式，讓行為符合核准規格與測試。
8. GitHub Runner 執行適用的 G2～G6。
9. 失敗時由 AI Failure Analyst 分析，再交對應角色修正。
10. 必要關卡通過、取得適用的 G7 核准後，才允許部署。
11. Human Reviewer 手動驗證遠端功能。

Gherkin 已產生、程式已提交、測試已通過及需求已核准，
是不同狀態，不得互相代替。

## 品質關卡

| Gate | 檢查內容 | 必須通過 |
|---|---|---|
| G1 | Gherkin 語法與 Human Reviewer 需求核准 | 是 |
| G2 | pytest／pytest-bdd 驗收測試 | 是 |
| G3 | Regression Tests | 是 |
| G4 | Ruff／Mypy：Lint 與 Type Check | 是 |
| G5 | Bandit／pip-audit：安全檢查 | 是 |
| G6 | Build／Integration Tests | 是 |
| G7 | Deployment Approval | 依環境 |

- 人工核准必須有可查證紀錄。
- 零個測試、略過、未執行或忽略錯誤，不得視為 PASS。
- 正式自動檢查結果以 GitHub Runner 為準。
- 測試使用隔離資料庫，不連線正式資料庫。
- 時間相關測試使用可控制的時間來源。
- 不得為了通過檢查而弱化測試或改動已核准規則。

## GitHub Actions 現況

目前 `quality-gates.yml` 使用：

```yaml
on:
  workflow_dispatch:
```

因此 Push／PR 不會自動啟動品質檢查。
這是規格與 Gherkin 建立階段的暫時安排。

未來程式與測試就緒後，再由 AI DevOps 配置 Push／PR 自動檢查，
並確認 `deploy.yml` 正確承接同一個 commit 的成功結果。

目前兩份 workflow 尚需整合驗證：

- `quality-gates.yml` 仍保留上傳 job。
- `deploy.yml` 也提供上傳流程。
- 現有部署條件要求來源事件為 Push，手動執行品質 workflow
  不會符合該條件。

正式啟用部署前，須移除重複上傳責任並確認觸發條件，
不能將公版設定視為已完成驗證。

## 部署原則

- 遠端作業系統、Python 與套件由 Human Reviewer 手動安裝及維護。
- 目前約定的部署工作僅上傳必要專案檔案。
- 不在遠端安裝套件、建立虛擬環境、遷移資料庫或重啟服務。
- 不執行部署後自動化功能測試。
- 不覆蓋正式 SQLite 資料庫、Session、環境設定或機密。
- 不將密碼、Token 或 SSH 私鑰寫入版本控制。
- SSH 必須驗證遠端主機身分。
- 上傳成功僅代表傳輸完成，不代表網站已切換版本或功能正常。

上傳路徑、清單及核准方式以實際部署設定與任務授權為準。

## 開始 AI 任務

每次任務應明確指定：

- Repo。
- AI 角色及對應的 `agents/*.md`。
- 本次目標與允許修改範圍。
- 分支名稱及是否授權 commit、push、開 PR。
- 完成條件與回報要求。

AI 必須先讀取共通規範與角色文件，不自行擴張權限。
規格不明確時提出問題；不受影響的工作可繼續進行。

## 文件維護

- 業務行為以已核准規格為準，不以 README 範例取代。
- Feature 增修須同步維護 CSV 與 Feature README。
- 只有取得核准紀錄，才能將 Feature 設為 `Approved`。
- 本 Repo 根目錄目前檔名為 `agents.md`；
  部分文件內稱為 `AGENTS.md`，閱讀時須核對實際檔案。
- 目錄、工具或流程變更後，應同步更新本 README。