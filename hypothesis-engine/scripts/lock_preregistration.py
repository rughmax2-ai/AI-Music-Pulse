#!/usr/bin/env python3
"""Lock and verify preregistration files using SHA-256.

This utility intentionally hashes the exact file bytes instead of parsing and
re-serializing YAML. Any edit after review, including whitespace, invalidates
the lock.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
from pathlib import Path
import re
import sys


BUFFER_SIZE = 1024 * 1024
DIGEST_RE = re.compile(r"^(?P<digest>[a-f0-9]{64})  (?P<name>[^\r\n]+)\n?$")


class LockError(RuntimeError):
    """Raised when a preregistration cannot be safely locked or verified."""


def _validate_target(path: Path) -> Path:
    resolved_parent = path.parent.resolve(strict=True)
    target = resolved_parent / path.name
    if target.is_symlink():
        raise LockError(f"refusing symlink target: {path}")
    if not target.is_file():
        raise LockError(f"not a regular file: {path}")
    return target


def sha256_file(path: Path) -> str:
    target = _validate_target(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(BUFFER_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def sidecar_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.sha256")


def lock(path: Path) -> str:
    target = _validate_target(path)
    sidecar = sidecar_path(target)
    digest = sha256_file(target)
    payload = f"{digest}  {target.name}\n".encode("utf-8")

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(sidecar, flags, 0o600)
    except FileExistsError as exc:
        raise LockError(
            f"lock already exists: {sidecar}; preserve it and create a new revision"
        ) from exc

    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            sidecar.unlink()
        except FileNotFoundError:
            pass
        raise

    return digest


def read_locked_digest(path: Path) -> str:
    target = _validate_target(path)
    sidecar = sidecar_path(target)
    if sidecar.is_symlink():
        raise LockError(f"refusing symlink lock: {sidecar}")
    if not sidecar.is_file():
        raise LockError(f"missing lock: {sidecar}")

    payload = sidecar.read_text(encoding="utf-8")
    match = DIGEST_RE.fullmatch(payload)
    if not match:
        raise LockError(f"malformed lock: {sidecar}")
    if match.group("name") != target.name:
        raise LockError(
            f"lock names {match.group('name')!r}, expected {target.name!r}"
        )
    return match.group("digest")


def verify(path: Path) -> str:
    expected = read_locked_digest(path)
    actual = sha256_file(path)
    if not hmac.compare_digest(expected, actual):
        raise LockError(
            f"digest mismatch for {path}: expected {expected}, calculated {actual}"
        )
    return actual


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SHA-256 lock or verify an exact preregistration file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("lock", "verify", "digest"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "lock":
            digest = lock(args.file)
            print(f"locked {args.file}: {digest}")
        elif args.command == "verify":
            digest = verify(args.file)
            print(f"verified {args.file}: {digest}")
        else:
            digest = sha256_file(args.file)
            print(digest)
    except (LockError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
