# AI-BDD-DEMO 技術規格

**文件版本：** 1.0
**文件狀態：** Approved（已核准）
**核准角色：** Human Reviewer

## 第一章：系統架構

### TECH-001：應用程式架構

1. 使用 Python 3.12 或相容版本開發。
2. 使用 FastAPI 作為 Web Framework。
3. 使用 Uvicorn 執行 Web Application。
4. 系統採用 Server-Side Rendering（SSR），由 Python 後端產生 HTML。
5. 使用 Jinja2 作為 HTML Template Engine。
6. 第一版不使用 React、Vue 等前端框架。

### TECH-002：資料儲存

1. 使用 SQLite 儲存會員帳號及登入狀態。
2. 資料庫檔案放置於部署環境的持久化資料目錄。
3. 資料庫不得放入 Git Repository。
4. 帳號登入失敗次數及鎖定到期時間必須持久化儲存。

---

## 第二章：網頁介面設計

### UI-001：視覺風格

1. 網站以淡藍色作為主要視覺色調。
2. 登入頁與 Welcome 頁採用一致的設計風格。
3. 網頁須支援桌面與手機瀏覽器。
4. 使用 HTML、CSS 實作，不依賴大型前端框架。

### UI-002：登入頁面

1. 提供帳號輸入欄位。
2. 提供密碼輸入欄位，密碼不得以明文顯示。
3. 提供登入按鈕。
4. 登入失敗時，於頁面顯示對應的錯誤訊息。

### UI-003：Welcome 頁面

1. 登入成功後顯示 Welcome 頁面。
2. 顯示歡迎訊息。
3. 未登入的使用者不得直接進入 Welcome 頁面。

---

## 第三章：登入與安全設計

### SEC-001：密碼安全

1. 密碼不得以明文儲存。
2. 使用安全的密碼雜湊演算法，例如 Argon2id。
3. 不得將密碼寫入 Log。
4. 不得在程式碼中硬編碼正式環境密碼或 Secret Key。

### SEC-002：Session 管理

1. 使用伺服器端 Session 管理登入狀態。
2. 瀏覽器只保存不含敏感資料的 Session ID。
3. Session Cookie 設定 HttpOnly、SameSite，HTTPS 環境啟用 Secure。
4. Session 必須具備有效期限。
5. 未登入使用者存取 Welcome 頁面時，導向登入頁。

### SEC-003：帳號鎖定

1. 登入失敗次數及鎖定到期時間由伺服器端管理。
2. 依據已核准的 business-rules.md 實作。
3. 使用 UTC 儲存鎖定時間。
4. 不得依賴瀏覽器端計數來判定帳號鎖定。
5. 連續登入失敗次數與鎖定狀態的更新須避免併發請求造成計數錯誤。

### SEC-004：Web 安全

1. 正式環境使用 HTTPS。
2. 登入表單須具備 CSRF 防護。
3. 所有輸入必須進行伺服器端驗證。
4. HTML 輸出須避免 XSS 風險。
5. 不得將機密資訊或詳細系統錯誤顯示給使用者。

---

## 第四章：程式碼結構

### CODE-001：模組責任

1. `main.py`：建立 FastAPI Application、註冊路由。
2. `auth.py`：實作登入驗證、登入失敗計數及帳號鎖定。
3. `templates/`：存放登入頁與 Welcome 頁的 HTML。
4. `static/`：存放 CSS 等靜態資源。
5. 資料庫存取邏輯應與網頁路由分離，避免所有程式碼集中於 main.py。

### CODE-002：程式品質

1. 使用 Python Type Hints。
2. 使用 Ruff 執行 Lint。
3. 使用 Mypy 執行 Type Check。
4. 使用 pytest、pytest-bdd 執行自動化測試。

---

## 第五章：測試與品質關卡

### QA-001：品質檢查

所有程式變更必須通過：

- G1：Gherkin 語法檢查與 Human Reviewer 需求核准。
- G2：pytest-bdd 驗收測試。
- G3：Regression Tests。
- G4：Ruff / Mypy。
- G5：Bandit / pip-audit。
- G6：Build / Integration Tests。

G1 的人工核准不得以自動化語法檢查取代。

### QA-002：測試要求

1. 測試不得依賴正式環境資料庫。
2. 測試應使用隔離的 SQLite 資料庫。
3. 帳號鎖定時間測試應使用可控制的時鐘，不以實際等待 60 秒進行。
4. 已核准的 Gherkin 不得由 AI Developer 為了讓測試通過而自行修改。

---

## 第六章：部署環境

### DEPLOY-001：目標環境

1. 部署目標為 Raspberry Pi Ubuntu。
2. 目標機器事先安裝必要的 Python Runtime 與系統套件。
3. 使用 Python Virtual Environment 執行應用程式。
4. 使用 systemd 管理 FastAPI 服務。
5. SQLite 資料庫與部署程式分開保存，部署不得覆蓋既有資料。

### DEPLOY-002：持續部署

1. GitHub Actions 執行 G1～G6 品質檢查。
2. G1～G6 全部通過後，才允許進入 CD。
3. CD 使用 SSH 將已通過檢查的版本部署至 Raspberry Pi。
4. CD 不重新安裝作業系統套件。
5. CD 不執行部署後自動化測試；正式環境功能由 Human Reviewer 手動驗證。
6. 部署須避免覆蓋正式環境的 Secret、Session 資料及 SQLite 資料庫。
7. G7 部署核准依環境設定；正式環境預設須經人工核准。

---

## 第七章：規格優先順序

1. `functional-spec.md`：功能範圍。
2. `business-rules.md`：業務行為與判斷條件。
3. `technical-spec.md`：技術實作與非功能限制。
4. `features/*.feature`：經 Human Reviewer 核准的可執行驗收情境。

若規格間出現衝突，AI 不得自行選擇其中一個版本，必須回報 Human Reviewer 釐清。

---

## 第八章：核准紀錄

- **核准角色：** Human Reviewer
- **核准狀態：** Approved
- **核准版本：** 1.0
- **核准日期：** 2026-10-21

---