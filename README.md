# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-30

**57 posts** archived from 5 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Could AI Transparency Be More Specific?](https://www.reddit.com/r/SunoAI/comments/1vait26/could_ai_transparency_be_more_specific/) | r/SunoAI | – | – |
| 2 | [An idea i had to help artists at least on youtube](https://www.reddit.com/r/SunoAI/comments/1vajsku/an_idea_i_had_to_help_artists_at_least_on_youtube/) | r/SunoAI | – | – |
| 3 | [If AI music becomes harder to monetize on YouTube, what alternative ecosystem should we be](https://www.reddit.com/r/SunoAI/comments/1vai8ea/if_ai_music_becomes_harder_to_monetize_on_youtube/) | r/SunoAI | – | – |
| 4 | [Suno to Musiversal?](https://www.reddit.com/r/SunoAI/comments/1va1ndv/suno_to_musiversal/) | r/SunoAI | – | – |
| 5 | [Suno makes me verify I'm human](https://www.reddit.com/r/SunoAI/comments/1va17cr/suno_makes_me_verify_im_human/) | r/SunoAI | – | – |
| 6 | [Suno Down... I just hit create...](https://www.reddit.com/r/SunoAI/comments/1vagkxl/suno_down_i_just_hit_create/) | r/SunoAI | – | – |
| 7 | [I just created a whole website for my songs](https://www.reddit.com/r/SunoAI/comments/1vak6rb/i_just_created_a_whole_website_for_my_songs/) | r/SunoAI | – | – |
| 8 | [\[Eletronic-Pop\] Morning Light](https://www.reddit.com/r/SunoAI/comments/1vag1mv/eletronicpop_morning_light/) | r/SunoAI | – | – |
| 9 | [Having a weird quality issue...](https://www.reddit.com/r/SunoAI/comments/1vafuou/having_a_weird_quality_issue/) | r/SunoAI | – | – |
| 10 | [Any of yall making dungeon synth or black metal?](https://www.reddit.com/r/SunoAI/comments/1vabmp3/any_of_yall_making_dungeon_synth_or_black_metal/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-30.json`](data/daily/2026-07-30.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-30 12:20 UTC_
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
