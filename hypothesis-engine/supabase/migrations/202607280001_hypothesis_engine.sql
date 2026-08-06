-- Hypothesis Engine ledger
-- Apply only on a Supabase branch / isolated test project first.
-- No automatic promotion into public.chunks.

create schema if not exists he;

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- observations
-- ---------------------------------------------------------------------------
create table if not exists he.observations (
  id text primary key,
  raw_text text not null,
  operationalized_effect text not null,
  predicted_direction text not null
    check (predicted_direction in ('increase', 'decrease', 'two_sided')),
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- experiments
-- ---------------------------------------------------------------------------
create table if not exists he.experiments (
  id text primary key,
  observation_id text not null references he.observations (id),
  schema_version text not null default '1.0',
  cycle_number integer not null check (cycle_number >= 1),
  cycle_type text not null check (cycle_type in ('existence', 'mechanism')),
  status text not null default 'draft'
    check (status in (
      'draft', 'locked', 'collecting', 'rated', 'analyzed',
      'claim_candidate', 'promoted', 'aborted', 'deviated'
    )),
  provider text not null default 'suno',
  model_version text not null,
  interface_mode text,
  fields_under_test text[] not null default '{}',
  preregistration_sha256 text,
  locked_at_utc timestamptz,
  locked_by text,
  preregistration jsonb not null default '{}'::jsonb,
  parent_experiment_id text references he.experiments (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists experiments_observation_idx
  on he.experiments (observation_id);
create index if not exists experiments_status_idx
  on he.experiments (status);
create index if not exists experiments_cycle_type_idx
  on he.experiments (cycle_type);

-- ---------------------------------------------------------------------------
-- conditions
-- ---------------------------------------------------------------------------
create table if not exists he.conditions (
  id uuid primary key default gen_random_uuid(),
  experiment_id text not null references he.experiments (id) on delete cascade,
  code text not null,
  blind_code text not null,
  label text not null,
  n_planned integer not null check (n_planned >= 1),
  change_description text not null,
  unique (experiment_id, code),
  unique (experiment_id, blind_code)
);

create index if not exists conditions_experiment_idx
  on he.conditions (experiment_id);

-- ---------------------------------------------------------------------------
-- renders
-- ---------------------------------------------------------------------------
create table if not exists he.renders (
  id uuid primary key default gen_random_uuid(),
  experiment_id text not null references he.experiments (id) on delete cascade,
  condition_id uuid not null references he.conditions (id),
  ordinal integer not null check (ordinal >= 1),
  blind_code text not null,
  artifact_ref text,
  artifact_sha256 text,
  generated_at_utc timestamptz,
  model_version_observed text,
  metadata jsonb not null default '{}'::jsonb,
  unique (experiment_id, ordinal)
);

create index if not exists renders_experiment_idx
  on he.renders (experiment_id);
create index if not exists renders_condition_idx
  on he.renders (condition_id);

-- ---------------------------------------------------------------------------
-- ratings
-- ---------------------------------------------------------------------------
create table if not exists he.ratings (
  id uuid primary key default gen_random_uuid(),
  render_id uuid not null references he.renders (id) on delete cascade,
  experiment_id text not null references he.experiments (id) on delete cascade,
  rater_id text not null,
  score integer not null check (score in (0, 1, 2)),
  is_blind_repeat boolean not null default false,
  listened_seconds numeric,
  notes text,
  rated_at_utc timestamptz not null default now()
);

create index if not exists ratings_experiment_idx
  on he.ratings (experiment_id);
create index if not exists ratings_render_idx
  on he.ratings (render_id);

-- ---------------------------------------------------------------------------
-- analysis_results
-- ---------------------------------------------------------------------------
create table if not exists he.analysis_results (
  id uuid primary key default gen_random_uuid(),
  experiment_id text not null references he.experiments (id) on delete cascade,
  registered_statistic text not null,
  observed_value numeric,
  uncertainty_low numeric,
  uncertainty_high numeric,
  confidence_level numeric,
  classification text not null
    check (classification in (
      'effect_detected', 'practically_null', 'ambiguous',
      'deviated', 'aborted'
    )),
  hypothesis_outcomes jsonb not null default '{}'::jsonb,
  analysis_notes text,
  analyzed_at_utc timestamptz not null default now(),
  analyzed_by text
);

create index if not exists analysis_results_experiment_idx
  on he.analysis_results (experiment_id);

-- ---------------------------------------------------------------------------
-- claim_candidates (never auto-promoted)
-- ---------------------------------------------------------------------------
create table if not exists he.claim_candidates (
  id uuid primary key default gen_random_uuid(),
  experiment_id text not null references he.experiments (id) on delete cascade,
  claim_text text not null,
  evidence_grade text not null
    check (evidence_grade in (
      'anecdote', 'preregistered_effect', 'surviving_mechanism',
      'contradiction', 'retired'
    )),
  status text not null default 'draft'
    check (status in ('draft', 'rejected', 'approved', 'promoted')),
  chunk_id uuid,
  created_at timestamptz not null default now()
);

create index if not exists claim_candidates_experiment_idx
  on he.claim_candidates (experiment_id);
create index if not exists claim_candidates_status_idx
  on he.claim_candidates (status);

-- ---------------------------------------------------------------------------
-- promotion_audit (human gate)
-- ---------------------------------------------------------------------------
create table if not exists he.promotion_audit (
  id uuid primary key default gen_random_uuid(),
  claim_candidate_id uuid not null
    references he.claim_candidates (id) on delete cascade,
  decision text not null
    check (decision in ('approved', 'rejected', 'deferred')),
  decided_by text not null,
  decided_at_utc timestamptz not null default now(),
  rationale text,
  chunks_row_id uuid
);

create index if not exists promotion_audit_claim_idx
  on he.promotion_audit (claim_candidate_id);

-- ---------------------------------------------------------------------------
-- RLS: deny-by-default for anon/authenticated; service_role bypasses RLS
-- ---------------------------------------------------------------------------
alter table he.observations enable row level security;
alter table he.experiments enable row level security;
alter table he.conditions enable row level security;
alter table he.renders enable row level security;
alter table he.ratings enable row level security;
alter table he.analysis_results enable row level security;
alter table he.claim_candidates enable row level security;
alter table he.promotion_audit enable row level security;

-- Migration bookkeeping (optional local tracking table in he schema)
create table if not exists he.schema_migrations (
  filename text primary key,
  applied_at_utc timestamptz not null default now()
);

insert into he.schema_migrations (filename)
values ('202607280001_hypothesis_engine.sql')
on conflict (filename) do nothing;
