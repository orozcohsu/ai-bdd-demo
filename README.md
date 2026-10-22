# AI-BDD-DEMO

以 AI 輔助行為驅動開發（AI-BDD）建立會員登入網站的示範專案。

本專案透過「規格 → Gherkin → 自動化測試 → 程式實作 → 品質檢查 → 部署」的流程，示範人類與不同 AI 角色如何協作。

**人類決定需求與驗收標準，AI 依核准內容產生測試、實作程式及維護自動化流程。**

本 README 提供專案總覽，不取代已核准規格、角色規範或實際檢查紀錄。

## 1. 專案狀態

以下為 2026-10-22 核對的狀態：

| 項目 | 狀態 |
|---|---|
| Gherkin AUTH-001～AUTH-007 | 已建立，可追溯至人類合併的 [PR #2](https://github.com/orozcohsu/ai-bdd-demo/pull/2) |
| 共用介面約定 | 已建立，見 [system-standard.md](docs/system-standard.md) |
| 測試程式 | 已透過 [PR #4](https://github.com/orozcohsu/ai-bdd-demo/pull/4) 合併 |
| 正式主程式 | 已實作於 [PR #5](https://github.com/orozcohsu/ai-bdd-demo/pull/5)，尚未合併 |
| Runner、打包與新版 G1 驗證 | 位於 [PR #7](https://github.com/orozcohsu/ai-bdd-demo/pull/7)，尚未合併，承接 PR #5 |
| G2～G6 | 已在 PR #7 的受測版本通過 Runner 檢查 |
| G1 | Gherkin 語法及七份 Feature 核准追溯成功；文件一致性及來源規格核准證據仍待補正 |
| 正式部署 | 未執行 |

main、工作分支與 PR 測試版本可能包含不同內容。查看檔案或執行指令前，應先確認目前分支及 commit。

目前不能宣稱 G1～G7 已全部通過，也不能宣稱正式網站已部署或可用。

## 2. 功能範圍

本版本包含：

- 帳號與密碼登入表單。
- 重設表單，清空帳號及密碼，將鍵盤焦點移至帳號欄。
- 正確登入後建立登入狀態並顯示 Welcome 頁面。
- 既有會員帳號第 3 次連續登入失敗，立即鎖定 60 秒。
- 鎖定期間拒絕登入，且再次嘗試不延長原鎖定期限。
- 登入成功或鎖定到期後，重設連續失敗次數。
- 不同帳號的失敗次數與鎖定狀態互相獨立。
- 不存在帳號維持相同錯誤回應，不套用既有會員鎖定規則。
- 未登入使用者不得直接存取 Welcome 頁面。
- SQLite 持久化、伺服器端 Session、密碼雜湊及 CSRF 防護。
- Server-Side Rendering（SSR）頁面呈現。

本版本不包含：

- 會員自行註冊。
- 忘記密碼或密碼重設。
- Email 驗證。
- 第三方登入。
- 多因素驗證。
- 後台會員管理。

詳細行為以已核准規格及 Gherkin 為準。

## 3. 技術選型

| 類別 | 技術 |
|---|---|
| 語言 | Python 3.12 或相容版本 |
| Web Framework | FastAPI |
| Web Server | Uvicorn |
| 頁面呈現 | Jinja2、HTML、CSS、必要的少量 JavaScript |
| 資料儲存 | SQLite |
| 密碼驗證 | Argon2id |
| 自動化測試 | pytest、pytest-bdd |
| 瀏覽器測試 | Playwright／Chromium |
| 程式品質 | Ruff、Mypy |
| 安全檢查 | Bandit、pip-audit |
| CI/CD | GitHub Actions |
| 目標環境 | Raspberry Pi Ubuntu、Python venv、systemd |

Python 與套件需求由 [pyproject.toml](pyproject.toml) 管理。

正式遠端環境由 Human Reviewer 手動安裝及維護。Runner 測試成功，不代表 Raspberry Pi 的 ARM 架構、實際作業系統及套件版本已全部驗證相容。

## 4. 目錄與檔案

下表說明各目錄責任。尚未合併的實作，須在對應 PR 分支查看。

| 目錄／檔案 | 功能說明 | 主要負責者 |
|---|---|---|
| `README.md` | 專案總覽、進度與使用入口 | Human Reviewer／經授權的文件維護者 |
| `agents.md` | 共通流程、角色權限及品質規範 | Human Reviewer |
| `agents/` | 各 AI 角色的詳細工作規範 | Human Reviewer |
| `agents/analyst.md` | 需求分析、規格與 Gherkin 管理 | AI Analyst 依此執行 |
| `agents/test-engineer.md` | 測試設計、fixtures 與驗證 | AI Test Engineer 依此執行 |
| `agents/developer.md` | 主程式實作與設計原則 | AI Developer 依此執行 |
| `agents/failure-analyst.md` | 失敗分析與修正建議 | AI Failure Analyst 依此執行 |
| `agents/devops.md` | 建置、品質關卡與 CI/CD | AI DevOps 依此執行 |
| `pyproject.toml` | 專案資訊、依賴、打包與工具設定 | AI DevOps |
| `specs/functional/functional-spec.md` | 功能範圍與需求 | Human Reviewer／AI Analyst |
| `specs/business/business-rules.md` | 登入、鎖定及錯誤訊息規則 | AI Analyst／Human Reviewer |
| `specs/technical/technical-spec.md` | 架構、安全、品質與部署要求 | Human Reviewer／相關 AI 角色 |
| `docs/system-standard.md` | 測試與主程式共用的介面約定 | Human Reviewer 核准；授權角色維護 |
| `features/` | Gherkin 驗收情境 | AI Analyst |
| `features/feature-index.csv` | Feature ID、分類、檔名與狀態索引 | AI Analyst |
| `features/README.md` | Feature 管理規則、清單與核准追溯 | AI Analyst |
| `src/` | 正式應用程式及實作交接資訊 | AI Developer |
| `tests/` | 自動化測試與測試輔助程式 | AI Test Engineer |
| `tests/bdd/` | G2：BDD 測試與 Step Definitions | AI Test Engineer |
| `tests/regression/` | G3：既有回歸測試 | AI Test Engineer |
| `tests/integration/` | G6：API、資料庫、Session 等整合測試 | AI Test Engineer |
| `tests/conftest.py` | 共用 fixtures 與隔離環境 | AI Test Engineer |
| `tests/README.md` | 執行方式、證據限制及角色交接 | AI Test Engineer |
| `tests/COVERAGE.md` | Feature／Scenario 對應測試 | AI Test Engineer |
| `deploy/` | 經授權的部署與服務設定 | AI DevOps |
| `.github/workflows/quality-gates.yml` | Runner 環境與品質檢查 | AI DevOps |
| `.github/workflows/deploy.yml` | 部署前置驗證、G7 與檔案傳輸 | AI DevOps |

共通規範應放在根目錄 `agents.md`，不得誤放於 `features/README.md`。

目錄用途不代表其中所有檔案均已建立、合併或啟用。

## 5. 六個角色

| 角色 | 主要責任 | 預設修改範圍 |
|---|---|---|
| Human Reviewer | 決定需求、核准規格與驗收標準、審查 PR 並決定合併 | 依專案管理權限 |
| AI Analyst | 分析需求、整理規格與 Gherkin 草稿、維護索引及追溯 | 授權的規格草稿、Feature、索引與清單 |
| AI Test Engineer | 建立、審查與修正測試 | `tests/` |
| AI Developer | 依規格、介面約定與測試實作主程式 | `src/` |
| AI Failure Analyst | 分析失敗原因並提出證據與修正建議 | 原則上唯讀 |
| AI DevOps | 配置依賴、建置、Runner、品質檢查及部署流程 | `.github/`、`deploy/`、`pyproject.toml` |

詳細權限以 [agents.md](agents.md)、對應角色文件與本次任務授權為準。

角色文件是工作指示，不代表 Agent 可以自行核准、合併或擴大修改範圍，也不代表工具會自動啟動多個 Agent。

## 6. 開發流程

1. Human Reviewer 提出需求。
2. AI Analyst 分析、釐清並產生規格草稿。
3. Human Reviewer 審查並核准規格。
4. AI Analyst 產生 Gherkin 草稿，執行語法及一致性檢查。
5. Human Reviewer 審查並合併對應 Gherkin PR，留下 G1 人工核准紀錄。
6. 必要時先建立並核准共用介面與重要設計。
7. AI Test Engineer 建立測試，提供情境與斷言對應。
8. AI Developer 實作主程式，符合規格、介面約定及測試。
9. AI DevOps 配置 Runner，驗證 G1 紀錄並執行 G2～G6。
10. 失敗時分析原因，交由負責角色修正。
11. Human Reviewer 審查 PR，決定是否合併。
12. 必要關卡通過並取得適用的 G7 核准後，才允許部署。
13. Human Reviewer 手動進行正式環境功能驗證。

AI-BDD 不取代系統分析與設計。重要架構與跨模組介面應留下可審查的設計；一般函數、類別與組合方式由 Developer 在既有規範內合理決定。

## 7. 品質關卡

| Gate | 檢查內容 | 必須通過 |
|---|---|---|
| G1 | Gherkin 語法、索引一致性與有效的人類核准紀錄 | 是 |
| G2 | pytest-bdd 驗收測試 | 是 |
| G3 | Regression Tests | 是 |
| G4 | Ruff／Mypy | 是 |
| G5 | Bandit／pip-audit | 是 |
| G6 | Build／Integration Tests | 是 |
| G7 | Deployment Approval | 依環境 |

### G1 核准方式

依共通規範，Human Reviewer 審查並合併對應規格／Gherkin PR，留下可查證的核准紀錄。

規格與 Gherkin 未變且紀錄仍有效時，可以沿用核准，不要求每次 Actions 重複核准，也不以 `requirements-review` Environment 為必要機制。

核准紀錄缺漏或與目前內容不一致時，應回報「核准尚未驗證」，不得自行改成 PASS。

### 結果判讀

- 工具通過、人類核准及部署核准是不同證據。
- 人類合併 PR，不會讓失敗的自動檢查變成成功。
- 零個測試、跳過、收集失敗、逾時及未執行，不得視為 PASS。
- 本地成功不能取代正式 GitHub Runner 結果。
- 部分檢查成功不代表所有關卡通過。
- Gate 結果必須對應實際受測版本。

## 8. 最近一次 Runner 證據

[Actions Run 39748776268](https://github.com/orozcohsu/ai-bdd-demo/actions/runs/39748776268) 驗證 PR #7：

- 分支 head：`c55deb0afc8a63561b465f8d8e22d40e07af082d`
- 實際 checkout SHA：`1832e6bc18cb36d65fd8823bcc360a941c1466db`
- checkout 版本為 GitHub 產生的 PR 測試合併 commit，不代表已合併 main。

| Gate | 該次結果 |
|---|---|
| G1 | 未通過：README 一致性與來源規格核准證據仍有缺口 |
| G2 | PASS：41 個 BDD 案例 |
| G3 | PASS：16 個既有斷言工具回歸案例 |
| G4 | PASS：Ruff／Mypy |
| G5 | PASS：Bandit 及依賴稽核，當次無回報弱點 |
| G6 | PASS：5 個整合案例及 wheel 安裝、頁面與資源驗證 |
| G7／正式部署 | 未執行 |

G1 已成功追溯 AUTH-001～AUTH-007 至人類合併的 PR #2。三份來源規格的核准補正及文件一致性，仍須由負責角色處理。

此表是特定版本的歷史證據，不表示後續 commit 自動通過。文件修正後須核對新的執行結果。

## 9. 測試與本地驗證

請先閱讀：

- [測試執行與交接](tests/README.md)
- [情境覆蓋對應](tests/COVERAGE.md)
- 含主程式的分支內之 `src/README.md`

在包含主程式、測試與所需依賴的版本中，由 Repo 根目錄執行：

```sh
python -m tests.check_bindings
python -m pytest tests/bdd/
python -m pytest tests/regression/
python -m pytest tests/integration/
python -m ruff check src tests
python -m mypy src tests
python -m bandit -r src
python -m pip_audit
```

執行前必須確認：

- 正式應用程式可匯入。
- 已安裝該版本需要的依賴與瀏覽器。
- 資料庫與設定均為隔離測試用途。

不以假主程式、固定成功或測試專用公開後門取代受測系統。

測試失敗時，先判斷是環境、測試、主程式或規格問題，不得任意修改測試預期取得 PASS。

## 10. GitHub Actions

品質工作由 [quality-gates.yml](.github/workflows/quality-gates.yml) 定義；部署工作由 [deploy.yml](.github/workflows/deploy.yml) 定義。

PR #7 提供的品質流程包含：

- PR 至 main、push 至 main 及手動觸發。
- 標準 GitHub-hosted Ubuntu Runner。
- Python、正式與開發依賴安裝。
- 匹配的 Playwright／Chromium 與系統依賴。
- G1 核准追溯及 G2～G6 檢查。
- Job Summary、測試與掃描報告。
- Repo 外安裝 wheel 並驗證應用與資源。

在 PR #7 合併前，main 的 workflow 仍可能是較舊設定，應以所選分支的實際 YAML 為準。

品質流程不應取得部署憑證或自動上傳正式主機。部署流程必須另外符合來源版本、品質、artifact、授權及 G7 條件。

Actions 入口：
[查看工作流程與報告](https://github.com/orozcohsu/ai-bdd-demo/actions)

## 11. 部署原則

- 目標為 Raspberry Pi Ubuntu。
- 正式 OS、Python、套件、虛擬環境與服務由 Human Reviewer 手動安裝及維護。
- CD 預設只上傳明確授權的必要檔案。
- 不自動安裝套件、建立虛擬環境、執行建置或資料庫遷移。
- 不自動啟動、重啟服務或切換正式版本路徑。
- 不執行部署後自動化測試。
- 不刪除既有遠端檔案，不覆蓋正式資料庫、Session、環境設定或機密。
- SSH 必須驗證主機身分。
- 密碼、Token、私鑰與 Secret 不得寫入 Git。
- 上傳成功只表示傳輸完成，不表示網站已更新或功能正常。

具體目標目錄、上傳清單與核准條件，以已確認的部署設定及本次任務授權為準。

## 12. 開始 AI 任務

每次任務應指定：

- Repo 與 AI 角色。
- 本次目標、分支名稱及修改範圍。
- 應讀取的規範與相關文件。
- 是否授權 commit、push、開 PR 或執行 Actions。
- 是否授權部署；未授權時不得自行部署。
- 完成條件、證據與回報方式。

AI 必須先讀取 [agents.md](agents.md) 及對應的 `agents/*.md`，不得只依 prompt 範例猜測專案規則。

## 13. 文件維護

- 根目錄 `README.md`：專案總覽。
- 根目錄 `agents.md`：共通 Agent 工作規範。
- `agents/*.md`：各角色工作規範。
- `features/README.md`：Feature 管理、清單與核准追溯。
- `tests/README.md`：測試操作與交接。
- `docs/system-standard.md`：已核准的共用介面約定。

文件更新應依實際內容與證據，不把草稿、未合併分支或尚未執行工作宣稱為完成。

Feature 變更須同步維護 CSV、清單及適用的核准紀錄。

目錄、流程或 PR 狀態改變後，應更新本 README；根目錄介紹文件的更新，不會自動修改 workflow 或補足 G1 證據。

---