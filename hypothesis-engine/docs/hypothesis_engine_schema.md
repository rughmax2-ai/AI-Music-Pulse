# Hypothesis Engine schema map

PostgreSQL schema: `he`. Applied by
[`../supabase/migrations/202607280001_hypothesis_engine.sql`](../supabase/migrations/202607280001_hypothesis_engine.sql).

## Tables

### `he.observations`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | text PK | e.g. `obs_short_slug` |
| `raw_text` | text | Unedited observation |
| `operationalized_effect` | text | One measurable effect |
| `predicted_direction` | text | `increase` \| `decrease` \| `two_sided` |
| `created_at` | timestamptz | default `now()` |
| `metadata` | jsonb | default `{}` |

### `he.experiments`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | text PK | e.g. `exp_YYYYMMDD_short_slug_e1` |
| `observation_id` | text FK → observations | |
| `schema_version` | text | e.g. `1.0` |
| `cycle_number` | int | |
| `cycle_type` | text | `existence` \| `mechanism` |
| `status` | text | draft → locked → … |
| `provider` | text | e.g. `suno` |
| `model_version` | text | e.g. `v5.5` |
| `interface_mode` | text | |
| `fields_under_test` | text[] | |
| `preregistration_sha256` | text | null until locked |
| `locked_at_utc` | timestamptz | |
| `locked_by` | text | |
| `preregistration` | jsonb | full parsed YAML snapshot |
| `parent_experiment_id` | text | existence id for mechanism cycles |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

### `he.conditions`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `experiment_id` | text FK | |
| `code` | text | A / B / C |
| `blind_code` | text | LARK / MOSS / … |
| `label` | text | control / treatment |
| `n_planned` | int | |
| `change_description` | text | |

Unique on `(experiment_id, code)` and `(experiment_id, blind_code)`.

### `he.renders`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `experiment_id` | text FK | |
| `condition_id` | uuid FK | |
| `ordinal` | int | position in render order |
| `blind_code` | text | as presented to rater |
| `artifact_ref` | text | opaque private storage id |
| `artifact_sha256` | text | content digest |
| `generated_at_utc` | timestamptz | |
| `model_version_observed` | text | for drift checks |
| `metadata` | jsonb | |

### `he.ratings`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `render_id` | uuid FK | |
| `experiment_id` | text FK | |
| `rater_id` | text | |
| `score` | int | 0 kill / 1 fine / 2 magic |
| `is_blind_repeat` | boolean | |
| `listened_seconds` | numeric | |
| `notes` | text | optional; no protocol leaks |
| `rated_at_utc` | timestamptz | |

### `he.analysis_results`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `experiment_id` | text FK | |
| `registered_statistic` | text | |
| `observed_value` | numeric | |
| `uncertainty_low` | numeric | |
| `uncertainty_high` | numeric | |
| `confidence_level` | numeric | |
| `classification` | text | effect_detected / practically_null / … |
| `hypothesis_outcomes` | jsonb | mechanism cycles |
| `analysis_notes` | text | |
| `analyzed_at_utc` | timestamptz | |
| `analyzed_by` | text | |

### `he.claim_candidates`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `experiment_id` | text FK | |
| `claim_text` | text | |
| `evidence_grade` | text | |
| `status` | text | `draft` \| `rejected` \| `approved` \| `promoted` |
| `chunk_id` | uuid | nullable; set only after promotion into `public.chunks` |
| `created_at` | timestamptz | |

### `he.promotion_audit`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | uuid PK | |
| `claim_candidate_id` | uuid FK | |
| `decision` | text | `approved` \| `rejected` \| `deferred` |
| `decided_by` | text | human id |
| `decided_at_utc` | timestamptz | |
| `rationale` | text | |
| `chunks_row_id` | uuid | nullable target in `public.chunks` |

## Relationships

```text
observations 1──* experiments
experiments 1──* conditions
experiments 1──* renders ──* ratings
experiments 1──* analysis_results
experiments 1──* claim_candidates 1──* promotion_audit
```

## Security

All `he.*` tables have RLS enabled. Authenticated anon clients have no
policies (deny by default). `service_role` bypasses RLS for controlled
writes. No trigger auto-inserts into `public.chunks`.
