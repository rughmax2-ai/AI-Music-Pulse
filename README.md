# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-27

**63 posts** archived from 4 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [This is how AI music wins](https://www.reddit.com/r/SunoAI/comments/1v7fux9/this_is_how_ai_music_wins/) | r/SunoAI | – | – |
| 2 | [Wrote an article going a little in depth what's going on when you hit the generate button.](https://www.reddit.com/r/SunoAI/comments/1v7i9mv/wrote_an_article_going_a_little_in_depth_whats/) | r/SunoAI | – | – |
| 3 | [New AI song promotion post](https://www.reddit.com/r/SunoAI/comments/1v7oy8z/new_ai_song_promotion_post/) | r/SunoAI | – | – |
| 4 | [I decided to wait a few years before distributing my music](https://www.reddit.com/r/SunoAI/comments/1v7d9cz/i_decided_to_wait_a_few_years_before_distributing/) | r/SunoAI | – | – |
| 5 | [Why So Much Hate Towards AI Music?](https://www.reddit.com/r/SunoAI/comments/1v7nkyf/why_so_much_hate_towards_ai_music/) | r/SunoAI | – | – |
| 6 | [Unsolicited tip: Want to take tracks to the next level write your lyrics. Ai is shit at wr](https://www.reddit.com/r/SunoAI/comments/1v7ppk5/unsolicited_tip_want_to_take_tracks_to_the_next/) | r/SunoAI | – | – |
| 7 | [Suddenly got banned for the Sino Discord](https://www.reddit.com/r/SunoAI/comments/1v7h3ng/suddenly_got_banned_for_the_sino_discord/) | r/SunoAI | – | – |
| 8 | [\[Warm Melancholic Indietronica\] Black Cat White Cat](https://www.reddit.com/r/SunoAI/comments/1v7gye5/warm_melancholic_indietronica_black_cat_white_cat/) | r/SunoAI | – | – |
| 9 | [Hi community. What styles do you write in, and which ones are your favorites—the ones that](https://www.reddit.com/r/SunoAI/comments/1v7y198/hi_community_what_styles_do_you_write_in_and/) | r/SunoAI | – | – |
| 10 | [Copyrighted material from 1529](https://www.reddit.com/r/SunoAI/comments/1v7mekj/copyrighted_material_from_1529/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-27.json`](data/daily/2026-07-27.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-27 16:03 UTC_
<!-- DIGEST:END -->

## How It Works

```
┌────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│ GitHub Actions │───▶│ fetch_reddit.py     │───▶│ data/daily/DATE.json │
│ cron (daily)   │    │ JSON API + RSS      │    │ data/index.json      │
└────────────────┘    │ fallback, dedupe,   │    └──────────┬───────────┘
                      │ keyword filtering   │               │
                      └─────────────────────┘               ▼
                                            ┌──────────────────────────┐
                                            │ update_readme.py         │
                                            │ renders digest ▸ README  │
                                            │ then auto-commits        │
                                            └──────────────────────────┘
```

1. **Fetch** — `scripts/fetch_reddit.py` pulls the top posts of the day
   from each subreddit in `sources.json` using Reddit's public JSON
   listing API, with an automatic fallback to Atom/RSS feeds if the API
   is rate-limited. General AI subreddits are filtered by music-related
   keywords so only relevant posts are archived.
2. **Archive** — Each day is stored as `data/daily/YYYY-MM-DD.json` with
   full post metadata (title, author, score, comments, flair, permalink,
   body excerpt). A rolling `data/index.json` tracks every archived day.
3. **Digest** — `scripts/update_readme.py` renders the latest day's top
   posts into the digest section above, between HTML comment markers, so
   the rest of this README is never touched by automation.
4. **Commit** — The workflow commits and pushes only when something
   actually changed.

## Data Schema

Each daily archive (`data/daily/YYYY-MM-DD.json`) looks like:

```json
{
  "schema_version": 1,
  "date": "2026-07-23",
  "generated_at_utc": "2026-07-23T06:15:04+00:00",
  "sources": {
    "platform": "reddit",
    "subreddits": ["SunoAI", "aimusic", "udiomusic"],
    "listing": "top",
    "window": "day"
  },
  "stats": {
    "total_posts": 87,
    "posts_by_subreddit": {"SunoAI": 42, "udiomusic": 25},
    "total_score": 3120,
    "total_comments": 954,
    "top_post": "https://www.reddit.com/r/SunoAI/comments/..."
  },
  "errors": {},
  "posts": [
    {
      "id": "1v40vir",
      "title": "…",
      "author": "…",
      "created_utc": "2026-07-23T02:27:00+00:00",
      "score": 251,
      "upvote_ratio": 0.93,
      "num_comments": 118,
      "permalink": "https://www.reddit.com/r/SunoAI/comments/…",
      "url": "…",
      "selftext": "first 2000 chars of the post body",
      "link_flair_text": "Discussion",
      "subreddit": "SunoAI",
      "topic": "Suno",
      "transport": "json"
    }
  ]
}
```

## Configuration

All sources live in [`sources.json`](sources.json):

| Field | Purpose |
| --- | --- |
| `subreddits[].name` | Subreddit to fetch (top posts of the day) |
| `subreddits[].topic` | Label attached to each archived post |
| `subreddits[].keyword_filter` | If `true`, only keep posts matching `keywords` (used for general AI subs) |
| `keywords` | Case-insensitive keyword list for filtering |
| `posts_per_subreddit` | Max posts fetched per subreddit |
| `min_score` | Minimum upvote score to be archived |

Add a subreddit by appending one line to `sources.json` — no code
changes needed.

## Running Locally

Requires Python 3.10+ and nothing else (standard library only):

```bash
python scripts/fetch_reddit.py    # writes data/daily/YYYY-MM-DD.json
python scripts/update_readme.py   # refreshes the digest in this README
```

## Roadmap

- [ ] Discord server digests (requires a bot token; planned as a second
      fetcher module writing to the same schema)
- [ ] Weekly trend rollups (top keywords, score deltas across days)
- [ ] Hacker News and YouTube sources
- [ ] Static site rendering of the archive via GitHub Pages

## License

MIT — data archived here is public content fetched from Reddit's public
feeds and remains subject to Reddit's terms.
