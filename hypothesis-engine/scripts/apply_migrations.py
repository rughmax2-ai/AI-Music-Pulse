#!/usr/bin/env python3
"""Apply Hypothesis Engine SQL migrations with credential gating.

Requires env vars (same names as scripts/sync_to_supabase.py):
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY

If either is missing, prints a dry-run listing of migration files and
exits 0 (so CI / local workflows without secrets stay green).

When credentials are present, this script attempts to execute each
migration via the Supabase SQL HTTP endpoint:

  POST {SUPABASE_URL}/rest/v1/rpc/exec_sql

That RPC is **not** created by default. Preferred apply paths:

  1. Supabase SQL editor (paste migration) on a branch/test project
  2. supabase db push / psql against the test database URL
  3. Optional: create a tightly scoped exec_sql RPC, then re-run this script

This tool never auto-promotes claims into public.chunks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HE_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = HE_ROOT / "supabase" / "migrations"


def list_migrations() -> list[Path]:
    if not MIGRATIONS_DIR.is_dir():
        return []
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def dry_run(migrations: list[Path], *, reason: str) -> int:
    print(reason, file=sys.stderr)
    print("Dry-run only — no SQL will be applied.", file=sys.stderr)
    if not migrations:
        print("No migration files found under", MIGRATIONS_DIR)
        return 0
    print(f"Would apply {len(migrations)} migration(s):")
    for path in migrations:
        size = path.stat().st_size
        print(f"  - {path.name} ({size} bytes)")
    print(
        "Apply on a Supabase branch/test project via SQL editor or psql, "
        "then re-run with credentials if an exec_sql RPC is available."
    )
    return 0


def try_exec_sql(sql: str, supabase_url: str, service_role_key: str) -> None:
    """Best-effort POST to a user-provided exec_sql RPC."""
    url = f"{supabase_url.rstrip('/')}/rest/v1/rpc/exec_sql"
    body = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Prefer": "return=minimal",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()


def apply_with_credentials(
    migrations: list[Path],
    supabase_url: str,
    service_role_key: str,
    force_rpc: bool,
) -> int:
    if not migrations:
        print("No migration files found.")
        return 0

    print(f"Credentials present. Target: {supabase_url}")
    print(
        "IMPORTANT: use a branch/test project. Do not apply unreviewed "
        "migrations to production."
    )

    applied: list[str] = []
    for path in migrations:
        sql = path.read_text(encoding="utf-8")
        print(f"Applying {path.name} ({len(sql)} chars)…")
        try:
            try_exec_sql(sql, supabase_url, service_role_key)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            print(
                f"RPC apply failed for {path.name} ({exc.code}): {detail}",
                file=sys.stderr,
            )
            print(
                "Falling back to documented manual apply. Migration file is "
                f"ready at: {path}",
                file=sys.stderr,
            )
            if force_rpc:
                return 1
            print("Would-run log (manual apply required):")
            for done in applied:
                print(f"  [done] {done}")
            print(f"  [failed_rpc] {path.name}")
            for pending in migrations[migrations.index(path) + 1 :]:
                print(f"  [pending] {pending.name}")
            return 0
        except urllib.error.URLError as exc:
            print(f"Network error applying {path.name}: {exc}", file=sys.stderr)
            return 1
        applied.append(path.name)
        print(f"  applied {path.name}")

    print(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-rpc",
        action="store_true",
        help="Exit non-zero if exec_sql RPC is unavailable when credentials exist",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List migrations without applying, even if credentials exist",
    )
    args = parser.parse_args(argv)

    migrations = list_migrations()
    supabase_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    has_credentials = bool(supabase_url and service_role_key)

    if args.dry_run:
        reason = (
            "--dry-run requested; credentials present but apply skipped."
            if has_credentials
            else "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set."
        )
        return dry_run(migrations, reason=reason)

    if not has_credentials:
        return dry_run(
            migrations,
            reason="SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set.",
        )

    return apply_with_credentials(
        migrations, supabase_url, service_role_key, args.force_rpc
    )


if __name__ == "__main__":
    sys.exit(main())
