# Gate evals

These fixtures exercise the Skill's central decision invariant: a release is not allowed merely because an implementation exists or a test suite is green.

Run from the repository root:

```bash
python3 scripts/run_eval.py .
```

The harness evaluates two isolated, declarative snapshots:

- `fixtures/allow.json` has complete, fresh evidence and must produce `ALLOW RELEASE`.
- `fixtures/block.json` has passing tests but missing runtime/security evidence and must produce `BLOCK`.

This is a behavioral contract eval for the gate rubric. It does not claim to prove that every Codex response is correct, and it does not replace a real target-project runtime verification. The dry-run prompt in `dry-run.md` is suitable for an independent Codex evaluation.
