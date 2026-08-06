# Discord activation (Phase 4)

The daily workflow already runs `scripts/fetch_discord.py`. It **no-ops**
until secrets are present. Use this checklist when you are ready to go live.

## 1. Create the bot

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create an application → Bot → Reset Token → copy the token.
3. Enable **Message Content Intent** if you need message bodies.
4. Invite the bot to the target server with permission to **View Channel**
   and **Read Message History**.

## 2. Configure secrets

In the GitHub repo: **Settings → Secrets and variables → Actions**:

| Secret | Value |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Bot token |
| `DISCORD_CHANNEL_IDS` | Comma-separated channel snowflakes |

For local runs, copy [`.env.example`](../.env.example) to `.env`.

Optionally list channels in [`sources.json`](../sources.json):

```json
"discord": {
  "enabled": true,
  "channels": [
    { "id": "1234567890", "topic": "Suno" }
  ]
}
```

## 3. Implement the fetch body

Replace the Phase 4 placeholder in `scripts/fetch_discord.py` with:

1. Discord REST reads of recent messages in configured channels (stdlib
   `urllib`, same style as `fetch_reddit.py`).
2. Keyword filter using `sources.json` → `keywords` where useful.
3. Map each message into the shared post shape (`id`, `title`, `author`,
   `created_utc`, `permalink`, `selftext`, `platform: "discord"`, …).
4. Merge into `data/daily/YYYY-MM-DD.json` (dedupe by message id). When
   Discord contributes, set `sources.platform` to `"mixed"` (or a platform
   list) without breaking Reddit-only days.
5. Extend `scripts/sync_to_supabase.py` with `source_type: "discord_message"`.

## 4. Verify

```bash
export DISCORD_BOT_TOKEN=…
export DISCORD_CHANNEL_IDS=…
python scripts/fetch_discord.py
python scripts/update_readme.py
python scripts/build_site.py
```

Confirm the archive, README digest, and `site/` pages include Discord
rows, then re-run the **Daily AI Music Update** workflow.

Do not commit tokens or `.env` files.
