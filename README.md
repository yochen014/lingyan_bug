# Social Media Scraper (社群媒體爬蟲工具)

這是一個基於 Python 的工具，旨在幫助使用者透過關鍵字在特定的時間內收集社群媒體（Threads、Facebook、PTT）上的文章與留言資料。抓取到的資料會被整理成條列式的表格（CSV 或 Excel），包含發佈時間、帳號、內容以及原始連結。

## 核心功能
*   **多平台支援**：一次搜尋 PTT、Threads 與 Facebook。
*   **關鍵字搜尋**：精準抓取包含特定字眼的內容。
*   **時間過濾**：可指定追蹤過去幾天內的資料（例如最近 7 天）。
*   **格式匯出**：支援匯出為 `.csv` 或 `.xlsx` (Excel) 格式，方便後續分析。

---

## 安裝與環境設置

1.  **安裝 Python 依賴項**：
    確保您的電腦已安裝 Python 3.10+，接著在專案目錄執行：
    ```powershell
    python -m pip install playwright beautifulsoup4 requests pandas openpyxl
    ```

2.  **初始化瀏覽器核心**：
    本工具使用 Playwright 模擬瀏覽器行為，請執行以下指令安裝瀏覽器元件：
    ```powershell
    python -m playwright install chromium
    ```

---

## 如何使用 (操作說明)

您可以使用 `main.py` 來啟動爬蟲。以下是常用的指令範例：

### 1. 基本搜尋 (預設為 7 天，匯出為 CSV)
```powershell
python main.py "您的關鍵字"
```

### 2. 指定搜尋天數與 Excel 格式 (推薦)
如果您想要搜尋最近 3 天的內容，並直接產出 Excel 表格：
```powershell
python main.py "您的關鍵字" --days 3 --format xlsx
```

### 3. 指定抓取平台
只想要抓取 PTT 和 Threads，不抓取 Facebook：
```powershell
python main.py "您的關鍵字" --platforms ptt threads
```

### 參數清單：
*   `keyword`: (必要) 您要搜尋的目標關鍵字。
*   `--days`: (選用) 往前追蹤的天數。預設值為 `7`。
*   `--format`: (選用) 匯出格式，可挑選 `csv` 或 `xlsx`。
*   `--platforms`: (選用) 欲搜尋的平台。可複選：`ptt`, `threads`, `facebook`。

---

## 輸出結果
執行完成後，系統會自動在專案下建立一個 `output/` 資料夾，所有的結果檔案都會存放在裡面，檔名會標註搜尋的關鍵字與時間戳記。

*   **平台 (Platform)**：顯示內容來源（如 PTT 或 Threads）。
*   **時間 (Time)**：貼文或留言的發佈時間。
*   **帳號 (Account)**：發佈者的 ID。
*   **內容 (Content)**：貼文或留言的文字。
*   **連結 (URL)**：該貼文的完整網址，方便點擊回原站查看。

---

## 注意事項與限制
*   **Meta 平台 (FB/Threads)**：由於防爬蟲機制非常嚴格，目前的抓取是以「公開、非登入」的狀態進行，搜尋結果可能有限。若遇到讀取不到內容，可能是 IP 被暫時限制或需要登入驗證。
*   **PTT 看板**：目前預設搜尋 `Gossiping` (八卦)、`Stock` (股票)、`C_Chat` (動漫)。如需擴充，請至 `main.py` 修改看板清單。
