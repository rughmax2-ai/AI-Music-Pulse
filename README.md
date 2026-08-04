# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-08-04

**59 posts** archived from 5 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Don't read this if you are somebody.](https://www.reddit.com/r/SunoAI/comments/1vekxsi/dont_read_this_if_you_are_somebody/) | r/SunoAI | – | – |
| 2 | [I’M TIRED (AND YOU SHOULD TOO)](https://www.reddit.com/r/SunoAI/comments/1vete2d/im_tired_and_you_should_too/) | r/SunoAI | – | – |
| 3 | [Your Best Song](https://www.reddit.com/r/SunoAI/comments/1vecyns/your_best_song/) | r/SunoAI | – | – |
| 4 | [Your Songs on Wax? We’re Exploring It!](https://www.reddit.com/r/SunoAI/comments/1veg1q0/your_songs_on_wax_were_exploring_it/) | r/SunoAI | – | – |
| 5 | [🎵 Round 2 – Let's Share Our Best AI Songs (and Actually Listen This Time)](https://www.reddit.com/r/SunoAI/comments/1ved9y3/round_2_lets_share_our_best_ai_songs_and_actually/) | r/SunoAI | – | – |
| 6 | [German court rules AI music firm Suno broke copyright rules](https://www.reddit.com/r/SunoAI/comments/1ve93lh/german_court_rules_ai_music_firm_suno_broke/) | r/SunoAI | – | – |
| 7 | [Spotify has 'deleted' 75 million AI songs... or not?](https://www.reddit.com/r/SunoAI/comments/1vepkf1/spotify_has_deleted_75_million_ai_songs_or_not/) | r/SunoAI | – | – |
| 8 | [Spotify analytics make no sense](https://www.reddit.com/r/SunoAI/comments/1vefaiy/spotify_analytics_make_no_sense/) | r/SunoAI | – | – |
| 9 | [How can I trust someone with 4200 songs on Suno?](https://www.reddit.com/r/SunoAI/comments/1vf1dxh/how_can_i_trust_someone_with_4200_songs_on_suno/) | r/SunoAI | – | – |
| 10 | [MiniMax H3 seems like it's a pretty promising for generating music videos locally](https://www.reddit.com/r/SunoAI/comments/1vexues/minimax_h3_seems_like_its_a_pretty_promising_for/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-08-04.json`](data/daily/2026-08-04.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-08-04 09:14 UTC_
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
