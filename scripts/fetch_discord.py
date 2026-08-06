#!/usr/bin/env python3
"""
fetch_discord.py — Discord fetcher scaffold for AI Music Pulse.

Writes into the same daily archive schema as fetch_reddit.py when a bot
token and channel IDs are configured. Until then this module no-ops so
the daily workflow stays green without Discord secrets.

Env:
  DISCORD_BOT_TOKEN      required to enable fetching
  DISCORD_CHANNEL_IDS    comma-separated channel snowflakes (optional until Phase 4)

Config (sources.json → "discord"):
  channels: [{ "id": "...", "topic": "..." }, ...]
  enabled: bool (optional; default true when token present)

Phase 4 will replace the placeholder body with real Discord API reads
and merge posts into data/daily/YYYY-MM-DD.json.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = REPO_ROOT / "sources.json"


def main() -> int:
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        print("Discord disabled; skipping (DISCORD_BOT_TOKEN not set)")
        return 0

    sources = {}
    if SOURCES_FILE.exists():
        sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    discord_cfg = sources.get("discord") or {}
    if discord_cfg.get("enabled") is False:
        print("Discord disabled; skipping (sources.json discord.enabled=false)")
        return 0

    channel_ids_env = os.environ.get("DISCORD_CHANNEL_IDS", "").strip()
    channels = list(discord_cfg.get("channels") or [])
    if channel_ids_env:
        for cid in channel_ids_env.split(","):
            cid = cid.strip()
            if cid and not any(str(c.get("id")) == cid for c in channels):
                channels.append({"id": cid, "topic": "Discord"})

    if not channels:
        print(
            "Discord token present but no channel IDs configured "
            "(set DISCORD_CHANNEL_IDS or sources.json discord.channels); "
            "skipping until Phase 4 activation."
        )
        return 0

    # Phase 4 placeholder: real Discord REST fetch + archive merge.
    day_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(
        f"Discord fetch not implemented yet (Phase 4). "
        f"Would fetch {len(channels)} channel(s) for {day_key}."
    )
    print("Exiting cleanly without modifying the archive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
