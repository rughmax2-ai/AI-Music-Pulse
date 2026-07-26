#!/usr/bin/env python3
"""
sync_to_supabase.py — Upserts a day's fetched Reddit posts into Supabase.

Run after fetch_reddit.py. Reads data/daily/YYYY-MM-DD.json (today's file
by default, or a date passed as argv[1]) and upserts each post into the
`documents` table as source_type='reddit_post', keyed on source_url via
the `uniq_reddit_post_url` partial unique index — safe to re-run.

Requires env vars:
  SUPABASE_URL               e.g. https://xocrwemfdxhuefdzolxv.supabase.co
  SUPABASE_SERVICE_ROLE_KEY  service_role secret (Settings -> API), never
                              the anon/publishable key — RLS is enabled on
                              this table and only service_role can write.

No external dependencies: uses only the Python standard library.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = REPO_ROOT / "data" / "daily"

SELFTEXT_LIMIT = 800  # keep documents rows lean; full 2000-char body stays in the local JSON archive


def load_day(day_key: str) -> dict:
    path = DAILY_DIR / f"{day_key}.json"
    if not path.exists():
        raise SystemExit(f"No archive for {day_key}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def to_row(post: dict, day_key: str) -> dict:
    return {
        "source_type": "reddit_post",
        "source_url": post.get("permalink"),
        "title": (post.get("title") or "")[:300],
        "raw_content": (post.get("selftext") or "")[:SELFTEXT_LIMIT],
        "metadata": {
            "reddit_id": post.get("id"),
            "subreddit": post.get("subreddit"),
            "topic": post.get("topic"),
            "score": post.get("score"),
            "num_comments": post.get("num_comments"),
            "author": post.get("author"),
            "created_utc": post.get("created_utc"),
            "fetch_date": day_key,
        },
    }


def upsert(rows: list[dict], supabase_url: str, service_role_key: str) -> None:
    url = f"{supabase_url}/rest/v1/documents?on_conflict=source_url"
    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            # merge-duplicates -> upsert against uniq_reddit_post_url;
            # ignore-duplicates would also work since we only insert, never update.
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase upsert failed ({e.code}): {e.read().decode(errors='replace')}")


def main() -> int:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set", file=sys.stderr)
        return 1

    day_key = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive = load_day(day_key)
    rows = [to_row(p, day_key) for p in archive["posts"] if p.get("permalink")]

    if not rows:
        print(f"No posts with permalinks for {day_key}; nothing to sync")
        return 0

    # PostgREST batch insert size is generous, but keep chunks modest to
    # avoid oversized requests as daily volume grows.
    CHUNK = 100
    for i in range(0, len(rows), CHUNK):
        upsert(rows[i:i + CHUNK], supabase_url, service_role_key)

    print(f"Synced {len(rows)} posts for {day_key} to Supabase")
    return 0


if __name__ == "__main__":
    sys.exit(main())
