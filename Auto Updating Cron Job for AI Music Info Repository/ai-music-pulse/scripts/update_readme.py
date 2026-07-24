#!/usr/bin/env python3
"""
update_readme.py — Renders the latest daily archive into README.md.

The README contains two marker comments:
  <!-- DIGEST:START --> ... <!-- DIGEST:END -->
Everything between the markers is replaced with the latest digest.
Static content outside the markers is preserved, so the project
description can be edited freely without breaking automation.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"
README = REPO_ROOT / "README.md"

START = "<!-- DIGEST:START -->"
END = "<!-- DIGEST:END -->"

TOP_N = 10


def latest_archive() -> dict | None:
    files = sorted(DAILY_DIR.glob("*.json"), reverse=True)
    if not files:
        return None
    return json.loads(files[0].read_text(encoding="utf-8"))


def md_escape(text: str) -> str:
    return re.sub(r"([\\|\[\]`*_])", r"\\\1", text or "")


def fmt_num(n) -> str:
    return f"{n:,}" if isinstance(n, int) else "–"


def render_digest(archive: dict) -> str:
    stats = archive["stats"]
    posts = archive["posts"][:TOP_N]

    summary = (f"**{fmt_num(stats['total_posts'])} posts** archived from "
               f"{len(stats['posts_by_subreddit'])} subreddits")
    # RSS fallback has no vote data; only show engagement when we have it.
    if stats.get("total_score"):
        summary += (f" · **{fmt_num(stats['total_score'])} combined upvotes** "
                    f"· **{fmt_num(stats['total_comments'])} comments**")

    lines = [
        "",
        f"### Daily Digest — {archive['date']}",
        "",
        summary,
        "",
        "| # | Post | Subreddit | Score | Comments |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, p in enumerate(posts, 1):
        title = md_escape(p["title"])[:90]
        lines.append(
            f"| {i} | [{title}]({p['permalink']}) "
            f"| r/{p['subreddit']} | {fmt_num(p.get('score'))} "
            f"| {fmt_num(p.get('num_comments'))} |"
        )

    lines += [
        "",
        f"Full structured data: [`data/daily/{archive['date']}.json`]"
        f"(data/daily/{archive['date']}.json) · "
        "Archive index: [`data/index.json`](data/index.json)",
        "",
        f"_Last updated: "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    archive = latest_archive()
    if archive is None:
        print("No daily archives found; leaving README unchanged.")
        return 0

    content = README.read_text(encoding="utf-8")
    if START not in content or END not in content:
        print("README markers missing; aborting to avoid clobbering README.",
              file=sys.stderr)
        return 1

    digest = render_digest(archive)
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END),
                         re.DOTALL)
    content = pattern.sub(START + "\n" + digest + END, content)
    README.write_text(content, encoding="utf-8")
    print(f"README updated with digest for {archive['date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
