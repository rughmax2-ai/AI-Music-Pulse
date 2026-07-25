# AI Music Pulse

An auto-updating knowledge archive of the AI music scene. Every day, a
scheduled GitHub Actions workflow fetches the top discussions about
**Suno**, **Udio**, and AI-generated music from Reddit, stores them as a
structured JSON archive, and refreshes the digest below — no servers, no
manual work.

[![Daily AI Music Update](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml/badge.svg)](https://github.com/rughmax2-ai/AI-Music-Pulse/actions/workflows/daily-update.yml)

<!-- DIGEST:START -->

### Daily Digest — 2026-07-25

**64 posts** archived from 4 subreddits

| # | Post | Subreddit | Score | Comments |
| --- | --- | --- | --- | --- |
| 1 | [Didn't think people like this genuinely existed. Is this a common thing?](https://www.reddit.com/r/SunoAI/comments/1v5kgv2/didnt_think_people_like_this_genuinely_existed_is/) | r/SunoAI | – | – |
| 2 | [I thought songs you made on Free couldn't get commercial rights even if you upgraded after](https://www.reddit.com/r/SunoAI/comments/1v5awop/i_thought_songs_you_made_on_free_couldnt_get/) | r/SunoAI | – | – |
| 3 | [Does a Suno account gradually become trapped in a creative attractor? (Long-term Pro user ](https://www.reddit.com/r/SunoAI/comments/1v5zynr/does_a_suno_account_gradually_become_trapped_in_a/) | r/SunoAI | – | – |
| 4 | [Idea: A 30-Day Suno Song Challenge with Random Genre + Subject, Daily Winners, and a Liste](https://www.reddit.com/r/SunoAI/comments/1v5cqou/idea_a_30day_suno_song_challenge_with_random/) | r/SunoAI | – | – |
| 5 | [Writing NES/chiptune music. Any tips to get the right sound?](https://www.reddit.com/r/SunoAI/comments/1v5laim/writing_neschiptune_music_any_tips_to_get_the/) | r/SunoAI | – | – |
| 6 | [\[Cinematic EDM\] Spiritual Exile, Part II: Postumus by SlipshodDuke, Suno v5](https://www.reddit.com/r/SunoAI/comments/1v5tqev/cinematic_edm_spiritual_exile_part_ii_postumus_by/) | r/SunoAI | – | – |
| 7 | [\[Electro swing Dubstep\] One More Drink at the Speakeasy by SK](https://www.reddit.com/r/SunoAI/comments/1v5ru0w/electro_swing_dubstep_one_more_drink_at_the/) | r/SunoAI | – | – |
| 8 | [Hidden duration trick: set it in v5.5, then switch models — the duration setting stays act](https://www.reddit.com/r/SunoAI/comments/1v5lt17/hidden_duration_trick_set_it_in_v55_then_switch/) | r/SunoAI | – | – |
| 9 | [\[Sophistindustrial\] Chrome Longing by Cyborgized](https://www.reddit.com/r/SunoAI/comments/1v5k7t0/sophistindustrial_chrome_longing_by_cyborgized/) | r/SunoAI | – | – |
| 10 | [Problem with voices](https://www.reddit.com/r/SunoAI/comments/1v5axti/problem_with_voices/) | r/SunoAI | – | – |

Full structured data: [`data/daily/2026-07-25.json`](data/daily/2026-07-25.json) · Archive index: [`data/index.json`](data/index.json)

_Last updated: 2026-07-25 11:01 UTC_
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
