# AI-BDD-DEMO 技術規格

**文件版本：** 1.1  
**文件狀態：** Approved
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

重設按鈕及鍵盤焦點行為，依已核准功能規格與業務規則辦理。

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

正式 Session 期限與 SameSite 具體政策須經 Human Reviewer 確認。隔離測試使用的設定值，不得直接視為正式政策。

### SEC-003：帳號鎖定

1. 登入失敗次數及鎖定到期時間由伺服器端管理。
2. 依據已核准的 `specs/business/business-rules.md` 實作。
3. 使用 UTC 儲存鎖定時間。
4. 不得依賴瀏覽器端計數來判定帳號鎖定。
5. 連續登入失敗次數與鎖定狀態的更新，須避免併發請求造成計數錯誤。

### SEC-004：Web 安全

1. 正式環境使用 HTTPS。
2. 登入表單須具備 CSRF 防護。
3. 所有輸入必須進行伺服器端驗證。
4. HTML 輸出須避免 XSS 風險。
5. 不得將機密資訊或詳細系統錯誤顯示給使用者。

---

## 第四章：程式碼結構

### CODE-001：模組責任

正式應用程式放在 `src/`，各模組適當分離職責：

1. `main.py`：建立 FastAPI Application、註冊路由。
2. `auth.py`：實作登入驗證、登入失敗計數及帳號鎖定。
3. `templates/`：存放登入頁與 Welcome 頁的 HTML。
4. `static/`：存放 CSS 等靜態資源。
5. 資料庫存取邏輯應與網頁路由分離，避免所有程式碼集中於 main.py。

應用入口及共用介面遵循已核准的 `docs/system-standard.md`。不得為配合局部實作，自行改變跨角色介面約定。

### CODE-002：程式品質

1. 使用 Python Type Hints。
2. 使用 Ruff 執行 Lint。
3. 使用 Mypy 執行 Type Check。
4. 使用 pytest、pytest-bdd 執行自動化測試。
5. 一般函數、類別與組合方式，由 AI Developer 依需求及既有架構合理選擇。
6. 不為套用 Design Pattern 而增加不必要的複雜度。
7. 影響重要架構或既有共用介面的設計變更，須先提出方案並取得核准。

---

## 第五章：測試與品質關卡

### QA-001：品質檢查

所有程式變更必須符合以下品質要求：

| Gate | 檢查內容 |
|---|---|
| G1 | Gherkin 語法、索引一致性及有效的人類需求／Gherkin 核准紀錄 |
| G2 | pytest-bdd 驗收測試 |
| G3 | Regression Tests |
| G4 | Ruff／Mypy |
| G5 | Bandit／pip-audit |
| G6 | Build／Integration Tests |

G1 包含自動檢查與人工核准，兩者不得互相取代。

人工核准依 `agents.md`，以 Human Reviewer 審查並合併對應規格／Gherkin PR 的可查證紀錄為依據。

不要求額外建立 `requirements-review` Environment，也不要求每次 Actions 執行都重新核准相同需求與 Gherkin。

規格與 Gherkin 未變且核准紀錄仍有效時，可以沿用既有核准；受影響內容變更後，必須重新審查。

CI 應驗證核准紀錄與目前內容的對應。紀錄缺漏或無法確認時，標示「核准尚未驗證」，不得宣稱 G1 PASS。

Gherkin PR 合併前的語法檢查，不得等待同一個 PR 已合併才執行，以免形成循環依賴。

G2～G6 由工具自動執行，但不取代 Human Reviewer 對重要變更的 PR 審查。人類合併 PR，不會讓失敗、跳過或未執行的檢查變成 PASS。

### QA-002：測試要求

1. 測試不得依賴正式環境資料庫。
2. 測試應使用隔離的 SQLite 資料庫。
3. 帳號鎖定時間測試應使用可控制的時鐘，不以實際等待 60 秒進行。
4. 已核准的 Gherkin 不得由 AI Developer 為了讓測試通過而自行修改。
5. 測試程式放在 `tests/`，依已核准情境與共用介面約定執行。
6. 鍵盤焦點及訊息可見性等瀏覽器行為，使用真實瀏覽器驗證。
7. SSR 檢查應直接驗證原始 HTTP HTML，不以瀏覽器渲染後 DOM 取代。
8. 零個測試、收集失敗、環境錯誤、逾時與未執行，不得視為 PASS。
9. 主程式未實作造成的匯入或環境錯誤，不得宣稱為有效的行為 Red。

### QA-003：Runner 與建置驗證

1. 正式自動檢查在 GitHub Runner 的隔離環境執行。
2. Runner 安裝所需 Python、正式依賴、測試工具及匹配的瀏覽器。
3. 記錄實際受測 commit、OS、Python 與相依版本。
4. 本地驗證可作為開發證據，但不取代正式 Runner 結果。
5. 建置產物須包含必要模板與靜態資源。
6. 在隔離環境安裝 wheel，從 Repo 外驗證真實應用、頁面與必要資源。
7. 建置或 import 成功，不代表完整的安裝與整合驗證通過。
8. Runner 環境與 Raspberry Pi 實機不同，應如實記錄尚未驗證的架構與版本相容性限制。

---

## 第六章：部署環境

### DEPLOY-001：目標環境

1. 部署目標為 Raspberry Pi Ubuntu。
2. 目標機器的 Python Runtime、系統與 Python 套件，由 Human Reviewer 手動安裝及維護。
3. 使用 Python Virtual Environment 執行應用程式。
4. 使用 systemd 管理 FastAPI 服務。
5. SQLite 資料庫與部署程式分開保存，部署不得覆蓋既有資料。
6. 正式 Session、環境設定與機密，須與可覆寫的應用程式檔案分開保護。

### DEPLOY-002：持續部署

1. GitHub Actions 執行 G1 自動檢查與核准紀錄驗證，以及 G2～G6。
2. G1～G6 全部通過後，且符合必要部署授權及 G7 要求，才允許進入 CD。
3. CD 使用 SSH 傳輸已通過檢查版本的指定必要檔案。
4. 必須確認上傳內容與受測版本一致，不以當下最新 main 取代已驗證版本。
5. 品質檢查與部署流程分開；PR 品質工作不得取得部署憑證或觸發正式上傳。
6. CD 不刪除遠端既有檔案，不覆蓋 Secret、Session、環境設定及 SQLite 資料庫。
7. CD 不執行部署後自動化測試；正式環境功能由 Human Reviewer 手動驗證。
8. G7 依環境政策設定；正式環境預設須經人工核准。
9. G1 採用 PR 核准紀錄，不會取消 G7 的部署核准。

### DEPLOY-003：遠端操作限制

本專案預設 CD 僅上傳經授權的必要專案檔案。

除非另有明確授權，不得在遠端：

- 安裝、更新或移除系統與 Python 套件。
- 建立虛擬環境。
- 執行建置或資料庫遷移。
- 啟動或重啟服務。
- 執行測試。
- 切換正式服務指向的版本路徑。

必要的服務操作及功能驗證，由 Human Reviewer 手動執行。

上傳成功只表示檔案傳輸完成，不表示網站已更新或功能正常。

---

## 第七章：規格與介面文件的關係

| 文件 | 主要責任 |
|---|---|
| `specs/functional/functional-spec.md` | 功能範圍 |
| `specs/business/business-rules.md` | 業務行為與判斷條件 |
| `specs/technical/technical-spec.md` | 技術實作與非功能限制 |
| `features/*.feature` | 經核准的可執行驗收情境 |
| `docs/system-standard.md` | 經核准的跨角色共用介面約定 |

上述文件共同約束實作，不得僅因某份文件列在前面，就自動忽略其他文件。

若規格、Gherkin 或介面約定互相衝突，AI 必須回報 Human Reviewer，不得自行選擇其中一個版本。

正式 Session 期限、SameSite 具體值、精確視覺色碼、瀏覽器與尺寸矩陣，以及額外輸入驗證／XSS 驗收尺度，未明確核准時不得自行當成既定產品要求。

不受待確認事項影響的工作可以繼續。

---

## 第八章：核准紀錄

### 既有版本

- **核准角色：** Human Reviewer
- **核准狀態：** Approved
- **核准版本：** 1.0
- **核准日期：** 2026-10-21

上述紀錄僅適用於 v1.0，不代表本次修訂已核准。

### 本次修訂

- **文件版本：** 1.1
- **核准狀態：** Pending Review
- **待核准角色：** Human Reviewer
- **核准 PR／版本紀錄：** 待核准後填寫
- **核准日期：** 待核准後填寫

本次主要調整：

1. 明確 G1 以對應規格／Gherkin PR 的人類審查及合併紀錄作為核准依據。
2. 移除每次 CI 必須額外進行 Environment 核准的假設。
3. 補充測試、Runner 與安裝後建置驗證要求。
4. 明確遠端環境由人類維護，CD 預設只上傳必要檔案。
5. 修正實際文件路徑與介面文件的關係。

文件修訂不會自動修改既有 workflow；後續須在授權任務內同步調整及驗證。

---