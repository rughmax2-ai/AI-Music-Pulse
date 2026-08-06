#!/usr/bin/env python3
"""
build_site.py — Generate a static HTML archive from data/daily/*.json.

Outputs under site/:
  index.html           — day list + latest digest summary
  days/YYYY-MM-DD.html — per-day post tables
  styles.css           — shared styles

No external dependencies. Safe to run when Discord contributed nothing.
"""

from __future__ import annotations

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = REPO_ROOT / "data" / "daily"
INDEX_FILE = REPO_ROOT / "data" / "index.json"
SITE_DIR = REPO_ROOT / "site"
DAYS_DIR = SITE_DIR / "days"

TOP_N = 25


def esc(text) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def fmt_num(n) -> str:
    return f"{n:,}" if isinstance(n, int) else "–"


def load_days() -> list[dict]:
    files = sorted(DAILY_DIR.glob("*.json"), reverse=True)
    archives = []
    for path in files:
        try:
            archives.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  [warn] skip {path.name}: {exc}", file=sys.stderr)
    return archives


def page_shell(title: str, body: str, *, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html">AI Music Pulse</a>
    <p class="tagline">Daily archive of AI music community discussion</p>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <p>Generated from the JSON archive ·
       <a href="https://github.com/rughmax2-ai/AI-Music-Pulse">GitHub</a></p>
  </footer>
</body>
</html>
"""


def render_day_table(posts: list[dict], limit: int | None = None) -> str:
    rows = posts if limit is None else posts[:limit]
    if not rows:
        return "<p class=\"empty\">No posts archived for this day.</p>\n"
    lines = [
        '<table class="posts">',
        "<thead><tr>"
        "<th>#</th><th>Post</th><th>Source</th><th>Score</th><th>Comments</th>"
        "</tr></thead>",
        "<tbody>",
    ]
    for i, p in enumerate(rows, 1):
        title = esc((p.get("title") or "")[:120])
        permalink = esc(p.get("permalink") or p.get("url") or "#")
        platform = p.get("platform") or (
            f"r/{p['subreddit']}" if p.get("subreddit") else "reddit"
        )
        lines.append(
            "<tr>"
            f"<td>{i}</td>"
            f'<td><a href="{permalink}">{title}</a></td>'
            f"<td>{esc(platform)}</td>"
            f"<td>{esc(fmt_num(p.get('score')))}</td>"
            f"<td>{esc(fmt_num(p.get('num_comments')))}</td>"
            "</tr>"
        )
    lines += ["</tbody>", "</table>"]
    return "\n".join(lines) + "\n"


def write_day_page(archive: dict) -> None:
    day = archive["date"]
    stats = archive.get("stats") or {}
    posts = archive.get("posts") or []
    by_sub = stats.get("posts_by_subreddit") or {}
    summary = (
        f"<p><strong>{esc(fmt_num(stats.get('total_posts', len(posts))))} posts</strong>"
    )
    if by_sub:
        summary += f" from {len(by_sub)} subreddit(s)"
    if stats.get("total_score"):
        summary += (
            f" · {esc(fmt_num(stats['total_score']))} combined upvotes"
            f" · {esc(fmt_num(stats.get('total_comments')))} comments"
        )
    summary += "</p>"

    body = f"""    <nav class="crumb"><a href="../index.html">Archive</a> / {esc(day)}</nav>
    <h1>Digest — {esc(day)}</h1>
    {summary}
    {render_day_table(posts)}
    <p class="meta">Source JSON:
      <code>data/daily/{esc(day)}.json</code></p>
"""
    path = DAYS_DIR / f"{day}.html"
    path.write_text(page_shell(f"AI Music Pulse — {day}", body, depth=1),
                    encoding="utf-8")


def write_index(archives: list[dict]) -> None:
    latest = archives[0] if archives else None
    parts = ['    <h1>Archive</h1>\n']
    if latest:
        parts.append(
            f'    <section class="latest">\n'
            f'      <h2>Latest — {esc(latest["date"])}</h2>\n'
            f'      <p><a href="days/{esc(latest["date"])}.html">Open full day</a></p>\n'
            f'      {render_day_table(latest.get("posts") or [], TOP_N)}'
            f'    </section>\n'
        )
    parts.append('    <section class="day-list">\n      <h2>All days</h2>\n      <ul>\n')
    for archive in archives:
        day = archive["date"]
        stats = archive.get("stats") or {}
        n = stats.get("total_posts", len(archive.get("posts") or []))
        parts.append(
            f'        <li><a href="days/{esc(day)}.html">{esc(day)}</a>'
            f' — {esc(fmt_num(n))} posts</li>\n'
        )
    parts.append('      </ul>\n    </section>\n')
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts.append(f'    <p class="meta">Built {esc(generated)}</p>\n')
    (SITE_DIR / "index.html").write_text(
        page_shell("AI Music Pulse — Archive", "".join(parts)),
        encoding="utf-8",
    )


def write_css() -> None:
    css = """:root {
  --bg: #0f1419;
  --surface: #1a222c;
  --text: #e7ecf1;
  --muted: #9aa7b5;
  --accent: #3d9a7a;
  --line: #2a3542;
  --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --font-body: "Segoe UI", "Helvetica Neue", sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--font-body);
  color: var(--text);
  background:
    radial-gradient(1200px 600px at 10% -10%, #1c3a32 0%, transparent 55%),
    radial-gradient(900px 500px at 100% 0%, #243044 0%, transparent 50%),
    var(--bg);
  line-height: 1.5;
}
.site-header, main, .site-footer {
  width: min(960px, calc(100% - 2rem));
  margin-inline: auto;
}
.site-header { padding: 2.5rem 0 1rem; }
.brand {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  color: var(--text);
  text-decoration: none;
  letter-spacing: -0.02em;
}
.tagline { color: var(--muted); margin: 0.35rem 0 0; }
main { padding-bottom: 3rem; }
h1, h2 { font-family: var(--font-display); font-weight: 600; }
.crumb { color: var(--muted); margin-bottom: 0.75rem; }
.crumb a { color: var(--accent); }
.posts {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0 1.5rem;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
}
.posts th, .posts td {
  text-align: left;
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}
.posts th { color: var(--muted); font-weight: 600; font-size: 0.85rem; }
.posts a { color: var(--text); text-decoration: none; }
.posts a:hover { color: var(--accent); text-decoration: underline; }
.day-list ul { padding-left: 1.1rem; }
.day-list a { color: var(--accent); }
.meta, .empty { color: var(--muted); font-size: 0.9rem; }
.site-footer {
  padding: 1rem 0 2.5rem;
  color: var(--muted);
  border-top: 1px solid var(--line);
}
.site-footer a { color: var(--accent); }
@media (max-width: 640px) {
  .posts th:nth-child(4), .posts td:nth-child(4),
  .posts th:nth-child(5), .posts td:nth-child(5) { display: none; }
}
"""
    (SITE_DIR / "styles.css").write_text(css, encoding="utf-8")


def main() -> int:
    archives = load_days()
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    DAYS_DIR.mkdir(parents=True, exist_ok=True)
    write_css()
    for archive in archives:
        write_day_page(archive)
    write_index(archives)
    print(f"Built site/ with {len(archives)} day page(s)")
    if INDEX_FILE.exists():
        print(f"Index source: {INDEX_FILE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
