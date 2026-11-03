# 測試執行與交接

## 本批依據與狀態

本次在 `copy-main` 增量更新測試，依功能／業務規格 v1.1、技術規格 v1.2、[共用介面 v0.2](../docs/system-standard.md)、AUTH-001～008。
核對的 PR #14 候選 head 為 `77352e16af0c5193602248c320a171e0072ee6d2`；本次對話已明確核准 AUTH-004／006／008。CSV／Feature README 仍標 Pending Review，沒有修改來源或核准狀態。
根 agents.md 與 test-engineer.md 仍有 SQLite 舊敘述；本次依明確授權及新版共用介面改為 MariaDB，未修改規範文件。

這是測試編寫與靜態驗證階段。正式產品結果以 GitHub Runner 為準；收集、綁定或局部斷言工具成功不代表產品驗收成功。

## 結構與覆蓋

- `bdd/test_auth_001.py`～`test_auth_008.py`：40 個 Scenario／Outline、49 組展開案例，所有 Examples 均由 pytest-bdd 參數化。
- `bdd/steps.py`：保留既有登入、鎖定、CSRF、Cookie、安全、瀏覽器及 SSR 斷言；AUTH-006 兩步改為 MariaDB。
- `bdd/migration_steps.py`：AUTH-004 重啟 Session 與 AUTH-008 真實遷移工具的步驟。
- `conftest.py`／`mariadb_support.py`：每案例獨立 MariaDB 資料庫、正常 initialize_schema、真實應用、受控 UTC 時鐘、生命週期及安全清理。
- `migration_support.py`：建立舊版 SQLite 來源快照、備份及獨立 SQL 比對；沒有遷移實作或替代受測系統。
- `support.py`：真實 HTTP／服務轉接、原始 HTML 解析、可控制且執行緒安全的 UTC 時鐘；重啟保留 Cookie、資料庫與原設定，不重新初始化資料表。
- `integration/`：5 組案例，包含兩個獨立 MariaDB 應用隔離、Session TTL、無效 CSRF 及兩種錯誤訊息的真實瀏覽器可見性。
- `regression/test_review_assertions.py`：原 16 組斷言工具回歸完整保留。
- `regression/test_database_guards.py`：6 組測試基礎設施保護，包含不回退、公網拒絕、清理所有權及設定機密隱藏；不冒稱產品測試。
- `check_bindings.py`：靜態檢查每個 Scenario／Example 的唯一步驟、參數、顯式綁定及覆蓋清單。
- [COVERAGE.md](COVERAGE.md)：全部情境到測試函式與關鍵斷言的對應。

合計 76 組可收集案例：49 BDD＋5 integration＋22 infrastructure/assertion regression。
原 AUTH-001／002／003／005／007 測試與業務斷言不變；一般資料存取全部改走真實 MariaDB，SQLite 只用於遷移來源快照。

## DevOps：測試服務與環境設定

需要獨立、可拋棄的 **MariaDB 11.8.6**，不能使用樹莓派、正式 `bdd`、正式帳號或正式憑證。以下均為測試專用設定，不讀取 `AI_BDD_DB_*` 或正式設定：

| 設定 | 用途 |
|---|---|
| AI_BDD_TEST_DB_HOST | 明確指定 loopback（GitHub-hosted Runner 的服務對外映射）或 Docker service alias `mariadb`；不接受公網主機 |
| AI_BDD_TEST_DB_PORT | 明確指定測試服務映射 TCP Port |
| AI_BDD_TEST_DB_USER | 隔離服務測試帳號，可建立／刪除案例資料庫及建立結構，不擴大正式帳號權限 |
| AI_BDD_TEST_DB_PASSWORD | 測試專用密碼，由 Runner 提供；不寫進本文件、Git 或正式設定 |
| AI_BDD_TEST_DB_SERVER_ID | 啟動測試服務時明確設定的 server_id；每次連線核對 @@server_id |
| AI_BDD_TEST_DB_DISPOSABLE | 必須明確填 YES，確認服務為可拋棄測試服務 |

缺任何設定、服務版本不符、身分不符、服務不可用或缺驅動，都明確報錯。禁止退回 SQLite、正式連線或 skip。
連線等待最多 20 秒，只等待基礎設施就緒，不等待業務鎖定時間。

每案例建立 `bdd_test_<32位隨機hex>`，保存本程序 ownership registry 及該庫 `_bdd_test_owner` 隨機所有權標記。此表為測試基礎設施，不是應用資料或遷移來源。
清理重新驗證服務版本、server_id、完整名稱、程序 registry 與資料庫標記，只 DROP 該案例擁有的單一資料庫；不做模糊匹配／批次刪除。Client／應用／瀏覽器先關閉，才清理。身分或所有權不符即停止清理並報錯，保留資料供檢查；初始化標記失敗也不猜測性刪除。
這些保護不能代替 DevOps 提供真正隔離的服務。不要將正式服務轉發到 loopback 供測試。

需由 DevOps 補齊：

1. `PyMySQL`：只作 fixtures 的管理及獨立 SQL 觀察驅動，透過動態 import 在 fixture 執行時載入。產品驅動由 Developer 決定；需要的產品套件另行配置。請固定經 Runner 驗證的相容版本。
2. 既有 pytest 9.1.1、pytest-bdd 8.1.0、FastAPI／Starlette TestClient、HTTPX、argon2-cffi、Uvicorn、Ruff／Mypy 與 gherkin-official。
3. 既有 Playwright 1.64.0、匹配 Chromium 及 Linux 系統依賴。瀏覽器驗證不得改用 HTML 靜態檢查。
4. Runner 的 MariaDB 11.8.6 service、健康檢查、上述測試環境、隔離憑證與 schema 建立權限。此分支尚未修改 pyproject 或 Actions。
5. wheel 安裝後的驗證也需改成 MariaDB；目前 workflow 的舊 SQLite 設定不能證明新介面通過。必要時由 DevOps 拆分階段檢查。

## 執行方式

先準備可匯入的正式套件、開發依賴；下列三項不需要資料庫或主程式載入：

```sh
python -m tests.check_bindings
python -m pytest tests --collect-only -q
python -m ruff check tests
python -m mypy tests
```

環境及主程式就緒後，才執行正式產品測試：

```sh
python -m pytest tests/bdd --junitxml=reports/G2.xml
python -m pytest tests/integration --junitxml=reports/G6.xml
python -m pytest tests/regression --junitxml=reports/G3.xml
```

pytest fixtures 在執行階段載入主程式、驅動與測試設定。缺介面、收集失敗或缺環境不是有效行為 Red。
僅執行 `tests/regression/test_database_guards.py` 不需要服務、瀏覽器或受測應用，只驗證測試安全保護；不代表 MariaDB 產品行為。

## Developer：共用介面與真實受測系統

遵循 [system-standard.md v0.2](../docs/system-standard.md)，不另訂登入、資料服務或 HTTP 介面：

- 實作 MariaDB AppSettings 欄位、create_app、正常 `ai_bdd_demo.db.initialize_schema(*, settings)`、資料服務、交易及 UTC 時鐘。
- initialize_schema 每個新案例呼叫一次；重啟不重建資料表。測試使用原始 secret、Cookie 與 DB，驗證原失敗次數／期限／Session。
- 正常帳號鎖定前置狀態仍以真實登入請求建立；只有隔離 SQLite 遷移快照直接表示既有儲存資料。
- 既有兩 Client、獨立有效 CSRF、Barrier 並行驗證保留；不得以記憶體資料庫或 fake repository 替代。
- 真實瀏覽器負責焦點、重設與訊息可見性；AUTH-007 保留原始 HTTP HTML 的 SSR 驗證。
- 原 16 個 Cookie 編碼／訊息可見性斷言回歸保留，其通過不能證明產品安全全部有效。

### 尚未實作的正常遷移入口：最小交接提案

共用介面第 10 章要求欄位映射及全量遷移，但尚未指定呼叫名稱；現有 src 沒有遷移工具。依本次授權，測試採以下正常維護工具接合，供 Developer 實作，不聲稱它已存在：

```python
ai_bdd_demo.migration.migrate_sqlite_to_mariadb(
    *, source_path: pathlib.Path, target_settings: AppSettings
) -> MigrationReport

class MigrationReport:
    table_mapping: dict[str, str]  # SQLite 應用表 -> MariaDB 應用表
    column_mapping: dict[str, dict[str, str]]  # 來源表 -> 來源欄 -> 目標欄

class MigrationConflictError(Exception):
    ...
```

這是內部維護入口，不是公開路由、測試後門或第二套介面標準；一般應用介面仍以共用文件為準。
不固定目標表布局、游標或 SQL。回傳映射須對應真實結構，覆蓋全部來源應用表及欄位；測試使用獨立 SQL 連線讀取實際目標逐列比對，**不信任工具自報的成功旗標／筆數**。UTC datetime 與數值 epoch 可正規化為同一時間點；毫秒／秒或時區偏差不能被忽略。型別／結構需要其他轉換時，Developer 提供具體映射證據再協調測試，不自行忽略欄位。

來源快照使用目前 SQLite 的 members／sessions 真實欄位，包含原 Argon2、計數、UTC epoch、SHA-256 token_hash 及到期／過期 Session。
所有來源 writer 關閉／提交後才呼叫工具，並有本案例備份；遷移後檢查來源及備份 SHA-256 不變。測試只管理自己建立的快照，不模擬正式維護停機、部署切換或實際復原操作。
目標有同名會員時必須由真實工具回報 MigrationConflictError，且全部既有應用資料不被覆寫／刪除。測試不要求新的衝突處理策略。

## 本批檢查與限制（2026-11-03）

| 本地檢查 | 實際結果與界線 |
|---|---|
| Python 語法 | 22 個 Python 檔案 compile 通過 |
| 綁定與覆蓋 | 40 個 Scenario／Outline、49 展開案例、289 步驟唯一匹配；COVERAGE.md 一致 |
| pytest 收集 | 76 案例，未啟動主程式／資料庫 |
| Ruff | 全 tests/ 通過 |
| 嚴格 Mypy | 全 tests/ 22 檔通過 |
| 基礎設施安全保護 | 6 passed；只驗證本地 fixture guard，沒有假受測應用 |
| 既有內容保留 | 6 份既有 BDD 綁定檔及原 regression 內容不變；steps.py 除兩處 SQLite→MariaDB 文字外 AST 相同 |
| 真實 MariaDB／遷移／瀏覽器產品行為 | 未執行，待 Developer 與 DevOps 接續 |

本地 Python 3.12.2；pytest 9.1.1、pytest-bdd 8.1.0、Ruff 0.17.3、Mypy 1.20.2、PyMySQL 1.2.3、Playwright 1.64.0。
暫存隔離檢查環境另有 FastAPI 0.162.0／Starlette 1.10.0／HTTPX 0.28.1；收集發出既有 TestClient／HTTPX 淘汰提醒，沒有因此修改專案依賴，也不宣稱此組合已通過產品相容性測試。
現有主程式仍使用 SQLite 設定，尚缺 MariaDB initialize_schema、MariaDB 資料服務及遷移入口；沒有用假應用代替。
目前沒有配置本次隔離 MariaDB 服務／測試專用連線，未連線正式主機、未執行資料遷移或產品行為測試。
不手動觸發／重跑 Actions。Push／更新 PR 若自動觸發 CI，另列實際結果，不與本地靜態證據混稱。
