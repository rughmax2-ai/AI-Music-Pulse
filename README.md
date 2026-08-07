# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-08-07

**58 posts** archived from 4 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Let the witch hunt begin](https://www.reddit.com/r/SunoAI/comments/1vh4234/let_the_witch_hunt_begin/) | r/SunoAI | – | – |
| 2 | [Updates incoming 👀](https://www.reddit.com/r/SunoAI/comments/1vh2zbn/updates_incoming/) | r/SunoAI | – | – |
| 3 | [Info on the Suno Changes](https://www.reddit.com/r/SunoAI/comments/1vh9ahf/info_on_the_suno_changes/) | r/SunoAI | – | – |
| 4 | [“Your Lyrics Contain Copyrighted Material” for Oohhs and Ahhhs](https://www.reddit.com/r/SunoAI/comments/1vhbvmo/your_lyrics_contain_copyrighted_material_for/) | r/SunoAI | – | – |
| 5 | [Why does r/sunoai allow hateful trolls? Where is the moderation?](https://www.reddit.com/r/SunoAI/comments/1vh52sg/why_does_rsunoai_allow_hateful_trolls_where_is/) | r/SunoAI | – | – |
| 6 | [Questions about Suno’s new watermarks & fingerprints](https://www.reddit.com/r/SunoAI/comments/1vh5saa/questions_about_sunos_new_watermarks_fingerprints/) | r/SunoAI | – | – |
| 7 | [Allright Suno cats. Let’s hear your weird songs](https://www.reddit.com/r/SunoAI/comments/1vhdc27/allright_suno_cats_lets_hear_your_weird_songs/) | r/SunoAI | – | – |
| 8 | [No commercial rights?!?](https://www.reddit.com/r/SunoAI/comments/1vhltjq/no_commercial_rights/) | r/SunoAI | – | – |
| 9 | [2nd Request to Remix](https://www.reddit.com/r/SunoAI/comments/1vhixim/2nd_request_to_remix/) | r/SunoAI | – | – |
| 10 | [\[Trip-Hop\] Sleep Transit \| Winds of Urartu - "The Violet Commission"](https://www.reddit.com/r/SunoAI/comments/1vh7s13/triphop_sleep_transit_winds_of_urartu_the_violet/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-08-07.json`](data/daily/2026-08-07.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-08-07 07:47 UTC_
<!-- DIGEST:END -->

## How It Works

```
┌────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│ GitHub Actions │───▶│ fetch_reddit.py     │───▶│ data/daily/DATE.json │
│ cron (daily)   │    │ fetch_discord.py    │    │ data/index.json      │
└────────────────┘    │ (no-op w/o token)   │    └──────────┬───────────┘
                      └─────────────────────┘               │
                           ┌────────────────────────────────┤
                           ▼                                ▼
              ┌──────────────────────┐       ┌──────────────────────────┐
              │ update_readme.py     │       │ build_site.py            │
              │ digest ▸ README      │       │ static archive ▸ site/   │
              └──────────────────────┘       └──────────────────────────┘
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
python scripts/fetch_discord.py   # no-op without DISCORD_BOT_TOKEN
python scripts/update_readme.py   # refreshes the digest in this README
python scripts/build_site.py      # writes static pages under site/
```

## Experimental Prompt Research

The [`Hypothesis Engine`](hypothesis-engine/) turns observations about Suno v5/v5.5 prompt behavior into SHA-256-locked experiments, blinded render evidence, and human-approved RAG claims. It keeps anecdotes, preregistered effects, surviving mechanisms, contradictions, and retired model-version findings explicitly separated from the daily community-ingestion pipeline.

See [`hypothesis-engine/README.md`](hypothesis-engine/README.md).

## Roadmap

- [x] Discord server digests — scaffold wired (`fetch_discord.py` no-ops
      without `DISCORD_BOT_TOKEN`; see [`docs/DISCORD_ACTIVATION.md`](docs/DISCORD_ACTIVATION.md))
- [ ] Weekly trend rollups (top keywords, score deltas across days)
- [ ] Hacker News and YouTube sources
- [x] Static site rendering of the archive via GitHub Pages (`site/` +
      Pages workflow)
- [x] Hypothesis Engine Supabase migration (in-repo; apply on a
      branch/test project via `hypothesis-engine/scripts/apply_migrations.py`)
- [ ] First real existence test without claim promotion

## License

MIT — data archived here is public content fetched from Reddit's public
feeds and remains subject to Reddit's terms.
