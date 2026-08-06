# Hypothesis Engine

A strong-inference research layer for Suno v5/v5.5 prompt behavior.
Community digests (Reddit/Discord) stay separate; this subsystem only
handles preregistered experiments and human-approved RAG claims.

## State machine

```text
draft
  -> locked          (SHA-256 sidecar written; bytes immutable)
  -> collecting      (blinded renders under locked protocol)
  -> rated           (blind human ratings recorded)
  -> analyzed        (registered statistic + classification)
  -> claim_candidate (optional draft claim; not in RAG yet)
  -> promoted        (human approval only; may copy into public.chunks)
  -> aborted|deviated (first-class terminal states)
```

Nothing is promoted automatically. Null results, ambiguity, contradictions,
and protocol deviations remain first-class records.

## Cycle types

| Type | Purpose |
| --- | --- |
| `existence` | Detect whether a declared effect exists. No mechanism hypotheses. |
| `mechanism` | Discriminate among exactly three falsifiable mechanism hypotheses after an existence effect survives. |

Templates live in [`experiments/templates/`](../experiments/templates/).

## Evidence grades

| Grade | Meaning |
| --- | --- |
| `anecdote` | Unlocked observation only |
| `preregistered_effect` | Locked existence cycle with registered classification |
| `surviving_mechanism` | Mechanism cycle with one or more surviving hypotheses |
| `contradiction` | Later cycle falsifies or conflicts with an earlier claim |
| `retired` | Model-version or interface drift retires prior findings |

Retrieval policy: RAG consumers must prefer higher grades and must never
treat anecdotes as confirmed effects.

## Protocol essentials

1. Operationalize one audible or measurable effect.
2. Lock the preregistration YAML with
   [`scripts/lock_preregistration.py`](../scripts/lock_preregistration.py).
3. Collect blinded renders; store private audio outside git; keep only opaque
   refs + SHA-256 in the ledger.
4. Rate blindly on the registered scale (kill / fine / magic).
5. Analyze only the registered primary endpoint.
6. Classify: `effect_detected` | `practically_null` | `ambiguous` |
   `deviated` | `aborted`.
7. Optional claim candidate. Promotion requires an explicit row in
   `he.promotion_audit` with decision `approved`.

## Database

Schema `he` is defined in
[`supabase/migrations/202607280001_hypothesis_engine.sql`](../supabase/migrations/202607280001_hypothesis_engine.sql).
Field map: [`hypothesis_engine_schema.md`](hypothesis_engine_schema.md).

Apply with [`scripts/apply_migrations.py`](../scripts/apply_migrations.py)
against a **Supabase branch or isolated test project first**. Never apply
unreviewed migrations to production.

## Rollout plan

1. Review SQL and templates.
2. Apply migration on a test project (or dry-run without credentials).
3. Synthetic end-to-end experiment (lock → fake renders → analysis).
4. One real existence test **without** claim promotion.
5. Review audit trail and retrieval labels.
6. Enable human-approved promotion into `public.chunks`.

## Privacy

Do not commit audio, private prompts, signed URLs, or credentials. Private
artifacts remain outside Git and are referenced only by opaque IDs and
SHA-256 digests.
