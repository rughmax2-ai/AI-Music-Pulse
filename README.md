# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-24

**59 posts** archived from 5 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Tell the human slop to step it up](https://www.reddit.com/r/SunoAI/comments/1v40vir/tell_the_human_slop_to_step_it_up/) | r/SunoAI | – | – |
| 2 | [5.0](https://www.reddit.com/r/SunoAI/comments/1v4ey8c/50/) | r/SunoAI | – | – |
| 3 | [Have you heard any amazing songs on Suno?](https://www.reddit.com/r/SunoAI/comments/1v486yg/have_you_heard_any_amazing_songs_on_suno/) | r/SunoAI | – | – |
| 4 | [Share you most soulful/human/emotional tracks. Heavy Hitters only.](https://www.reddit.com/r/SunoAI/comments/1v4krol/share_you_most_soulfulhumanemotional_tracks_heavy/) | r/SunoAI | – | – |
| 5 | [New AI song promotion post](https://www.reddit.com/r/SunoAI/comments/1v4uovj/new_ai_song_promotion_post/) | r/SunoAI | – | – |
| 6 | [wellp i did it](https://www.reddit.com/r/SunoAI/comments/1v4o9s1/wellp_i_did_it/) | r/SunoAI | – | – |
| 7 | [Anyone else depressed/grieving and turning their notes into Suno songs just to get through](https://www.reddit.com/r/SunoAI/comments/1v4x160/anyone_else_depressedgrieving_and_turning_their/) | r/SunoAI | – | – |
| 8 | [I vs Suno. I honestly didn't expect this outcome](https://www.reddit.com/r/SunoAI/comments/1v4r1vv/i_vs_suno_i_honestly_didnt_expect_this_outcome/) | r/SunoAI | – | – |
| 9 | [What has Suno Taught you about Your Songwriting style](https://www.reddit.com/r/SunoAI/comments/1v4f7bl/what_has_suno_taught_you_about_your_songwriting/) | r/SunoAI | – | – |
| 10 | [The Better My Prompt Engineering Got, The Fewer Songs I Wanted To Publish](https://www.reddit.com/r/SunoAI/comments/1v4381k/the_better_my_prompt_engineering_got_the_fewer/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-24.json`](data/daily/2026-07-24.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-24 02:32 UTC_
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
