#!/usr/bin/env python3
"""
AI 課程筆記站 — 驗收腳本（完成的定義）

用法：在專案根目錄執行
    python3 scripts/check.py

每一條檢查都對應 AGENTS.md 的一條規則。全部通過才算完成；
有任何 ❌ 時以非 0 狀態碼結束。只用 Python 標準函式庫，不需安裝任何套件。
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
LESSON_DIR = ROOT / "lessons"
LESSON_NAME = re.compile(r"^week-(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.html$")
TITLE_RE = re.compile(r"^第 (\d{2}) 週｜.+｜AI 課程筆記$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_SECTIONS = ["tldr", "roadmap", "concepts", "practice", "terms", "reflection", "source"]
TEXT_MIN, TEXT_MAX = 1500, 4500
AGENTS_MAX_CHARS = 12000

errors: list[str] = []
passes: list[str] = []


def check(ok: bool, msg: str) -> bool:
    (passes if ok else errors).append(msg)
    return ok


class Page(HTMLParser):
    """收集一頁裡檢查需要的資訊。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.sections: list[str] = []
        self.classes: list[str] = []
        self.inline_style = 0
        self.scripts = 0
        self.title = ""
        self.meta_desc = None
        self.stylesheets: list[str] = []
        self.body_attrs: dict = {}
        self.cards: list[tuple[str, str | None]] = []  # (data-week, 第一個連結)
        self.dt_ids: list[str] = []
        self.tables = 0
        self.tables_wrapped = 0
        self.main_text: list[str] = []
        self.week_badge = ""
        self._stack: list[tuple[str, set]] = []
        self._in_title = False
        self._in_main = 0
        self._in_badge = False
        self._card_open: list | None = None
        self._void = {"meta", "link", "br", "img", "hr", "input", "source"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        self.classes.extend(cls)
        if "id" in a:
            self.ids.append(a["id"])
        if "style" in a:
            self.inline_style += 1
        if tag == "script":
            self.scripts += 1
        if tag != "link":
            for key in ("href", "src"):
                if key in a:
                    self.links.append(a[key])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.stylesheets.append(a.get("href", ""))
            self.links.append(a.get("href", ""))
        if tag == "meta" and a.get("name") == "description":
            self.meta_desc = a.get("content", "")
        if tag == "title":
            self._in_title = True
        if tag == "body":
            self.body_attrs = a
        if tag == "main":
            self._in_main += 1
        if tag == "section" and "id" in a:
            self.sections.append(a["id"])
        if tag == "dt" and "id" in a:
            self.dt_ids.append(a["id"])
        if tag == "table":
            self.tables += 1
            if any("table-wrap" in c for _, c in self._stack):
                self.tables_wrapped += 1
        if "week-badge" in cls:
            self._in_badge = True
        if tag == "li" and "lesson-card" in cls:
            self._card_open = [a.get("data-week", ""), None]
            self.cards.append(tuple())  # 佔位，關閉時寫入
        if self._card_open is not None and tag == "a" and self._card_open[1] is None:
            self._card_open[1] = a.get("href")
        if tag not in self._void:
            self._stack.append((tag, cls))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "main":
            self._in_main -= 1
        if tag == "span":
            self._in_badge = False
        if tag == "li" and self._card_open is not None and self._stack and "lesson-card" in self._stack[-1][1]:
            self.cards[-1] = tuple(self._card_open)
            self._card_open = None
        # 彈出到對應的 tag
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_badge:
            self.week_badge += data
        if self._in_main > 0:
            self.main_text.append(data)


def parse(path: Path) -> Page:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


_cache: dict[Path, Page] = {}


def page(path: Path) -> Page:
    path = path.resolve()
    if path not in _cache:
        _cache[path] = parse(path)
    return _cache[path]


def check_links(path: Path, pg: Page) -> None:
    rel = path.relative_to(ROOT)
    bad = []
    for link in pg.links:
        if not link or link.startswith(("http://", "https://", "mailto:")):
            continue
        if link.startswith("/"):
            bad.append(f"{link}（不可用 / 開頭的絕對路徑）")
            continue
        parts = urlsplit(link)
        target = path if not parts.path else (path.parent / unquote(parts.path))
        if not target.exists():
            bad.append(f"{link}（檔案不存在）")
            continue
        if parts.fragment and target.suffix == ".html":
            if parts.fragment not in page(target).ids:
                bad.append(f"{link}（找不到錨點 #{parts.fragment}）")
    check(not bad, f"{rel}：所有內部連結都連得到" + ("" if not bad else " → " + "；".join(bad)))


def check_common(path: Path, pg: Page, prefix: str) -> None:
    rel = path.relative_to(ROOT)
    check(pg.inline_style == 0, f"{rel}：沒有 inline style")
    check(pg.scripts == 0, f"{rel}：沒有 <script>")
    check(pg.stylesheets == [f"{prefix}assets/style.css"], f"{rel}：只引用 {prefix}assets/style.css")
    check(bool(pg.meta_desc), f"{rel}：有 meta description")
    check("site-header" in pg.classes and "site-footer" in pg.classes and "site-nav" in pg.classes,
          f"{rel}：有共用外框（site-header / site-nav / site-footer）")
    for target in ("index.html", "glossary.html"):
        check(f"{prefix}{target}" in pg.links, f"{rel}：導覽列連到 {prefix}{target}")
    check(pg.tables == pg.tables_wrapped, f"{rel}：表格都包在 .table-wrap 裡（{pg.tables_wrapped}/{pg.tables}）")
    raw = path.read_text(encoding="utf-8")
    check("{{" not in raw, f"{rel}：沒有殘留的模板佔位符 {{{{...}}}}")
    check_links(path, pg)


def main() -> int:
    # ---- 規則檔 ----
    agents = ROOT / "AGENTS.md"
    if check(agents.exists(), "AGENTS.md 存在"):
        n = len(agents.read_text(encoding="utf-8"))
        check(n <= AGENTS_MAX_CHARS, f"AGENTS.md 長度 {n} 字元（上限 {AGENTS_MAX_CHARS}）")
    claude = ROOT / "CLAUDE.md"
    check(claude.exists() and claude.read_text(encoding="utf-8").strip() == "@AGENTS.md",
          "CLAUDE.md 只有一行 @AGENTS.md（只維護一份規則）")
    check((ROOT / "templates" / "lesson-template.html").exists(), "templates/lesson-template.html 存在")
    log = ROOT / "log.md"
    log_text = log.read_text(encoding="utf-8") if log.exists() else ""
    check(log.exists(), "log.md 存在")

    # ---- 週次頁 ----
    lessons = sorted(LESSON_DIR.glob("*.html"))
    check(len(lessons) > 0, f"lessons/ 至少有一頁（目前 {len(lessons)} 頁）")
    weeks_seen: dict[str, str] = {}
    for path in lessons:
        rel = path.relative_to(ROOT)
        m = LESSON_NAME.match(path.name)
        if not check(bool(m), f"{rel}：檔名符合 week-NN-短名.html"):
            continue
        nn = m.group(1)
        check(nn not in weeks_seen, f"{rel}：第 {nn} 週只有一個檔案")
        weeks_seen[nn] = path.name
        pg = page(path)
        check(pg.body_attrs.get("data-week") == nn, f"{rel}：<body data-week> 與檔名週次一致（{nn}）")
        tm = TITLE_RE.match(pg.title.strip())
        check(bool(tm) and tm.group(1) == nn, f"{rel}：<title> 格式為「第 {nn} 週｜標題｜AI 課程筆記」")
        check(pg.sections == REQUIRED_SECTIONS,
              f"{rel}：7 個區塊齊全且順序正確" + ("" if pg.sections == REQUIRED_SECTIONS else f" → 目前 {pg.sections}"))
        check(pg.week_badge.strip() == f"第 {nn} 週", f"{rel}：頁首週次標籤為「第 {nn} 週」")
        check("subtitle" in pg.classes and "tags" in pg.classes, f"{rel}：頁首有副標 .subtitle 與標籤 .tags")
        check("callout" in pg.classes and "key" in pg.classes, f"{rel}：一句話重點使用 .callout.key")
        check("flow" in pg.classes, f"{rel}：路線圖使用 .flow")
        check("chips" in pg.classes, f"{rel}：本週詞彙使用 .chips")
        glossary_links = [l for l in pg.links if l.startswith("../glossary.html#")]
        check(len(glossary_links) >= 1, f"{rel}：本週詞彙至少連到 1 個詞彙表條目（{len(glossary_links)} 個）")
        text_len = len(re.sub(r"\s+", "", "".join(pg.main_text)))
        check(TEXT_MIN <= text_len <= TEXT_MAX, f"{rel}：內文 {text_len} 字（規定 {TEXT_MIN}–{TEXT_MAX}）")
        check(path.name in log_text, f"{rel}：log.md 有這一頁的修改紀錄")
        check_common(path, pg, "../")

    # ---- 首頁 ----
    index = ROOT / "index.html"
    if check(index.exists(), "index.html 存在"):
        pg = page(index)
        check_common(index, pg, "")
        cards = [c for c in pg.cards if c]
        card_weeks = [c[0] for c in cards]
        check(card_weeks == sorted(card_weeks), f"index.html：週次卡片依週次由小到大排列 {card_weeks}")
        linked = {Path(c[1]).name: c[0] for c in cards if c[1]}
        for nn, name in sorted(weeks_seen.items()):
            check(linked.get(name) == nn, f"index.html：有第 {nn} 週卡片並連到 lessons/{name}")
        for name in linked:
            check(name in weeks_seen.values(), f"index.html：卡片 {name} 對應的頁面存在")

    # ---- 詞彙表 ----
    glossary = ROOT / "glossary.html"
    if check(glossary.exists(), "glossary.html 存在"):
        pg = page(glossary)
        check_common(glossary, pg, "")
        ids = pg.dt_ids
        check(len(ids) == len(set(ids)), "glossary.html：詞彙 id 沒有重複")
        check(all(KEBAB.match(i) for i in ids), "glossary.html：詞彙 id 都是英文小寫 kebab-case")
        check(ids == sorted(ids), "glossary.html：詞彙依 id 字母排序")
        check(pg.classes.count("seen-in") == len(ids), "glossary.html：每個詞彙都標出出現週次（.seen-in）")

    # ---- 報告 ----
    for msg in passes:
        print(f"✅ {msg}")
    for msg in errors:
        print(f"❌ {msg}")
    print(f"\n通過 {len(passes)} 項，失敗 {len(errors)} 項。")
    if errors:
        print("請只修上面列出的 ❌ 項目，修完再跑一次（最多 3 輪，見 AGENTS.md 第 7 節）。")
        return 1
    print("全部通過 🎉 記得更新 log.md 並 commit。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
