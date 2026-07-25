# Handoff: Supabase + local-LLM knowledge base for AI Music Pulse

Written by a Claude Code instance on the `sherri` machine, for whichever Claude
instance picks this up on the machine running LM Studio. Read this fully
before doing anything — several decisions are made, several are still open,
and one is blocked on you.

## 1. What this project currently is

Repo: `AI-Music-Pulse` (GitHub: `rughmax2-ai/AI-Music-Pulse`), local checkout
at `~/Suno-Pulse-Dir/AI-Music-Pulse` on the `sherri` machine.

Today it's a single GitHub Actions cron (`.github/workflows/daily-update.yml`,
`15 6 * * *` UTC) that:

1. Runs `scripts/fetch_reddit.py` — pulls top-of-day posts from Suno/Udio/AI
   music subreddits (config in `sources.json`), writes
   `data/daily/YYYY-MM-DD.json` + rolling `data/index.json`.
2. Runs `scripts/update_readme.py` — renders the latest day into a digest
   table in `README.md` between `<!-- DIGEST:START/END -->` markers.
3. Commits and pushes both, only if something changed.

No LLM, no database — it's pure JSON-in-git today.

## 2. What the user actually wants (target architecture)

Two **separate** cron jobs:

- **Cron A — fetch** (stays on GitHub Actions, cloud, already working):
  same daily Reddit fetch, but writes rows into **Supabase** instead of
  committing JSON files to git.
- **Cron B — summarize** (runs locally on whichever machine serves the LLM,
  i.e. **not** `sherri` — see §5): reads the day's newly-fetched posts from
  Supabase, sends them to a **local LLM via LM Studio** (model: Qwen3-30B-A3B,
  a ~30B-total/~3B-active MoE — the user wrote "Qwen 35B 3BA Moe", this is
  almost certainly Qwen3-30B-A3B; confirm the exact model id LM Studio
  reports), asks it to extract "the most useful info," and **merges** that
  into a persistent, evolving "running context" record in Supabase — not a
  fresh daily digest that replaces the old one, but a knowledge base that
  accumulates/updates over time as new posts come in every day.

## 3. Decisions already made (with the user, via AskUserQuestion)

| Decision | Choice | Why |
|---|---|---|
| Storage | Supabase (existing project, see §4) | User wants to get off JSON-in-git |
| Fetch cron location | Stays on GitHub Actions | Already reliable, cloud-scheduled, no dependency on any machine being on |
| Summarize cron location | Runs on the machine serving the local LLM | The LLM is local — GitHub Actions runners can't reach it unless tunneled, which the user explicitly did *not* want ("Both on GitHub Actions" was rejected as "not truly local anymore") |
| LLM runtime | LM Studio | User confirmed after ruling out Ollama/llama.cpp/vLLM |
| Model | Qwen3-30B-A3B (MoE) | User's choice; verify exact LM Studio model id string before wiring the API calls |

## 4. Supabase project — already exists, already schema'd

- Project ref/id: `xocrwemfdxhuefdzolxv`
- URL: `https://xocrwemfdxhuefdzolxv.supabase.co`
- Org: `rughmax2-ai's Project` (matches the GitHub repo owner — this is
  clearly the intended project, not an accident)
- Legacy anon key (safe to embed client-side, RLS-gated):
  `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvY3J3ZW1mZHhodWVmZHpvbHh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4NDA3ODYsImV4cCI6MjEwMDQxNjc4Nn0.Ks3ZecKmXLXTI7DcO-l2wdT4ZFQUxw6efcsPyZCEgSc`
- Publishable key (modern equivalent): `sb_publishable_2Cu33KRM95BFelhNrF829w_JacKNjYW`
- **Service role key: NOT included here.** All tables have RLS enabled, so
  both cron scripts (fetch + summarize) will need the service role key for
  server-side writes. It is not retrievable via MCP tools by design — the
  user must pull it themselves from the Supabase dashboard
  (Project Settings → API → service_role secret) and store it as:
  - a GitHub Actions repo secret (for Cron A), and
  - a local env var / secrets file on the LM Studio machine (for Cron B),
  never committed to git, never pasted into chat.

**Existing schema (all tables currently empty, `rows: 0`):**

```
public.documents
  id            uuid PK, default gen_random_uuid()
  source_type   text
  source_url    text, nullable
  title         text, nullable
  raw_content   text, nullable
  metadata      jsonb, default '{}'
  created_at    timestamptz, default now()

public.chunks
  id            uuid PK, default gen_random_uuid()
  document_id   uuid  -> documents.id
  chunk_index   int4
  content       text
  embedding     vector, nullable   -- pgvector
  tsv           tsvector, generated from content (full-text search)
  token_count   int4, nullable
  metadata      jsonb, default '{}'
  created_at    timestamptz, default now()

public.eval_queries   -- for retrieval eval, not needed for this task
public.eval_runs      -- for retrieval eval, not needed for this task
```

This is a **RAG-ready schema someone already built** (pgvector + tsvector
hybrid search, chunking, eval harness) and it fits this task well without
inventing new tables. Proposed mapping (recommend confirming with the user
before building, but this is the natural fit):

- Each fetched Reddit post → one `documents` row:
  `source_type='reddit_post'`, `source_url=permalink`, `title=post title`,
  `raw_content=selftext`, `metadata={subreddit, topic, score, num_comments,
  author, created_utc, fetch_date}`.
- The "running context" itself → **one** `documents` row that Cron B
  **upserts** (not inserts fresh each day): e.g. `source_type='knowledge_base'`
  with a stable identifying key in `metadata` (or just "the single row where
  `source_type='knowledge_base'`"), `raw_content` = the current accumulated
  summary text, updated in place each run so it keeps evolving.
- Optional/stretch: also chunk+embed the running context into `chunks` so
  it's retrievable via the same vector/full-text search as everything else —
  requires an embedding model too (LM Studio can serve one, or use a small
  dedicated embedding model). Not required for the core ask; flag as a
  follow-up, don't build it unasked.

## 5. Open blocker — LM Studio location (unresolved, ask the user)

The user confirmed LM Studio is **not** running on `sherri`
(`localhost:1234` was unreachable there, and they corrected the assumption
that it would be started on that machine). Before writing Cron B, you need
from the user:

1. The reachable `host:port` for LM Studio's OpenAI-compatible server
   (LM Studio's default port is `1234`, endpoint shape
   `POST /v1/chat/completions`, model list at `GET /v1/models`).
2. Whether Cron B should run **on that same machine** (simplest — LLM is
   local to the cron) — confirm that machine is always-on/reachable daily,
   the same way the user confirmed `sherri` is.
3. The exact model id string as LM Studio reports it in `/v1/models`, to
   put in the `model` field of chat completion requests.
4. A schedule for Cron B — recommend offsetting it a few hours after Cron
   A's `15 6 * * *` UTC fetch (e.g. `0 9 * * *` UTC) so it always has that
   day's posts available before summarizing.

## 6. Concrete next steps

1. Resolve §5 with the user.
2. Get the Supabase service role key from the user (dashboard, not MCP).
3. Write `scripts/fetch_reddit_supabase.py` — same fetch logic as
   `scripts/fetch_reddit.py`, but upsert into `documents` (dedupe by
   `source_url`/reddit post id in metadata) instead of writing local JSON.
   Update `.github/workflows/daily-update.yml` to call it and drop the
   git-commit step (or keep both during a transition period if the user
   wants a fallback).
4. Write `scripts/summarize_context.py` — queries `documents` for
   `source_type='reddit_post'` rows from the current fetch day, calls LM
   Studio's chat completions endpoint with a prompt like "here is today's
   running context + today's new posts, extract what's genuinely useful and
   produce an updated running context," then upserts the result into the
   `source_type='knowledge_base'` document.
5. Install this as a cron (crontab or systemd timer, per what §5 decides)
   on the LM Studio machine.
6. Test both crons manually end-to-end before trusting the schedule.

## 7. Things NOT decided yet — don't assume

- Whether to keep `data/daily/*.json` + README digest running in parallel
  as a human-readable fallback, or fully retire them once Supabase is live.
- Whether the running context is a single ever-growing text blob, or gets
  periodically re-consolidated/summarized-of-summaries to control length
  (worth raising once you see how big it gets after a week or two).
- Retention: `data/daily/*.json` currently accumulates forever; decide if
  `documents` should too, or get pruned.
