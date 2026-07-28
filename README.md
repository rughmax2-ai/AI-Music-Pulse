# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-28

**62 posts** archived from 5 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Listener (pt. 3)](https://www.reddit.com/r/SunoAI/comments/1v8pzpw/listener_pt_3/) | r/SunoAI | – | – |
| 2 | [Avoid vocal intro and wordless vocal](https://www.reddit.com/r/SunoAI/comments/1v8az9p/avoid_vocal_intro_and_wordless_vocal/) | r/SunoAI | – | – |
| 3 | [Is 13,457 a lot ? Does anyone else upload their Freestyles Raps to Suno? I’d love to hear ](https://www.reddit.com/r/SunoAI/comments/1v8g1kn/is_13457_a_lot_does_anyone_else_upload_their/) | r/SunoAI | – | – |
| 4 | [Can AI music help us make sense of what is happening in the world?](https://www.reddit.com/r/SunoAI/comments/1v8tu7v/can_ai_music_help_us_make_sense_of_what_is/) | r/SunoAI | – | – |
| 5 | [Anyone create a Suno song then remade it as a human cover?](https://www.reddit.com/r/SunoAI/comments/1v8nqfq/anyone_create_a_suno_song_then_remade_it_as_a/) | r/SunoAI | – | – |
| 6 | [are ai musicians actually making money? i went through the ones that charted or got signed](https://www.reddit.com/r/SunoAI/comments/1v8ttlp/are_ai_musicians_actually_making_money_i_went/) | r/SunoAI | – | – |
| 7 | [\[Medieval/Nordic/Ambience\] The Blackthorn Wood - Dark Medieval Nordic Music & Winter For](https://www.reddit.com/r/SunoAI/comments/1v86ryc/medievalnordicambience_the_blackthorn_wood_dark/) | r/SunoAI | – | – |
| 8 | [Suno V5.5 is only for polish; 4.5 and 5 do the heavy lifting.](https://www.reddit.com/r/SunoAI/comments/1v8uyk6/suno_v55_is_only_for_polish_45_and_5_do_the_heavy/) | r/SunoAI | – | – |
| 9 | [I wish Suno had proper “Top Charts” for discovering genuinely great AI songs](https://www.reddit.com/r/SunoAI/comments/1v8thfa/i_wish_suno_had_proper_top_charts_for_discovering/) | r/SunoAI | – | – |
| 10 | [Suno v6 Feature Request](https://www.reddit.com/r/SunoAI/comments/1v8h5rq/suno_v6_feature_request/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-28.json`](data/daily/2026-07-28.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-28 12:33 UTC_
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
