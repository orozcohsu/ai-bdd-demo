# 測試執行與交接

本批依 Human Reviewer 本次明確核准、main `84983924bf4fec2beff6a910b052208b42c831bb` 的功能／業務 v1.1、技術 v1.0、AUTH-001～007，以及 [system-standard.md v0.1](../docs/system-standard.md) 建立。
本文件記錄測試用法，不另訂應用介面。正式測試證據以 GitHub Runner 為準。

## 結構與覆蓋

- `bdd/test_auth_001.py`～`test_auth_007.py`：32 個 Scenario／Outline，Examples 展開為 41 個案例。
- `bdd/steps.py`：共用步驟與實際斷言；[完整情境對應](COVERAGE.md)。
- `conftest.py`：每案例 tmp_path SQLite、真實應用生命週期、真實 Chromium／loopback 伺服器 fixtures。
- `support.py`：介面轉接、執行緒安全 UTC 測試時鐘、原始 HTTP HTML 解析；沒有替代產品的登入或鎖定實作。
- `integration/test_contract.py`：獨立資料庫／應用隔離、可配置 Session 期限、無效 CSRF 值，3 個整合案例。
- `check_bindings.py`：靜態稽核 Scenario 顯式綁定、每組 Examples、步驟唯一匹配與參數解析；不是行為測試。
- `regression/`：保留既有預留檔，尚無明確 Bug 回歸需求，不為湊數新增。零案例不代表 G3 PASS。

| Feature | 展開案例數 | 主要證據／斷言函式（`bdd/steps.py`） |
|---|---:|---|
| AUTH-001 | 12 | `form_fields`、`reset`／`focused`／`typed_username`、`success`、`all_errors`、`count` |
| AUTH-002 | 8 | `count`、`is_locked`、`lock_deadline`、`named_count`、`a_still_locked` |
| AUTH-003 | 4 | `timed_login`、`unlocked`、`count`、`success` |
| AUTH-004 | 4 | `redirect_welcome`、`welcome_message`、`denied_welcome` |
| AUTH-005 | 7 | `masked`、`real_hash`、`safe_logs`、`opaque_session`、`cookie_attribute`、`csrf_rejected`、`generic_error` |
| AUTH-006 | 4 | `restart`／`timed_restart`、`clean_browser`、`concurrent_failures`、`count`、`is_locked` |
| AUTH-007 | 2 | `form_fields`、`submit_button`、`ssr_welcome`（直接使用 HTTP response.text） |

`Scenario Outline` 的空字串 Examples 也包含在內。瀏覽器重設測試只由產品清欄位／移動焦點，測試不呼叫 focus；後續直接 keyboard.type 驗證實際鍵盤行為。
鎖定前置狀態全部透過真實錯誤登入建立。並行請求使用同一真實應用與 SQLite、兩個獨立 Client／CSRF，Barrier 同步送出並等待完成。

## 執行方式

由 Repo 根目錄執行，先由 DevOps 準備下節環境與可匯入的正式應用：

```sh
python -m tests.check_bindings
python -m pytest tests --collect-only -q
python -m pytest tests/bdd/ --junitxml=reports/G2.xml
python -m pytest tests/integration/ --junitxml=reports/G6.xml
python -m ruff check tests
python -m mypy tests
```

`pytest tests/regression/` 目前為零測試（預期 exit 5），不得記作通過。DevOps／Human Reviewer 應決定尚無 Bug 歷史時的正式 G3 政策；本批不更改關卡或 CI。
不需要正式資料庫或外部主機憑證。測試 secret 隨案例隨機產生；測試會員均為隔離資料。時間以受控時鐘推進，不等待鎖定的 60 秒。

## 給 Developer

請實作已核准 [system-standard.md](../docs/system-standard.md) 第 2～7 節；本批沒有新增入口、路由、公開測試後門或其他介面標準。

- 目前 `src/` 只有預留檔。應用匯入延至 fixture 執行階段；缺少模組會明確失敗，不 skip，也不當成有效 Red。
- `support.TestSettings` 只是承載約定的 settings 屬性，不是產品設定驗證器；不綁定未指定的 AppSettings 模組。`database_path` 使用絕對 Path。
- 初始會員經 `app.state.services.members.create` 提交真實 Argon2 雜湊；正常路由仍須以真實演算法驗證密碼，不可依測試帳號特判。
- `auth.get_account_state` 只作狀態證據之一，同時驗證實際登入拒絕、錯誤訊息及 Welcome 存取。重啟關閉 lifespan，保留同一 SQLite 檔案再建立新應用。
- Session Cookie 名稱不固定；從實際 Cookie 找到可對應 `sessions.get` 的有效紀錄，並核對會員、期限、Welcome 與竄改 ID 拒絕。
- 受控例外僅暫時以 monkeypatch 替換該測試實例的 `members.get`，使真實路由／錯誤處理收到帶標記的 RuntimeError；先證明 5xx，再檢查回應沒有機密或堆疊。
- 真實瀏覽器與 TestClient 共用已初始化應用，瀏覽器的 Uvicorn 關閉重複 lifespan；應用須遵循隔離連線與並行存取約定。
- 測試 Session TTL 300 秒、SameSite=lax、HTTP cookie_secure=false 均為隔離測試設定，不是正式政策。HTTPS Cookie 案例明確設定 secure=true；TestClient HTTPS 不證明正式 TLS。

## 給 DevOps

本次未修改 `pyproject.toml` 或 Actions：

1. 既有依賴包含 pytest／pytest-bdd／HTTPX／FastAPI／Uvicorn／argon2-cffi 與 Ruff／Mypy。請補齊正式套件建置／探索，使 `ai_bdd_demo.main` 可匯入；現有 pyproject 仍為初始化版本，不能把安裝或建置失敗當成測試失敗證據。
2. 真實瀏覽器需 `playwright` Python 套件及匹配的 Chromium／Runner 系統依賴。fixture 直接使用同步 Playwright API，不依賴 pytest-playwright plugin；如選用該 plugin，它會帶入 Playwright。請依 Runner／維護政策固定相容版本，再執行 `python -m playwright install --with-deps chromium`（只在 Runner）。
3. 本地結構驗證使用 Python 3.12.2、pytest 9.1.1、pytest-bdd 8.1.0、Ruff 0.17.1、Mypy 1.20.2、Playwright 1.64.0；這是驗證紀錄，不要求遠端正式環境安裝測試套件或採用這些版本。
4. 現有 `quality-gates.yml` 只由 workflow_dispatch 觸發，仍依賴 CI_PYTHON_VERSION、APP_CODE_PATH、APP_IMPORT_MODULE 等 Variables，且含上傳 jobs。未改動、未 dispatch；本次 push 不等於有 Runner 測試證據。請在另一次授權任務補齊測試環境／套件及關卡設定，避免誤觸上傳。
5. 目前依賴解析環境的 Starlette TestClient 發出 HTTPX 淘汰提醒；收集未被阻擋。請在鎖定依賴時核對相容性，不把警告當成產品功能通過證據。

## 本批實際驗證與限制（2026-10-21）

| 檢查 | 結果及範圍 |
|---|---|
| 本地 pytest collection | 44 案例正常收集：41 BDD＋3 integration；未匯入尚不存在的應用 |
| 本地步驟稽核 | 32 Scenario／Outline、41 展開案例、230 步驟均唯一匹配；參數與 fixture 名稱靜態解析成功 |
| 本地 Ruff | `ruff check tests` 通過（只表示本批 lint） |
| 本地 Mypy | `mypy tests` 嚴格設定通過（外部動態服務仍需實作後整合驗證） |
| 本地單案例試跑 | `test_valid_login` 失敗：缺少 ai_bdd_demo；fixture 無法建立受測應用，尚未進入業務斷言，不是有效 Red |
| GitHub Runner | 未執行；無正式 G2～G6 PASS 證據 |
| 真實瀏覽器／全套行為 | 未執行；缺主程式，亦未安裝／啟動 Chromium |
| Build／G5／部署 | 未執行；非本次範圍 |
| 故意破壞產品行為／mutation | 未執行；待實作後驗證第三次鎖定、60 秒邊界、重設焦點、CSRF 等錯誤能被斷言抓到 |

所有案例已完成測試內容編寫；本地未發現尚待修正的收集／步驟／lint／型別問題。執行可靠性仍需真實主程式與 Runner 證據，不能宣稱全部證實。

## 文件差異及既有範圍限制

Feature CSV 為 approved；Feature README 表格仍為 Pending Review。system-standard 頁首為 approved，但仍留有 Draft／待核准的舊提案文字。本批依 Human Reviewer 本次明確核准繼續，沒有自行改動來源文件或狀態。
部分來源引用大寫 AGENTS.md 或 specs 平面路徑，本批使用實際 agents.md 及 specs/functional、business、technical 目錄。
視覺色碼／相容性矩陣及未具體化的輸入／XSS 驗收尺度不在這 32 個已核准情境中；沒有自行新增規則，也不阻擋已明確案例。
