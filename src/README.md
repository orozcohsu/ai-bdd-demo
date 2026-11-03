# MariaDB 應用程式與遷移交接

依據：功能／業務規格 v1.1、技術規格 v1.2、共用介面 v0.2、已核准 AUTH-004／006／008，以及 PR #15 的既有 tests/。本次只改 src/，不修改測試、相依設定、CI 或來源規格。

## 模組與驗收對應

| 模組 | 責任／Feature |
|---|---|
| config.py | MariaDB settings、外部環境驗證、機密 repr 隱藏；共用介面第 2 章 |
| db.py | 正常 initialize_schema、結構相容性檢查、會員資料、操作範圍連線／交易；AUTH-005／006 |
| auth.py | Argon2、原失敗計數與 60 秒邊界、UTC、持久化 Session；AUTH-001～006 |
| main.py | 保留路由、表單、CSRF、Cookie、SSR／錯誤回應；啟動只驗證結構，不建表／遷移；AUTH-001／004／005／007 |
| migration.py | 正常維護入口、全量盤點與搬移、衝突及回傳映射；AUTH-008 |

不新增公開 HTTP API、預設會員、測試開關、SQLite runtime fallback 或額外業務規則。以既有服務組合延伸，不導入 ORM 或繼承框架。

## MariaDB 設定與初始化

create_app(settings=..., clock=...) 與 create_app_from_environment 保留。
明確提供 AI_BDD_DB_HOST／PORT／NAME／USER／PASSWORD、AI_BDD_SECRET_KEY、AI_BDD_COOKIE_SECURE、AI_BDD_SESSION_TTL_SECONDS、AI_BDD_COOKIE_SAMESITE。
AI_BDD_DB_CONNECT_TIMEOUT_SECONDS 是唯一有預設值的連線設定，預設 10 秒。舊 AI_BDD_DATABASE_PATH 不再讀取。
必要設定缺漏、無效整數／Cookie 設定會失敗，錯誤不帶輸入值；AppSettings 的 db_password／secret_key 不出現在 repr。

操作員先建立指定資料庫，再明確呼叫正常 `ai_bdd_demo.db.initialize_schema(*, settings)`。
初始化不建立資料庫或預設會員、不搬資料、不清空或 ALTER 已有表。先檢查所有既有應用表的欄位、型別、主鍵、InnoDB、文字表示與外鍵，遇不相容即停止。
MariaDB DDL 有隱含提交，因此新結構建立不是可回滾的資料遷移交易；若建表失敗，可能留下已完成的空表。應確認原因與現況後再執行初始化，不自動刪表。
一般應用 lifespan 只檢查結構，缺表即回報需明確初始化；關閉時不刪資料。

## 資料表示與一致性

- 使用 PyMySQL，純 Python、不需 MariaDB C connector，動態載入於真正連線時。驅動例外轉成不含 SQL／參數／憑證的 DatabaseError。
- InnoDB、參數化 %s、autocommit=False；寫入提交、例外回滾，連線／游標每次操作結束關閉。
- 帳號狀態使用 `SELECT ... FOR UPDATE` 後，在同一交易內處理到期重設、累計、鎖定與成功 Session 建立。未存在會員仍走原一致錯誤訊息，不新增鎖定。
- username 使用 utf8mb4 LONGTEXT 保存原字串，以原 UTF-8 的 SHA-256 二進位鍵作索引／外鍵；讀取仍逐字確認原 username。避免 VARCHAR 索引長度迫使新增業務帳號長度限制，也不讓資料庫忽略大小寫或尾端空白。雜湊鍵碰撞時失敗，不合併帳號。
- 密碼雜湊原字串以 LONGTEXT 保存。failed_attempts 為非負 BIGINT；locked_until／expires_at 使用 DOUBLE UTC epoch 秒，保留既有 SQLite REAL 的浮點表示；外部服務仍回傳帶 UTC 時區 datetime。
- Session token_hash 保留既有 SHA-256 小寫 hex 表示，Cookie session_id／csrf_proof 與 HMAC、期限判定均保留。過期記錄不刪除，也不重新視為有效。
- 不依 SQL 比較字串的排序規則判定登入帳號；無自動 trim／lowercase。

## 正常遷移入口

```python
from ai_bdd_demo.migration import migrate_sqlite_to_mariadb

report = migrate_sqlite_to_mariadb(
    source_path=source_snapshot_path,
    target_settings=settings,
)
```

入口符合 tests/README.md 最小接合。回傳 MigrationReport.table_mapping、column_mapping 與 row_counts；衝突拋 MigrationConflictError，其餘不相容／驗證問題為 MigrationError，DB 連線問題亦會明確失敗。
這段只說明 API，本次未對正式資料執行。

| SQLite 表／欄位 | MariaDB 對應 |
|---|---|
| members.username／password_hash／failed_attempts／locked_until | 同名表與同名欄位，保留原值 |
| sessions.token_hash／username／expires_at | 同名表與同名欄位，包含已過期 Session |
| 會員／Session 關聯 | 額外 username_key，依原 username 計算，InnoDB 外鍵連至 members |

呼叫前操作員必須停止來源及目標寫入、完成並保護一致的來源備份、準備空目標應用表、保留原 Secret／Cookie 設定。這是正式操作前置要求，不代表本任務已獲部署／遷移授權。

工具行為：

1. 來源以 SQLite mode=ro／query_only 及一致讀取交易開啟，不寫入、不刪除來源或備份。若存在非空 WAL，要求先完成一致快照，不代替操作員 checkpoint。
2. 盤點全部非 sqlite_* 應用表與欄位。目前只支援現有 members／sessions 的完整已知結構；遇未知表或額外欄位即在寫入前拒絕，不能悄悄略過資料。後續新增表須補映射後再搬移。
3. 驗證資料型態、唯一性、Session 指紋與會員關聯；不修改原 hash、計數、鎖定／Session 期限，不依目前時間過濾資料。
4. 目標結構必須事先初始化且相容；任何既有應用資料都回報衝突，不 merge／upsert／REPLACE，不覆寫或刪除目標資料。其他非應用表不處理。
5. 全部 DML 與逐欄／列驗證在單一 MariaDB 交易內完成；來源 hash 在提交前再確認未變。正常衝突、驗證或 SQL 錯誤回滾。
6. 若連線在 commit 期間中斷，客戶端無法保證是否已提交；會明確失敗，要求核對目標後再重試／切換，不宣稱一定回滾或自動重跑。
7. 不更改外部連線設定、不停啟服務、不切換部署、不自動復原。備份及失敗後人工核對仍由操作流程負責。

目前以記憶體盤點登入系統的來源快照；大型 ETL 或大資料遷移須另設計串流、容量及恢復策略，不宣稱適用無限資料量。

## DevOps 接續

1. 將 `PyMySQL==1.2.3` 加入正式依賴並執行相依／安全檢查；本次不得修改 pyproject。fixtures 亦使用相同驅動。若 MariaDB 帳號採 ed25519，另核對 PyMySQL[ed25519] 及其 ARM 依賴；不自行切換帳號驗證方式。
2. PyMySQL 官方聲明為 pure Python、CPython >=3.9，提供 py3-none-any wheel，因此可避免本驅動的 32-bit ARM 二進位 wheel 問題；Python 3.13.5／ARM 實機與 MariaDB 11.8.6 組合仍待真正驗證。其他套件（例如 Argon2）亦需分別確認。
3. Runner 配置 tests/README.md 的隔離 MariaDB 11.8.6、測試專用 AI_BDD_TEST_DB_*、帳號／建庫權限、匹配 Chromium。不得連線正式 bdd 或正式主機。
4. 舊 G6 wheel smoke 仍以 SQLite 路徑建立 AppSettings，須改成新版 MariaDB settings、明確初始化隔離結構，再從 Repo 外驗證 wheel。舊 smoke 不能繼續使用；本次不越權改 CI。
5. 初始化帳號與一般應用帳號權限分開；本次未變更正式權限或 Environment／Secrets。

技術依據：
- https://pypi.org/project/PyMySQL/1.2.3/
- https://pymysql.readthedocs.io/en/latest/modules/connections.html
- https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/selecting-data/for-update
- https://mariadb.com/docs/server/reference/sql-statements/transactions/sql-statements-that-cause-an-implicit-commit

## 本次驗證與限制

本地 Python 3.12.2，暫存驗證環境，不修改專案依賴。
| 本地檢查 | 本次結果 |
|---|---|
| src Python 語法 | 通過，6 個 Python 模組 |
| Ruff（src tests） | 通過 |
| 嚴格 Mypy（src tests） | 通過，28 檔 |
| Bandit（src） | 通過，未加入 nosec 或規則忽略 |
| pytest 收集 | 76 案例正常收集 |
| 綁定／覆蓋 | 40 Scenario／Outline、49 展開案例、289 步驟唯一匹配 |
| 局部程式檢查 | 設定機密 repr、帳號鍵大小寫／尾空白區分、create_app 不連 DB、未知 SQLite 表拒絕且來源 bytes 不變 |

局部檢查沒有假資料庫或假登入系統，但也未執行 MariaDB 整合。暫存環境補裝 Jinja2、python-multipart 與 Bandit，只供本地匯入／掃描，不修改專案相依設定。
本地沒有可用 MariaDB；Docker CLI 存在但 Engine 未啟動。不自行啟動或安裝服務，不連線樹莓派替代。
因此真實 MariaDB、並行／持久化、全量遷移、真實應用瀏覽器及 ARM 相容性尚未驗證；不將靜態成功宣稱產品 PASS。
Push 自動 CI 另行唯讀觀察，不手動觸發／重跑；正式結果以 Runner 為準。
