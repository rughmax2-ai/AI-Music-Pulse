#!/usr/bin/env python3
"""
build_pages_summary.py - Build a running, truncated daily summary for GitHub Pages.

Inputs:
  data/daily/YYYY-MM-DD.json files produced by fetch_reddit.py

Outputs:
  data/running-summary.json  (full running summary for automation)
  docs/summary.json          (summary payload for static site use)
  docs/index.html            (static running summary page)
"""

import json
import re
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = REPO_ROOT / "data" / "daily"
DATA_OUT = REPO_ROOT / "data" / "running-summary.json"
DOCS_DIR = REPO_ROOT / "docs"
DOCS_SUMMARY_OUT = DOCS_DIR / "summary.json"
DOCS_INDEX_OUT = DOCS_DIR / "index.html"

MAX_HIGHLIGHTS_PER_DAY = 5
MAX_TITLE_LEN = 120
MAX_SNIPPET_LEN = 220
MAX_DAYS_ON_PAGE = 30


def truncate(text: str, max_len: int) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def clean_selftext(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text or "").strip()
    normalized = re.sub(
        r"\s*submitted by /u/[^[]+\[link\]\s*\[comments\]\s*$",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    return normalized


def post_rank_key(post: dict) -> tuple:
    score = post.get("score")
    comments = post.get("num_comments")
    has_score = isinstance(score, int)
    has_comments = isinstance(comments, int)
    clean_text_len = len(clean_selftext(post.get("selftext", "")))
    return (
        1 if has_score else 0,
        score if has_score else 0,
        comments if has_comments else 0,
        clean_text_len,
    )


def summarize_post(post: dict) -> dict:
    snippet_source = clean_selftext(post.get("selftext", ""))
    if not snippet_source:
        snippet_source = post.get("title", "")
    return {
        "title": truncate(post.get("title", "Untitled"), MAX_TITLE_LEN),
        "permalink": post.get("permalink"),
        "subreddit": post.get("subreddit"),
        "topic": post.get("topic"),
        "score": post.get("score"),
        "num_comments": post.get("num_comments"),
        "snippet": truncate(snippet_source, MAX_SNIPPET_LEN),
    }


def top_highlights(posts: list[dict]) -> list[dict]:
    ranked = sorted(posts, key=post_rank_key, reverse=True)
    seen: set[str] = set()
    picks: list[dict] = []
    for post in ranked:
        key = post.get("id") or post.get("permalink") or post.get("title", "")
        if key in seen:
            continue
        seen.add(key)
        picks.append(summarize_post(post))
        if len(picks) >= MAX_HIGHLIGHTS_PER_DAY:
            break
    return picks


def build_day_summary(archive: dict) -> dict:
    stats = archive.get("stats", {})
    posts = archive.get("posts", [])
    highlights = top_highlights(posts)
    posts_by_sub = stats.get("posts_by_subreddit", {})
    primary_subreddit = None
    if posts_by_sub:
        primary_subreddit = max(posts_by_sub.items(), key=lambda item: item[1])[0]
    return {
        "date": archive.get("date"),
        "total_posts": stats.get("total_posts", len(posts)),
        "total_score": stats.get("total_score", 0),
        "total_comments": stats.get("total_comments", 0),
        "subreddit_count": len(posts_by_sub),
        "primary_subreddit": primary_subreddit,
        "highlights": highlights,
    }


def load_archives() -> list[dict]:
    files = sorted(DAILY_DIR.glob("*.json"), reverse=True)
    archives: list[dict] = []
    for file_path in files:
        archives.append(json.loads(file_path.read_text(encoding="utf-8")))
    return archives


def build_running_summary(archives: list[dict]) -> dict:
    day_summaries = [build_day_summary(archive) for archive in archives]
    total_posts = sum(day.get("total_posts", 0) for day in day_summaries)
    total_score = sum(day.get("total_score", 0) for day in day_summaries)
    total_comments = sum(day.get("total_comments", 0) for day in day_summaries)
    last_7 = day_summaries[:7]
    latest_generated_at = archives[0].get("generated_at_utc")
    if not latest_generated_at:
        latest_generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "generated_at_utc": latest_generated_at,
        "stats": {
            "total_days": len(day_summaries),
            "total_posts": total_posts,
            "total_score": total_score,
            "total_comments": total_comments,
            "last_7_days_posts": sum(day.get("total_posts", 0) for day in last_7),
        },
        "days": day_summaries,
    }


def render_day_html(day: dict) -> str:
    details = (
        f"{day.get('total_posts', 0)} posts"
        f" · {day.get('subreddit_count', 0)} subreddits"
    )
    if day.get("primary_subreddit"):
        details += f" · top volume: r/{escape(day['primary_subreddit'])}"
    items = []
    for highlight in day.get("highlights", []):
        title = escape(highlight.get("title", "Untitled"))
        url = escape(highlight.get("permalink") or "#")
        subreddit = escape(highlight.get("subreddit") or "unknown")
        snippet = escape(highlight.get("snippet") or "")
        score = highlight.get("score")
        comments = highlight.get("num_comments")
        engagement = []
        if isinstance(score, int):
            engagement.append(f"score {score}")
        if isinstance(comments, int):
            engagement.append(f"comments {comments}")
        engagement_text = f" ({', '.join(engagement)})" if engagement else ""
        items.append(
            f"<li><a href=\"{url}\">{title}</a> "
            f"<span class=\"meta\">r/{subreddit}{engagement_text}</span>"
            f"<div class=\"snippet\">{snippet}</div></li>"
        )
    joined = "\n".join(items) if items else "<li>No highlights available.</li>"
    return (
        "<section class=\"day\">"
        f"<h2>{escape(day.get('date', 'unknown'))}</h2>"
        f"<p class=\"day-stats\">{details}</p>"
        f"<ul>{joined}</ul>"
        "</section>"
    )


def render_html(summary: dict) -> str:
    stats = summary["stats"]
    days = summary.get("days", [])[:MAX_DAYS_ON_PAGE]
    day_sections = "\n".join(render_day_html(day) for day in days)
    generated_value = summary.get("generated_at_utc")
    if generated_value:
        generated_at = generated_value.replace("T", " ").replace("+00:00", " UTC")
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Music Pulse - Running Summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .muted {{ color: #444; }}
    .overview {{ background: #f7f7f7; border: 1px solid #e4e4e4; border-radius: 8px; padding: 1rem; margin: 1.25rem 0 2rem; }}
    .overview ul {{ margin: 0.25rem 0 0 1.2rem; }}
    .day {{ border-top: 1px solid #e6e6e6; padding-top: 1.25rem; margin-top: 1.25rem; }}
    .day h2 {{ margin: 0 0 0.35rem; }}
    .day-stats {{ margin: 0 0 0.9rem; color: #444; }}
    .day ul {{ margin: 0 0 0 1.2rem; padding: 0; }}
    .day li {{ margin-bottom: 0.9rem; }}
    .meta {{ color: #555; font-size: 0.9rem; }}
    .snippet {{ margin-top: 0.2rem; color: #222; }}
  </style>
</head>
<body>
  <h1>AI Music Pulse - Running Summary</h1>
  <p class="muted">Daily highlights auto-generated from archived AI music discussions.</p>
  <div class="overview">
    <strong>Overview</strong>
    <ul>
      <li>Total archived days: {stats.get("total_days", 0)}</li>
      <li>Total archived posts: {stats.get("total_posts", 0)}</li>
      <li>Posts in last 7 days: {stats.get("last_7_days_posts", 0)}</li>
      <li>Total upvotes captured: {stats.get("total_score", 0)}</li>
      <li>Total comments captured: {stats.get("total_comments", 0)}</li>
    </ul>
  </div>
  {day_sections}
  <p class="muted">Last generated: {generated_at}</p>
</body>
</html>
"""


def main() -> int:
    archives = load_archives()
    if not archives:
        print("No daily archives found; cannot build running summary.", file=sys.stderr)
        return 1

    summary = build_running_summary(archives)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    DATA_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DOCS_SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DOCS_INDEX_OUT.write_text(render_html(summary), encoding="utf-8")

    print(f"Wrote {DATA_OUT.relative_to(REPO_ROOT)}")
    print(f"Wrote {DOCS_SUMMARY_OUT.relative_to(REPO_ROOT)}")
    print(f"Wrote {DOCS_INDEX_OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
