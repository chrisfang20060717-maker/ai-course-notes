# AI 課程筆記站

一週一頁的生成式 AI 課程筆記。這個專案的重點不是「做出一個網頁」，而是建立一套 **AI 能持續接手的規則**：之後每週只要丟進講義，AI 就能依同一份 `AGENTS.md` 做出新的一頁。

- 網站：https://chrisfang20060717-maker.github.io/ai-course-notes/
- 規則：[`AGENTS.md`](AGENTS.md)（`CLAUDE.md` 以 `@AGENTS.md` 共用同一份）

## 專案結構

| 路徑 | 用途 |
|---|---|
| `AGENTS.md` | 專案目的、風格、頁面結構、命名與 AI 修改規則 |
| `CLAUDE.md` | 一行 `@AGENTS.md` |
| `index.html` | 首頁：週次目錄 |
| `glossary.html` | 詞彙表（各週共用） |
| `lessons/week-NN-*.html` | 每週筆記 |
| `templates/lesson-template.html` | 新週次的模板 |
| `assets/style.css` | 全站唯一樣式表 |
| `scripts/check.py` | 驗收腳本（完成的定義） |
| `.agents/workflows/add-lesson.md` | 新增一週筆記的 loop 規格 |
| `log.md` | 修改紀錄 |

## 新增一週

1. 把講義放進 `raw/`（已在 `.gitignore`，不會上傳）。
2. 在 Code Agent（Claude Code / Antigravity / Codex…）中說：`/add-lesson 第 11 週，講義在 raw/11.pdf`。
3. 執行 `python3 scripts/check.py`，全部 ✅ 後 commit、push。

## 本機預覽

```bash
python3 -m http.server 8000
# 打開 http://localhost:8000
```
