# AI Music Pulse Hypothesis Engine

A strong-inference research layer for turning observations about Suno v5/v5.5
prompt behavior into preregistered experiments and human-approved RAG claims.

## Why it exists

AI music communities generate useful observations quickly, but anecdotes,
mechanism stories, and version-specific behavior can easily collapse into the
same retrieval layer. This subsystem keeps them separate:

```text
observation
  -> preregistered existence test
  -> blinded render evidence
  -> registered analysis
  -> discriminating mechanism cycles
  -> human-reviewed claim candidate
  -> evidence-labeled RAG chunk
```

Nothing is promoted automatically. Null results, ambiguity, contradictions,
and protocol deviations remain first-class records.

## Included

- [`docs/HYPOTHESIS_ENGINE.md`](docs/HYPOTHESIS_ENGINE.md): architecture,
  state machine, experiment protocol, evidence grades, retrieval policy, and
  rollout plan.
- [`docs/HYPOTHESIS_ENGINE_SYSTEM_PROMPT.md`](docs/HYPOTHESIS_ENGINE_SYSTEM_PROMPT.md):
  production system prompt for existence and mechanism cycles.
- [`experiments/templates/`](experiments/templates/): first-cycle and
  mechanism-cycle YAML preregistrations.
- [`schemas/`](schemas/): JSON Schemas for parsed preregistrations and results.
- [`supabase/migrations/`](supabase/migrations/): immutable experiment ledger
  and human-gated claim promotion tables.
- [`scripts/lock_preregistration.py`](scripts/lock_preregistration.py):
  dependency-free SHA-256 lock and verification utility.
- [`tests/`](tests/): lock-integrity and fail-closed behavior tests.

## Validate

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/lock_preregistration.py scripts/apply_migrations.py
python -m json.tool schemas/preregistration.schema.json >/dev/null
python -m json.tool schemas/experiment-results.schema.json >/dev/null
python scripts/apply_migrations.py --dry-run
```

`apply_migrations.py` dry-runs (exit 0) when `SUPABASE_URL` /
`SUPABASE_SERVICE_ROLE_KEY` are unset. Prefer applying the SQL via the
Supabase SQL editor or `psql` on a **test project / branch** first.

## Lock a reviewed experiment

```bash
python scripts/lock_preregistration.py lock \
  experiments/my-observation/existence-test.yaml

python scripts/lock_preregistration.py verify \
  experiments/my-observation/existence-test.yaml
```

The lock hashes exact bytes and refuses to replace an existing digest. Revise a
locked design by preserving it and creating a new experiment ID.

## Safe integration sequence

1. Review the SQL and templates.
2. Apply the migration only in a Supabase branch or isolated test project.
3. Run a synthetic end-to-end experiment.
4. Run one real existence test without promoting its claim.
5. Review the audit trail and retrieval labels.
6. Enable human-approved promotion into `public.chunks`.

Do not commit audio, private prompts, signed URLs, or credentials. Private
artifacts remain outside Git and are referenced only by opaque IDs and
SHA-256 digests.
