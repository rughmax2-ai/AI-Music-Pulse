# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-08-02

**64 posts** archived from 4 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [FIRST EARNING FROM MY AI MUSIC AFTER 3 MONTHS & 74 SONGS RELEASED](https://www.reddit.com/r/SunoAI/comments/1vcrezv/first_earning_from_my_ai_music_after_3_months_74/) | r/SunoAI | – | – |
| 2 | [New AI song promotion post](https://www.reddit.com/r/SunoAI/comments/1vcr3nq/new_ai_song_promotion_post/) | r/SunoAI | – | – |
| 3 | [YOUR VOICE IS THE BEST PROMPT!!!](https://www.reddit.com/r/SunoAI/comments/1vcq1hv/your_voice_is_the_best_prompt/) | r/SunoAI | – | – |
| 4 | [Do you guys think suno is being nerfed?](https://www.reddit.com/r/SunoAI/comments/1vclhgj/do_you_guys_think_suno_is_being_nerfed/) | r/SunoAI | – | – |
| 5 | [August 2026 Song Feedback Megathread - Leave a review, get a review!](https://www.reddit.com/r/SunoAI/comments/1vcpnch/august_2026_song_feedback_megathread_leave_a/) | r/SunoAI | – | – |
| 6 | [I dream of changing pop music](https://www.reddit.com/r/SunoAI/comments/1vd3d8t/i_dream_of_changing_pop_music/) | r/SunoAI | – | – |
| 7 | [Between "Guaranteed Human" and 74 Songs in Three Months](https://www.reddit.com/r/SunoAI/comments/1vd56wk/between_guaranteed_human_and_74_songs_in_three/) | r/SunoAI | – | – |
| 8 | [Silly Question: Does SUNO have canned Sound FX like "Footsteps" or "Thunder" (etc.)](https://www.reddit.com/r/SunoAI/comments/1vcx59u/silly_question_does_suno_have_canned_sound_fx/) | r/SunoAI | – | – |
| 9 | [Suno constantly not listening.](https://www.reddit.com/r/SunoAI/comments/1vclk2c/suno_constantly_not_listening/) | r/SunoAI | – | – |
| 10 | [New to suno](https://www.reddit.com/r/SunoAI/comments/1vcirvv/new_to_suno/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-08-02.json`](data/daily/2026-08-02.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-08-02 08:43 UTC_
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
