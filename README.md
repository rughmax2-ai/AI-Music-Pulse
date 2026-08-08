# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-08-08

**66 posts** archived from 5 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [I think Reddit is infected with bots.](https://www.reddit.com/r/SunoAI/comments/1vi9dsj/i_think_reddit_is_infected_with_bots/) | r/SunoAI | – | – |
| 2 | [New update](https://www.reddit.com/r/SunoAI/comments/1vi0hdt/new_update/) | r/SunoAI | – | – |
| 3 | [Stop trying to find ways to try & circumvent Suno anti-fraud measures & encouraging others](https://www.reddit.com/r/SunoAI/comments/1vhyugk/stop_trying_to_find_ways_to_try_circumvent_suno/) | r/SunoAI | – | – |
| 4 | [Using "my voice" is hilarious](https://www.reddit.com/r/SunoAI/comments/1vi852x/using_my_voice_is_hilarious/) | r/SunoAI | – | – |
| 5 | [New AI song promotion post](https://www.reddit.com/r/SunoAI/comments/1vif9wq/new_ai_song_promotion_post/) | r/SunoAI | – | – |
| 6 | [Voices just landed on mobile 🎶🎤](https://www.reddit.com/r/SunoAI/comments/1vi22b2/voices_just_landed_on_mobile/) | r/SunoAI | – | – |
| 7 | [Spotify Playlists for Suno Artists Post #3](https://www.reddit.com/r/SunoAI/comments/1vhycnj/spotify_playlists_for_suno_artists_post_3/) | r/SunoAI | – | – |
| 8 | [Am I stupid? Or does Suno just SUCK at following prompts?](https://www.reddit.com/r/SunoAI/comments/1vi3g3v/am_i_stupid_or_does_suno_just_suck_at_following/) | r/SunoAI | – | – |
| 9 | [Just made my first Ai Music account w/ Suno Pro](https://www.reddit.com/r/SunoAI/comments/1vii4aj/just_made_my_first_ai_music_account_w_suno_pro/) | r/SunoAI | – | – |
| 10 | [Novelty or the way around music streaming services?](https://www.reddit.com/r/SunoAI/comments/1vifwf2/novelty_or_the_way_around_music_streaming_services/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-08-08.json`](data/daily/2026-08-08.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-08-08 07:21 UTC_
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
