# AI-BDD-DEMO 最小介面約定

- **文件版本：** 0.1
- **文件狀態：** Draft
- **來源基底：** main `240d5eb7c576a5da2664e3e23bdd5a9f05ec338f`
- **核准狀態：** 尚未取得 Human Reviewer 對本文件的核准。

## 1. 用途與效力

本文件提出 Test Engineer 與 Developer 共用的最小接合設計，支援先建立測試、再實作應用程式。以下介面尚未實作；目前 `src/` 與各測試目錄僅有預留檔。

**Draft 不得當成已核准的正式介面依據。只有 Human Reviewer 明確核准後，後續 Agent 才能依此建立測試及實作。** 核准須對應文件版本或 commit，不能由 AI 自行更改狀態。

本文件不取代根目錄 [agents.md](../agents.md)、角色權限或已核准規格。若發生衝突，先回報，不以本文件覆寫規格。此次僅授權新增本文件，不擴大後續角色的修改範圍。

### 來源與設計的區分

| 類別 | 內容 |
|---|---|
| 既有規格要求 | 功能／業務規格 v1.1、技術規格 v1.0 及 AUTH-001～007；例如第三次失敗鎖定 60 秒、鍵盤焦點、SQLite、伺服器 Session、SSR |
| 本文件提出的設計 | Python 入口、函式及設定名稱、HTTP 路徑／狀態碼、表單標記、內部查詢介面 |
| 不在本批決定的事項 | 正式 Session 期限、SameSite 具體值、視覺與相容性尺度等後續提案事項 |

實際規格位置：
- [功能規格](../specs/functional/functional-spec.md)
- [業務規則](../specs/business/business-rules.md)
- [技術規格](../specs/technical/technical-spec.md)
- [Feature 索引](../features/feature-index.csv)
- [Developer 職責](../agents/developer.md)
- [Test Engineer 職責](../agents/test-engineer.md)

## 2. 應用入口與設定

建議採用 Developer 文件中的套件分工，入口為 `ai_bdd_demo.main:create_app`。這是候選設計，不代表 `src/ai_bdd_demo/` 已存在。完整模組內部布局不綁定測試。

候選函式介面：

```python
create_app(*, settings: AppSettings, clock: Clock | None = None) -> FastAPI
```

| 設定／參數 | 約定 |
|---|---|
| `settings.database_path` | SQLite 檔案的絕對路徑；測試明確提供暫存檔案路徑，不回退至正式資料庫 |
| `settings.secret_key` | 外部提供；測試使用臨時值，不寫入 Git 或日誌 |
| `settings.cookie_secure` | HTTPS 情境為 true；純 HTTP 測試環境可明確設為 false，不代表正式環境政策 |
| `settings.session_ttl_seconds` | 正整數、可配置；正式值待核准，測試明確指定隔離測試值 |
| `settings.cookie_samesite` | 可配置；測試值不升格為正式政策，正式值待核准 |
| `clock` | 提供 UTC 時間；未傳入時使用真正系統時鐘 |

匯入模組時不建立資料庫或預設會員。應用啟動生命週期初始化所指定的資料庫；關閉時釋放連線。測試執行相同生命週期，並支援使用不同設定建立多個獨立應用實例。

## 3. HTTP 路由及表單

以下狀態碼與命名屬本次技術設計，不新增業務判斷條件。

| 方法／路徑 | 回應約定 |
|---|---|
| `GET /login` | 200，回傳含完整登入表單的 HTML |
| `POST /login` 成功 | 303，Location 指向 `/welcome`，建立真正的伺服器端登入狀態 |
| `POST /login` 業務驗證失敗或鎖定 | 200，重新呈現登入頁及業務規格指定的錯誤訊息；不得因此新建登入狀態 |
| `POST /login` 缺少／無效 CSRF 證明 | 403，不完成登入；不額外約定錯誤文案或失敗計數變化 |
| `GET /welcome` 有效登入 | 200，HTML 含歡迎訊息 |
| `GET /welcome` 未登入 | 303，Location 指向 `/login` |

表單以 POST 提交至 `/login`：

| 元素 | 穩定介面 |
|---|---|
| 帳號欄 | `name="username"`、`id="username"`，有對應 label |
| 密碼欄 | `name="password"`、`id="password"`、`type="password"`，有對應 label |
| CSRF 欄 | 隱藏欄位 `name="csrf_token"`，由伺服器產生與驗證 |
| 登入按鈕 | 可及名稱「登入」、`type="submit"` |
| 重設按鈕 | 可及名稱「重設」，不提交登入請求 |
| 錯誤訊息 | `role="alert"` |
| Welcome 訊息 | `data-testid="welcome-message"`；不指定未核准的歡迎文案 |

正常登入測試先 GET 表單取得真正的 CSRF 證明，再 POST；不得停用安全機制。CSRF Token 可以使用安全實作所需的前置狀態，但不能把前置狀態誤判為已登入 Session。

## 4. SQLite 與內部資料介面

透過 `app.state.services` 取得正常內部服務物件。這不是 HTTP API；不得建立測試專用公開路由、繞過驗證參數或正式測試後門。

| 候選介面 | 行為 |
|---|---|
| `members.create(username, password_hash)` | 建立會員資料；不新增產品註冊功能。完成提交後可供其他應用連線讀取 |
| `members.get(username)` | 回傳會員的儲存資料（包含供內部驗證用的 password_hash），不存在回傳 None；不透過 HTTP 洩漏雜湊 |
| `auth.get_account_state(username)` | 回傳既有會員目前有效的 `failed_attempts`、`locked_until`、`is_locked`；不存在回傳 None |
| `sessions.get(session_id)` | 回傳有效 Session 的 `username`、`expires_at`，不存在或過期回傳 None |

上述回傳資料可用具名唯讀物件表示；資料表名稱、欄位布局及 SQL 由 Developer 決定，測試不固定資料庫 schema。不使用 getter 的回傳值作為唯一驗收依據，仍核對實際 HTTP 行為與持久化結果。

前置資料由測試使用實際雜湊機制與正常資料介面建立，不使用正式憑證。需要失敗兩次或已鎖定狀態時，透過真正的登入請求形成，不提供直接設定成功／鎖定結果的假介面。

## 5. 時鐘、到期與重新啟動

`Clock.now()` 回傳帶 UTC 時區的 datetime。帳號鎖定與 Session 到期皆使用此來源，不另讀取難以控制的全域時間。測試時鐘只控制時間，不計算登入結果。

- T 為第三次連續失敗的時刻。
- 測試直接調整到 T＋59、60、61 秒，不實際等待。
- 帳號到期後，狀態查詢與下一次登入應反映已解除鎖定、失敗次數重設；不強制使用背景排程更新 SQLite。
- 重新啟動測試：關閉應用生命週期，保留同一暫存 SQLite 檔案，以相同設定／時鐘重新建立應用，再驗證狀態與登入結果。
- 重啟不等於重設資料庫；不得重建資料掩蓋持久化缺陷。
- 每個測試案例使用獨立資料庫，案例內重啟才共用該案例原檔案。

## 6. 瀏覽器與 HTTP 測試的界線

真實瀏覽器測試使用上表的 label、role、id 辨識元素，不綁定 CSS 排版。重設驗收必須由應用本身實現：

1. 填入資料，按下「重設」。
2. 核對兩欄皆空，`document.activeElement` 為帳號欄。
3. 不重新點選欄位，直接用鍵盤輸入。
4. 核對文字進入帳號欄且密碼仍空白。

測試不得自行清欄位或呼叫 focus 代替產品功能。HTTP TestClient 不能證實鍵盤焦點或瀏覽器互動。

SSR 情境直接檢查 HTTP 原始 HTML 的欄位、按鈕及歡迎訊息，不只看 JavaScript 執行後 DOM。UI 重設可使用必要的少量瀏覽器腳本，不改變後端 SSR 架構。

瀏覽器測試的伺服器由測試 fixture 啟動真實應用，使用 loopback、臨時 port 及同一隔離資料庫。需要可控制時鐘的測試可在同一程序的獨立伺服器執行緒使用共享、執行緒安全的測試時鐘；不新增網路調時端點。

## 7. 安全、例外與並行接合

| 驗證 | 接合方式 |
|---|---|
| 密碼儲存 | 從正常內部資料介面讀取雜湊，使用真實演算法驗證測試密碼；不能只檢查字串與明文不同 |
| 日誌 | 應用使用標準 Python logging；測試擷取實際處理產生的日誌，確認沒有輸入的明文密碼 |
| Session | 同時核對 Cookie、對應伺服器紀錄及 Welcome 存取；不因 Cookie 存在就推定登入成功 |
| Cookie | 驗證 HttpOnly／SameSite 存在，HTTPS 情境有 Secure；HTTPS 的 Cookie 屬性與真實傳輸安全應分開驗證 |
| CSRF | 無效證明請求走正常路由，不替換安全驗證器；後續存取 Welcome 仍應未登入 |
| 受控內部錯誤 | 暫時替換測試實例正常資料介面的方法，使其拋出含測試標記的例外；仍執行真實路由與錯誤處理，驗證回應不洩漏標記／詳細錯誤 |
| 並行失敗計數 | 使用同一應用／SQLite，不同 Client 與獨立有效 CSRF 狀態同步送出請求；等待完成後核對真實狀態及後續登入行為 |

受控例外僅用於錯誤處理情境，不能將登入／鎖定核心替換成固定結果。必要的內部方法替換由測試工具暫時執行，測試結束還原，不新增正式應用的故障開關。HTTP 測試需捕捉應用回應而非讓測試工具直接重新拋出伺服器例外。

## 8. Feature 與介面對應

| Feature | 主要介面 |
|---|---|
| AUTH-001 | 登入路由、表單、會員資料、鍵盤焦點與重設瀏覽器操作 |
| AUTH-002 | 登入請求、帳號狀態、時鐘、獨立 Client |
| AUTH-003 | UTC 可控制時鐘、到期狀態與登入請求 |
| AUTH-004 | Session、Welcome 與重新導向 |
| AUTH-005 | 密碼欄、真實雜湊、日誌、Session／Cookie、CSRF、錯誤處理 |
| AUTH-006 | 隔離 SQLite、應用生命週期、重啟、時鐘與並行請求 |
| AUTH-007 | HTTP 原始 HTML，不以渲染後 DOM 代替 SSR 證據 |

## 9. 角色交接與所需環境

- **Human Reviewer：** 審查並明確核准本文件；決定真正影響業務預期的問題。
- **Test Engineer：** 核准後依此建立 BDD／fixtures／整合測試與覆蓋清單，僅修改 tests/ 授權範圍；缺主程式時如實回報，不建立假受測系統。
- **Developer：** 核准後實作入口與內部服務，依測試滿足規格；不修改測試預期或已核准 Feature。
- **DevOps：** 補齊相依套件、套件探索／建置／HTML 與靜態資源打包，以及 Runner 執行設定。

現有 pyproject.toml 已列 FastAPI、Uvicorn、Jinja2、python-multipart、argon2-cffi、pytest／pytest-bdd、HTTPX 及品質工具；尚未完成建置後端與套件探索。真實瀏覽器建議使用 pytest-playwright，需另由 DevOps 配置版本、瀏覽器與 Runner 系統依賴。若測試需要額外 HTML 解析工具，也由 DevOps 核對必要性後加入，不由測試角色越權修改設定。

正式執行證據以 GitHub Runner 為準。無主程式、缺依賴、測試收集錯誤與行為斷言失敗須分開回報；未執行或零個測試不是 PASS，也不因缺少模組而宣稱完成有效 Red。

## 10. 待定事項與限制

1. 本文件中所有介面名稱、狀態碼及選擇均是 v0.1 提案，待 Human Reviewer 核准；一般技術接合不要求逐一選參數。
2. 正式 Session 期限、SameSite 值、淡藍色樣本、瀏覽器與尺寸、輸入驗證及 XSS 覆蓋尺度，依角色文件留待後續方案與規格確認；不阻擋已明確情境的設計，不把測試設定當成產品需求。
3. 雜湊演算法強度、實際 HTTPS 部署、程式結構與品質關卡仍需安全／設定審查，本文件不是完整安全保證或部署指南。
4. Feature CSV 目前為小寫 approved，Feature README 仍描述 Pending Review；本次沿用 Human Reviewer 在對話的明確 Gherkin 核准，不修改狀態文件。
5. 部分來源引用 AGENTS.md 與 specs 平面路徑；本文件連結實際 agents.md 與規格子目錄，不擅自修正來源。
6. 本次只產生介面設計，沒有實作、執行測試或部署；不存在任何 G1～G7 新的 PASS 宣告。

## 11. 核准紀錄

- Human Reviewer：待填
- 核准版本／commit：待填
- 核准日期：待填
- 核准狀態：Pending（文件狀態維持 Draft）
