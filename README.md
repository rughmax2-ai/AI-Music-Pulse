# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-29

**62 posts** archived from 4 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [My content generated a combined total of $10,800 in June. AMA](https://www.reddit.com/r/SunoAI/comments/1v992ge/my_content_generated_a_combined_total_of_10800_in/) | r/SunoAI | – | – |
| 2 | [Voices feature not available for 4.5+ anymore ?!](https://www.reddit.com/r/SunoAI/comments/1v9lbx4/voices_feature_not_available_for_45_anymore/) | r/SunoAI | – | – |
| 3 | [New AI song promotion post](https://www.reddit.com/r/SunoAI/comments/1v9hrfe/new_ai_song_promotion_post/) | r/SunoAI | – | – |
| 4 | [Frustrated sometimes](https://www.reddit.com/r/SunoAI/comments/1v9gifs/frustrated_sometimes/) | r/SunoAI | – | – |
| 5 | [What are the things you try to do, but Suno never gets right?](https://www.reddit.com/r/SunoAI/comments/1v9bqba/what_are_the_things_you_try_to_do_but_suno_never/) | r/SunoAI | – | – |
| 6 | [🎵 Let's Share our best AI Songs, and actually listen to each other](https://www.reddit.com/r/SunoAI/comments/1v9prqj/lets_share_our_best_ai_songs_and_actually_listen/) | r/SunoAI | – | – |
| 7 | [We started an AI-assisted post-hardcore project from nothing and reached 4,500 monthly lis](https://www.reddit.com/r/SunoAI/comments/1v9r8jv/we_started_an_aiassisted_posthardcore_project/) | r/SunoAI | – | – |
| 8 | [I'm a bassist, but piano seeds steer Suno better than anything I do with prompts — 10 trac](https://www.reddit.com/r/SunoAI/comments/1v9c132/im_a_bassist_but_piano_seeds_steer_suno_better/) | r/SunoAI | – | – |
| 9 | [All the things that go unsaid](https://www.reddit.com/r/SunoAI/comments/1v91ngt/all_the_things_that_go_unsaid/) | r/SunoAI | – | – |
| 10 | [\[Cinematic Breakbeat\] The Unfinished Duel](https://www.reddit.com/r/SunoAI/comments/1v900ox/cinematic_breakbeat_the_unfinished_duel/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-29.json`](data/daily/2026-07-29.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-29 13:17 UTC_
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

## Experimental Prompt Research

The [`Hypothesis Engine`](hypothesis-engine/) turns observations about Suno v5/v5.5 prompt behavior into SHA-256-locked experiments, blinded render evidence, and human-approved RAG claims. It keeps anecdotes, preregistered effects, surviving mechanisms, contradictions, and retired model-version findings explicitly separated from the daily community-ingestion pipeline.

See [`hypothesis-engine/README.md`](hypothesis-engine/README.md).

## Roadmap

- [ ] Discord server digests (requires a bot token; planned as a second
      fetcher module writing to the same schema)
- [ ] Weekly trend rollups (top keywords, score deltas across days)
- [ ] Hacker News and YouTube sources
- [ ] Static site rendering of the archive via GitHub Pages
- [ ] Apply Hypothesis Engine Supabase migration (branch/test project first)
- [ ] First real existence test without claim promotion

## License

MIT — data archived here is public content fetched from Reddit's public
feeds and remains subject to Reddit's terms.
