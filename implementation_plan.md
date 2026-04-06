# 社群媒體爬蟲實作計畫

本計畫旨在建立一個基於 Python 的工具，用於根據關鍵字和時間範圍抓取多個社群媒體平台（Threads、Facebook、PTT）的文章/貼文和留言。

## 需要用戶確認

> [!IMPORTANT]
> **爬取政策與限制**: 
> - **Threads 和 Facebook (Meta)**: Meta 平台有嚴格的反爬蟲措施。在沒有帳號或使用自動化工具的情況下進行爬取，可能會導致臨時 IP 封鎖或帳號停權（如果已登入）。該腳本將使用無頭瀏覽器 (Playwright) 來盡量減少被偵測的風險，但對於大規模操作不保證其穩定性。
> - **PTT**: 相對開放，但目前缺乏一次搜尋所有看板的「全域」關鍵字搜尋功能。該工具需要指定目標看板（例如：Gossiping、Stock）或在熱門看板中進行搜尋。
> - **時間範圍過濾**: Threads 和 Facebook 的公開搜尋功能並不總是提供精確的「按日期篩選」功能。我們需要先爬取動態牆內容，然後再透過程式過濾日期。

## 擬議變更

### 平台模組

#### [NEW] [scraper_ptt.py](file:///c:/Users/yoche/Desktop/NYCU/lingyan/scraper_ptt.py)
使用 `requests` 和 `BeautifulSoup` 爬取 PTT 貼文的模組。
- 在特定看板內按關鍵字搜尋。
- 根據貼文元數據過濾日期。
- 提取推文（留言）。

#### [NEW] [scraper_threads.py](file:///c:/Users/yoche/Desktop/NYCU/lingyan/scraper_threads.py)
使用 `Playwright` 搜尋 Threads 並提取貼文/留言的模組。
- 自動滾動以加載更多結果。
- 提取相對時間（例如 "3h", "1d"）並轉換為實際的時間戳記。

#### [NEW] [scraper_facebook.py](file:///c:/Users/yoche/Desktop/NYCU/lingyan/scraper_facebook.py)
使用 `Playwright` 進行 Facebook 貼文搜尋的模組。
- 使用公開搜尋頁面。
- 極度依賴 Facebook 目前的 DOM 結構。

### 核心應用程式

#### [NEW] [main.py](file:///c:/Users/yoche/Desktop/NYCU/lingyan/main.py)
工具的入口點。
- 處理用戶輸入的關鍵字、平台和日期範圍。
- 協調各個爬蟲模組。
- 將數據彙整成統一格式。

#### [NEW] [exporter.py](file:///c:/Users/yoche/Desktop/NYCU/lingyan/exporter.py)
使用 `pandas` 處理數據並輸出 CSV 或 Excel 文件。

---

## 待解決問題

1. **PTT 的特定看板**: 您是否有經常關注的 PTT 看板清單？（例如：Gossiping, Stock, HatePolitics）
2. **登入需求**: 某些平台（特別是 Facebook）在未登入時顯示的結果非常有限。您是否願意提供瀏覽器的 Session 或使用備用帳號？
3. **關鍵字策略**: 多個關鍵字的搜尋應該是「且 (AND)」還是「或 (OR)」？

## 驗證計畫

### 自動化測試
- 使用快取的 HTML 文件對 PTT 解析器進行單元測試。
- 在公開搜尋 URL 上執行 Playwright 測試，以驗證 DOM 選擇器。

### 手動驗證
- 在三個平台上針對熱門關鍵字（例如 "AIGC"）執行一次搜尋。
- 驗證匯出的 CSV 包含正確的欄位：`平台`、`時間`、`帳號`、`內容`、`類型 (貼文/留言)`。
