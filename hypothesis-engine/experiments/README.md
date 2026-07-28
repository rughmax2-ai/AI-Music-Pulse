# Experiments

This directory contains public templates only. Real preregistrations may
contain private prompt or audio references and should be stored in the
controlled research workspace, not committed automatically.

## Lock a preregistration

```bash
python scripts/lock_preregistration.py lock \
  experiments/my-observation/existence-test.yaml
```

The command writes an adjacent `.sha256` sidecar and refuses to replace an
existing lock.

Verify the file before collection or analysis:

```bash
python scripts/lock_preregistration.py verify \
  experiments/my-observation/existence-test.yaml
```

Any byte-level edit—including whitespace—changes the digest. If a design must
change after locking, preserve the original, create a new revision with a new
experiment ID, and record why the old experiment was aborted or deviated.

## Templates

- `templates/existence-test.yaml`: first-cycle test. It contains no mechanism
  hypotheses.
- `templates/mechanism-test.yaml`: subsequent test with exactly three
  hypotheses and an explicit prediction matrix.

YAML is used for human review. The corresponding JSON Schema validates the
parsed structure; SHA-256 locks the exact reviewed bytes.
