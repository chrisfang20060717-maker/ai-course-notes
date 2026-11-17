# AGENTS.md — AI 課程筆記站

> 給 AI 代理（Claude Code、Codex、Antigravity、OpenCode…）看的專案手冊。
> 開始任何修改前先讀完這份文件；新增一週筆記時，照著 `.agents/workflows/add-lesson.md` 的流程做。

## 1. 專案目的

- 把「生成式 AI 課程」每一週的上課內容，整理成**一週一頁**的靜態網頁筆記。
- 讀者：我自己（期末複習）＋同學（快速看懂某一週在講什麼）。
- 成品要能直接用 GitHub Pages 瀏覽，**不需要任何建置步驟**（純 HTML + CSS）。
- 目標是「之後每週只要丟進新的講義，AI 就能照同一套規則做出新的一頁」，而不是每次重新設計。

## 2. 資料夾結構（不要新增其他頂層資料夾）

```
ai-course-notes/
├── AGENTS.md              ← 本文件（唯一的規則來源）
├── CLAUDE.md              ← 只有一行 @AGENTS.md，不要在裡面另寫規則
├── README.md              ← 給人看的專案介紹
├── log.md                 ← 修改紀錄，每次改動都要追加一筆
├── index.html             ← 首頁：課程週次目錄
├── glossary.html          ← 詞彙表：所有週次共用
├── lessons/               ← 每週一頁筆記
│   └── week-10-workflow-design.html
├── templates/
│   └── lesson-template.html   ← 新增一週時「複製這份」開始
├── assets/
│   └── style.css          ← 全站唯一的樣式表
├── scripts/
│   └── check.py           ← 驗收腳本（完成的定義）
├── .agents/workflows/
│   └── add-lesson.md      ← 新增一週的 loop 規格
└── raw/                   ← （可選）原始講義，不進 git，見 .gitignore
```

## 3. 檔名與放置規則

| 類型 | 位置 | 命名規則 | 範例 |
|---|---|---|---|
| 週次筆記 | `lessons/` | `week-NN-英文小寫短名.html`，NN 一定兩位數 | `week-10-workflow-design.html` |
| 詞彙 | `glossary.html` 內的 `<dt id="...">` | 英文小寫 kebab-case | `loop-engineering` |
| 圖片 | `assets/img/week-NN/` | 英文小寫 kebab-case | `assets/img/week-10/graph-flow.png` |

- 一週只能有一個檔案；同一週補充內容就改原檔，不要開 `week-10-2.html`。
- 所有連結都用**相對路徑**（`../assets/style.css`），不要用 `/` 開頭，否則 GitHub Pages 子路徑會壞掉。

## 4. 視覺風格

- 調性：像一本乾淨的紙本筆記本——米白紙張底色、深墨色文字、只有一個強調色（深青綠）＋螢光筆黃色標重點。
- 字體：標題用襯線（宋體/明體），內文用無襯線（蘋方/思源黑體），程式碼用等寬字。都已寫在 `style.css`，**不要引入外部字型或 CSS 框架**。
- 顏色只能用 `style.css` 最上方 `:root` 定義的變數；不要在 HTML 裡寫 `style="..."`，也不要新增顏色。
- 手機優先：內容欄寬最多 760px；表格外面一律包 `<div class="table-wrap">` 讓它在手機上可以橫向捲動。
- 語言：正體中文（台灣用語），專有名詞第一次出現時保留英文，例如「迴圈（Loop）」。中英文之間加半形空格。

## 5. 頁面結構

### 5.1 每一頁共用的外框

每頁都必須有：
1. `<header class="site-header">`：左邊站名連回首頁，右邊導覽列 `首頁 / 詞彙表`。
2. `<main>`：頁面內容。
3. `<footer class="site-footer">`：寫「依 AGENTS.md 規則產生」＋ GitHub 連結。

外框直接從 `templates/lesson-template.html` 複製，不要自己重寫。

### 5.2 週次筆記頁（`lessons/*.html`）—— 固定 7 個區塊，順序不可變

| 順序 | `<section id>` | 標題 | 內容要求 |
|---|---|---|---|
| 1 | `tldr` | 一句話重點 | 1 個 `.callout.key`，1–2 句，講這週最重要的結論 |
| 2 | `roadmap` | 本週路線圖 | 用 `.flow` 元件列出上課流程，3–7 個節點 |
| 3 | `concepts` | 核心觀念 | 每個觀念一個 `<h3>`，至少 3 個；比較型內容用表格 |
| 4 | `practice` | 實作紀錄 | 課堂實作的步驟（`ol.steps`）、用到的 prompt（`pre`） |
| 5 | `terms` | 本週詞彙 | 連到 `../glossary.html#詞彙id` 的 `.chips` 清單 |
| 6 | `reflection` | 我的反思 | 2–4 點，第一人稱，寫「我會怎麼用」，不要重複上面的內容 |
| 7 | `source` | 來源 | 講義名稱、週次、學期；有網址就附上 |

頁首（`.lesson-hero`）必須包含：週次標籤 `第 NN 週`、標題 `<h1>`、副標 `.subtitle`、標籤 `.tags`。

`<body>` 要有 `data-week="NN"`，數字要和檔名一致。

`<title>` 格式：`第 NN 週｜標題｜AI 課程筆記`（全形直線 `｜`）。

### 5.3 可以使用的元件（只用這些，不要自己發明新的 class）

| 元件 | 寫法 | 用途 |
|---|---|---|
| 重點框 | `<div class="callout key">` / `tip` / `warn` | key=結論、tip=小技巧、warn=常見錯誤 |
| 流程 | `<ol class="flow"><li>…</li></ol>` | 路線圖、pipeline |
| 步驟 | `<ol class="steps"><li><strong>步驟名</strong>說明</li></ol>` | 實作步驟 |
| 比較表 | `<div class="table-wrap"><table class="compare">…</table></div>` | A vs B 對照 |
| 卡片格 | `<div class="card-grid"><div class="card">…</div></div>` | 3–5 個並列概念 |
| 詞彙標籤 | `<ul class="chips"><li><a href="../glossary.html#id">詞</a></li></ul>` | 本週詞彙 |
| 螢光筆 | `<mark>` | 一段最多一處 |

### 5.4 首頁（`index.html`）

- `ol.lesson-list` 裡每週一個 `<li class="lesson-card" data-week="NN">`，**依週次由小到大排列**。
- 每張卡片：週次、標題（連到該頁）、一句話摘要（跟該頁 `tldr` 意思一致，30 字內）、2–4 個標籤。
- 只列已經存在的頁面，不要放「即將推出」的假卡片。

### 5.5 詞彙表（`glossary.html`）

- 使用 `<dl class="glossary">`；每個詞一組 `<dt id="kebab-id">中文（English）</dt><dd>…</dd>`。
- `<dd>` 1–3 句白話解釋，最後用 `<span class="seen-in">` 標出現在哪幾週並連回該頁。
- 依英文 id 字母排序。新增週次時，新詞加進來，舊詞若在新的週次又出現就補上週次連結。

## 6. 內容規則（AI 撰寫時必須遵守）

1. **只根據來源寫**：內容必須來自該週講義或我提供的筆記。講義沒有的東西不要自己補「延伸知識」；真的需要補充時放進 `.callout.tip` 並標明「補充」。
2. **用自己的話整理**，不要整段照抄講義；講義裡的金句可以引用，但一段最多一句。
3. 數字、人名、年份要和講義一致；看不清楚的地方寫 `【待確認】`，不要猜。
4. 每一頁內文 1,500–4,500 字之間；太長就拆成更多 `<h3>`，不要拆成兩個檔案。
5. `reflection` 區塊是我的意見，AI 只能寫草稿，並在 `log.md` 註明「反思為草稿，待本人修改」。

## 7. AI 修改時的工作規則

- **改之前**：先讀 `AGENTS.md`、`log.md` 最後 5 筆、要修改的檔案。
- **只動需要動的檔案**。不要順手重排別的頁面、不要改 `style.css` 的既有規則（只能在最下方追加，並在 log 說明原因）。
- **不要刪除**任何週次頁面；要下架就從首頁移除卡片並在 log 註明。
- **改完之後一定要跑驗收**：
  ```bash
  python3 scripts/check.py
  ```
  全部 ✅ 才算完成；有 ❌ 就修到過為止，最多修 3 輪，3 輪還過不了就停下來，把錯誤訊息回報給我，不要硬改規則或改腳本讓它通過。
- **在 `log.md` 最上方追加一筆**：日期、改了哪些檔、為什麼。
- **git**：一個邏輯變更一個 commit，訊息格式 `類型: 說明`，類型用 `add`（新增頁）、`fix`（修錯）、`style`（樣式）、`docs`（規則/說明）。例：`add: 第 11 週筆記`。

## 8. 完成的定義（Definition of Done）

一個新週次算完成，必須同時滿足：

- [ ] `lessons/week-NN-*.html` 存在，7 個區塊齊全且順序正確
- [ ] 首頁有對應卡片且週次排序正確
- [ ] 本週詞彙全部連得到 `glossary.html` 裡的 id
- [ ] `python3 scripts/check.py` 全部通過
- [ ] `log.md` 有新紀錄
- [ ] 已 commit

## 9. 不要做的事

- 不要引入 npm、框架、建置工具、外部 CDN、追蹤碼。
- 不要在 HTML 寫 inline style 或 inline script。
- 不要把 `raw/` 裡的原始講義 PDF 或任何個資上傳到 GitHub。
- 不要修改 `scripts/check.py` 來讓檢查通過；規則真的要改，先改 `AGENTS.md`，再改腳本，並在 log 說明。
