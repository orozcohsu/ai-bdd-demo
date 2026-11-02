# 應用程式實作與交接

依據：功能／業務 v1.1、技術 v1.0、AUTH-001～007、已核准 `docs/system-standard.md` v0.1，以及測試 PR #4 合併後的 main `5bb38b56367b2bf055760e430ba72526ac47558d`。本文件只記錄本次實作與操作資訊，不另定跨角色介面或業務規則。

## 模組職責

| 模組 | 責任與 Feature |
|---|---|
| `ai_bdd_demo/main.py` | FastAPI 路由、CSRF、Cookie、HTML 與通用錯誤回應；AUTH-001、004、005、007 |
| `ai_bdd_demo/auth.py` | 真實 Argon2id 驗證、帳號計數／鎖定、UTC 時鐘、伺服器端 Session；AUTH-001～006 |
| `ai_bdd_demo/db.py` | SQLite 初始化、會員資料及每次操作的連線／交易；AUTH-005、006 |
| `ai_bdd_demo/config.py` | 已核准 settings 屬性的型別與驗證、外部環境變數載入 |
| `templates/`、`static/` | Jinja2 SSR、共用 CSS、重設後的鍵盤焦點；AUTH-001、004、005、007 |

以少量組合式服務分離責任，沒有多層繼承或插件框架。Auth 的狀態讀取、到期重設、計數與 Session 建立在 SQLite `BEGIN IMMEDIATE` 交易內完成，避免並行失敗遺失計數。密碼驗證在執行緒池執行，避免阻塞 HTTP 事件迴圈。

會員密碼只接受內部介面傳入的雜湊，不新增產品註冊功能。Session 使用隨機 opaque token，SQLite 只儲存其 SHA-256 指紋與 UTC 到期時間，不把帳號或密碼編碼塞入 Cookie。CSRF 使用帶 HMAC 簽章的隨機 double-submit 證明，正常 GET／POST 均使用相同防護，不新增測試開關。
所有連線在每次操作後關閉；匯入不建立資料庫，lifespan 初始化、不清空既有資料。沒有全域預設會員、正式密碼或 secret。

## 啟動與設定

測試依既有約定呼叫 `create_app(settings=..., clock=...)`。操作環境也可使用 `ai_bdd_demo.main:create_app_from_environment` 的 Uvicorn factory。此入口不替代既有 create_app 介面。

以下環境變數全部必填，沒有把測試值設成正式預設：

| 變數 | 內容 |
|---|---|
| `AI_BDD_DATABASE_PATH` | SQLite 絕對路徑；父目錄須預先存在且可寫，放在受控持久化資料區 |
| `AI_BDD_SECRET_KEY` | 外部管理的隨機機密，不寫入程式、Git、日誌或命令列 |
| `AI_BDD_SESSION_TTL_SECONDS` | 正整數；正式期限須由 Human Reviewer 決定 |
| `AI_BDD_COOKIE_SAMESITE` | lax／strict／none；正式值須由 Human Reviewer 決定 |
| `AI_BDD_COOKIE_SECURE` | true／false；正式 HTTPS 環境使用 true；none 也要求 true |

套件與上述變數齊備後，可由 Repo 根目錄執行：

```sh
python -m uvicorn ai_bdd_demo.main:create_app_from_environment --factory --app-dir src
```

未提供必要設定會停止啟動，不回退到正式資料庫或測試憑證。SQLite 目錄權限、secret 管理、HTTPS、服務帳號與 systemd 均由操作環境／DevOps 維護，本次未連線遠端或部署。

## 本地驗證方式

pyproject 尚未完成套件探索／建置。本次只在程序的 `PYTHONPATH` 加入 Repo 的 src 絕對路徑，使用既有暫存 venv、SQLite tmp_path 與暫存 Chromium；未修改相依或 CI 設定。

```sh
python -m pytest tests/bdd tests/integration tests/regression -q
python -m ruff check src tests
python -m mypy src tests
python -m bandit -r src
python -m pip_audit
```

最終本地結果（2026-10-22）：

| 檢查 | 結果與限制 |
|---|---|
| 既有 BDD／integration／regression | 62 passed（41＋5＋16），52.26 秒；包含真實 Chromium；1 個既有 Starlette／HTTPX 淘汰提醒 |
| Ruff | src 與 tests 通過 |
| 嚴格 Mypy | 22 個 Python 檔案通過 |
| Bandit | src 掃描無發現，exit 0 |
| pip-audit | exit 1：隔離驗證環境 pip 24.0 回報 12 筆已知漏洞列項（含重複 ID）；其餘被掃描套件未回報，不代表未來無漏洞 |
| 暫存複本 Build | `build --no-isolation` 能產生 sdist／wheel，但 wheel 缺 templates／static；安裝至暫存 target 後，create_app 因缺 static 目錄而失敗；不能宣稱可部署建置通過 |
| GitHub Runner | 未執行；未 dispatch Actions，正式 Gate 未確認 |

建置在暫存來源複本進行，沒有將產物或 metadata 留在 Repo。沒有修改測試或依賴設定來讓檢查通過。正式 G2～G6 仍以 GitHub Runner 的實際結果為準；本地通過不代表 Gate 已核准。

## 給 DevOps 與 Human Reviewer

- 明確設定建置後端、src 套件探索與 templates／static 套件資料打包。已證實現行 setuptools fallback 只打包 Python 模組，缺 `templates/*.html`、`static/*.css`、`static/*.js`；DevOps 修正後須重新安裝 wheel，從 Repo 外驗證真實建立應用與頁面／資源回應。本次不修改 pyproject。
- 核對並更新 Runner 的安裝工具，處理 pip 24.0 的 audit 發現；本次未越權更新依賴或以忽略規則隱藏漏洞。
- 固定並核對執行環境依賴；瀏覽器測試需要匹配的 Playwright／Chromium 與 Runner 系統依賴。
- 完成 CI Variables、品質工作與部署隔離。現有 workflow 含上傳 jobs，不應為執行測試誤觸正式上傳。本次未 dispatch。
- 決定正式 Session 期限／SameSite、精確視覺色碼、瀏覽器與尺寸矩陣、輸入驗證／XSS 的額外驗收尺度。本次 CSS 是可檢視的淡藍色呈現，沒有宣稱色碼或完整跨瀏覽器政策已獲核准。
- 本次以參數化 SQL、Jinja2 自動 escaping、字串型別檢查、必要欄位及 CSRF 保護已明確的流程；不自行新增帳號格式、密碼強度或長度等業務限制。
- 內部 members.create 是正常資料服務，不是公開註冊／管理 API。測試資料只由隔離測試建立；正式會員建立方式不在本版本公開功能範圍內。
