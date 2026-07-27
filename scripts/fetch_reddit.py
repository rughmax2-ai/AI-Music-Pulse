#!/usr/bin/env python3
"""
fetch_reddit.py — Daily Reddit fetcher for the AI Music Pulse knowledge repo.

Fetches top daily posts from a configured list of subreddits covering
Suno, Udio, and AI music in general. Primary transport is Reddit's public
JSON API; if that is blocked or rate-limited, it falls back to the Atom/RSS
feed for the same listing.

Outputs:
  data/daily/YYYY-MM-DD.json  — structured archive for the day
  data/index.json             — rolling index of all archived days

No external dependencies: uses only the Python standard library.
"""

import json
import re
import sys
import time
import html
import gzip
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"
SOURCES_FILE = REPO_ROOT / "sources.json"

USER_AGENT = (
    "ai-music-pulse/1.0 (daily AI music knowledge archive; "
    "github.com portfolio project)"
)

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}

MAX_SELFTEXT_CHARS = 2000
TRUNCATED_TITLE_CHARS = 120
SUMMARY_EXCERPT_CHARS = 280
HIGHLIGHTS_PER_DAY = 10


def http_get(url: str, retries: int = 3, backoff: float = 5.0) -> bytes:
    """GET a URL with retries and gzip support. Raises on final failure."""
    last_err = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Encoding": "gzip",
                "Accept": "application/json, application/atom+xml, */*",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return body
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            last_err = e
            status = getattr(e, "code", None)
            wait = backoff * attempt
            if status == 429:
                wait = max(wait, 30.0 * attempt)
            print(f"  [warn] attempt {attempt}/{retries} failed for {url}: {e}; "
                  f"retrying in {wait:.0f}s", file=sys.stderr)
            if attempt < retries:
                time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def looks_like_json(body: bytes) -> bool:
    stripped = body.lstrip()
    return stripped.startswith(b"{") or stripped.startswith(b"[")


def fetch_via_json(subreddit: str, limit: int) -> list[dict]:
    """Fetch top-of-day posts via Reddit's public JSON listing API."""
    url = (f"https://www.reddit.com/r/{subreddit}/top.json"
           f"?t=day&limit={limit}&raw_json=1")
    body = http_get(url)
    if not looks_like_json(body):
        raise RuntimeError("JSON endpoint returned non-JSON (likely blocked)")
    payload = json.loads(body)
    posts = []
    for child in payload.get("data", {}).get("children", []):
        d = child.get("data", {})
        posts.append({
            "id": d.get("id"),
            "title": d.get("title", "").strip(),
            "author": d.get("author"),
            "created_utc": datetime.fromtimestamp(
                d.get("created_utc", 0), tz=timezone.utc
            ).isoformat(),
            "score": d.get("score", 0),
            "upvote_ratio": d.get("upvote_ratio"),
            "num_comments": d.get("num_comments", 0),
            "permalink": f"https://www.reddit.com{d.get('permalink', '')}",
            "url": d.get("url"),
            "selftext": (d.get("selftext") or "")[:MAX_SELFTEXT_CHARS],
            "link_flair_text": d.get("link_flair_text"),
            "is_video": d.get("is_video", False),
            "over_18": d.get("over_18", False),
            "transport": "json",
        })
    return posts


def strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_len: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def clean_selftext(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    cleaned = re.sub(
        r"\s*submitted by /u/[^[]+\[link\]\s*\[comments\]\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


def compute_importance(post: dict, keywords: list[str]) -> int:
    score = post.get("score")
    comments = post.get("num_comments")
    upvote_ratio = post.get("upvote_ratio")
    title = (post.get("title") or "").lower()
    body = clean_selftext(post.get("selftext", "")).lower()

    total = 0.0
    if isinstance(score, int):
        total += min(score, 500) * 0.08
    if isinstance(comments, int):
        total += min(comments, 200) * 0.22
    if isinstance(upvote_ratio, (float, int)):
        total += float(upvote_ratio) * 25.0

    keyword_hits = 0
    for kw in keywords:
        if kw in title:
            keyword_hits += 2
        elif kw in body:
            keyword_hits += 1
    total += min(keyword_hits, 12) * 3.0

    if body:
        total += min(len(body), 1200) / 100.0

    return int(round(total))


def fetch_via_rss(subreddit: str, limit: int) -> list[dict]:
    """Fallback: fetch top-of-day posts via Reddit's Atom feed."""
    url = (f"https://www.reddit.com/r/{subreddit}/top/.rss"
           f"?t=day&limit={limit}")
    body = http_get(url)
    root = ET.fromstring(body)
    posts = []
    for entry in root.findall("a:entry", ATOM_NS):
        entry_id = (entry.findtext("a:id", "", ATOM_NS) or "")
        link_el = entry.find("a:link", ATOM_NS)
        author_el = entry.find("a:author/a:name", ATOM_NS)
        content = entry.findtext("a:content", "", ATOM_NS) or ""
        posts.append({
            "id": entry_id.replace("t3_", ""),
            "title": (entry.findtext("a:title", "", ATOM_NS) or "").strip(),
            "author": (author_el.text or "").replace("/u/", "") if author_el is not None else None,
            "created_utc": entry.findtext("a:published", None, ATOM_NS),
            "score": None,
            "upvote_ratio": None,
            "num_comments": None,
            "permalink": link_el.get("href") if link_el is not None else None,
            "url": link_el.get("href") if link_el is not None else None,
            "selftext": strip_html(content)[:MAX_SELFTEXT_CHARS],
            "link_flair_text": None,
            "is_video": False,
            "over_18": False,
            "transport": "rss",
        })
    return posts


def matches_keywords(post: dict, keywords: list[str]) -> bool:
    haystack = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
    return any(kw in haystack for kw in keywords)


def fetch_subreddit(cfg: dict, keywords: list[str], limit: int,
                    min_score: int) -> tuple[list[dict], str | None]:
    """Fetch one subreddit with JSON->RSS fallback. Returns (posts, error)."""
    name = cfg["name"]
    posts = []
    try:
        posts = fetch_via_json(name, limit)
        print(f"  [ok] r/{name}: {len(posts)} posts via JSON")
    except Exception as e:
        print(f"  [warn] r/{name} JSON failed ({e}); trying RSS", file=sys.stderr)
        try:
            posts = fetch_via_rss(name, limit)
            print(f"  [ok] r/{name}: {len(posts)} posts via RSS")
        except Exception as e2:
            print(f"  [error] r/{name} RSS also failed: {e2}", file=sys.stderr)
            return [], str(e2)

    for p in posts:
        p["subreddit"] = name
        p["topic"] = cfg.get("topic", "AI Music")

    # NSFW is never included in the archive.
    posts = [p for p in posts if not p.get("over_18")]

    if cfg.get("keyword_filter"):
        posts = [p for p in posts if matches_keywords(p, keywords)]

    if min_score:
        posts = [p for p in posts
                 if p.get("score") is None or p["score"] >= min_score]

    return posts, None


def build_stats(posts: list[dict]) -> dict:
    scored = [p for p in posts if isinstance(p.get("score"), int)]
    by_sub: dict[str, int] = {}
    for p in posts:
        by_sub[p["subreddit"]] = by_sub.get(p["subreddit"], 0) + 1
    return {
        "total_posts": len(posts),
        "posts_by_subreddit": dict(sorted(by_sub.items(),
                                          key=lambda kv: -kv[1])),
        "total_score": sum(p["score"] for p in scored),
        "total_comments": sum(p["num_comments"] for p in posts
                              if isinstance(p.get("num_comments"), int)),
        "top_post": max(scored, key=lambda p: p["score"])["permalink"]
        if scored else None,
        "top_post_by_importance": max(
            posts, key=lambda p: p.get("importance_score", 0)
        )["permalink"] if posts else None,
    }


def update_index(day_key: str, stats: dict) -> None:
    index_file = DATA_DIR / "index.json"
    index = {"description": "Rolling index of daily AI music archives",
             "days": {}}
    if index_file.exists():
        index = json.loads(index_file.read_text(encoding="utf-8"))
    index["days"][day_key] = {
        "file": f"daily/{day_key}.json",
        "total_posts": stats["total_posts"],
        "total_score": stats["total_score"],
        "total_comments": stats["total_comments"],
    }
    index["days"] = dict(sorted(index["days"].items(), reverse=True))
    index["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    index["day_count"] = len(index["days"])
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def build_highlights(posts: list[dict], limit: int) -> list[dict]:
    ranked = sorted(posts, key=lambda p: p.get("importance_score", 0), reverse=True)
    highlights: list[dict] = []
    seen: set[str] = set()
    for post in ranked:
        pid = post.get("id") or post.get("permalink")
        if pid in seen:
            continue
        seen.add(pid)
        highlights.append({
            "id": post.get("id"),
            "title": post.get("truncated_title", post.get("title", "")),
            "excerpt": post.get("summary_excerpt", ""),
            "subreddit": post.get("subreddit"),
            "topic": post.get("topic"),
            "permalink": post.get("permalink"),
            "importance_score": post.get("importance_score", 0),
            "score": post.get("score"),
            "num_comments": post.get("num_comments"),
            "transport": post.get("transport"),
        })
        if len(highlights) >= limit:
            break
    return highlights


def main() -> int:
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    keywords = [k.lower() for k in sources.get("keywords", [])]
    limit = sources.get("posts_per_subreddit", 25)
    min_score = sources.get("min_score", 0)
    excerpt_chars = int(sources.get("summary_excerpt_chars", SUMMARY_EXCERPT_CHARS))
    title_chars = int(sources.get("truncated_title_chars", TRUNCATED_TITLE_CHARS))
    highlights_per_day = int(sources.get("highlights_per_day", HIGHLIGHTS_PER_DAY))

    now = datetime.now(timezone.utc)
    day_key = now.strftime("%Y-%m-%d")
    print(f"Fetching AI music posts for {day_key} (UTC)")

    all_posts: list[dict] = []
    errors: dict[str, str] = {}
    for cfg in sources["subreddits"]:
        posts, err = fetch_subreddit(cfg, keywords, limit, min_score)
        all_posts.extend(posts)
        if err:
            errors[cfg["name"]] = err
        time.sleep(3)  # be polite between subreddits

    # De-duplicate by post id (crossposts can appear in multiple subs).
    seen: set[str] = set()
    deduped = []
    for p in sorted(all_posts, key=lambda p: -(p.get("score") or 0)):
        pid = p.get("id") or p.get("permalink")
        if pid and pid in seen:
            continue
        seen.add(pid)
        cleaned_body = clean_selftext(p.get("selftext", ""))
        p["summary_excerpt"] = truncate_text(cleaned_body or p.get("title", ""), excerpt_chars)
        p["truncated_title"] = truncate_text(p.get("title", ""), title_chars)
        p["importance_score"] = compute_importance(p, keywords)
        deduped.append(p)

    deduped.sort(key=lambda p: p.get("importance_score", 0), reverse=True)
    stats = build_stats(deduped)
    highlights = build_highlights(deduped, highlights_per_day)

    archive = {
        "schema_version": 1,
        "date": day_key,
        "generated_at_utc": now.isoformat(),
        "sources": {
            "platform": "reddit",
            "subreddits": [c["name"] for c in sources["subreddits"]],
            "listing": "top",
            "window": "day",
        },
        "stats": stats,
        "highlights": highlights,
        "errors": errors,
        "posts": deduped,
    }

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DAILY_DIR / f"{day_key}.json"
    out_file.write_text(json.dumps(archive, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"Wrote {out_file.relative_to(REPO_ROOT)} "
          f"({stats['total_posts']} posts)")

    update_index(day_key, stats)
    print("Updated data/index.json")

    if not deduped and errors:
        print("All sources failed; failing the run so it is visible.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
