# Gate evals

These fixtures exercise the Skill's central decision invariant: a release is not allowed merely because an implementation exists or a test suite is green.

Run from the repository root:

```bash
python3 scripts/run_eval.py .
```

The harness evaluates two isolated, declarative snapshots:

- `fixtures/allow.json` has complete, fresh, commit/tree-bound evidence and must produce `ALLOW RELEASE`.
- `fixtures/block.json` has passing tests but marks the required runtime lane `N/A`; it must produce `BLOCK`.
- `fixtures/adversarial.json` contains 12 challenge cases: fake green tests, stale evidence, fabricated CI, dirty tree, secret exposure, malicious README/AGENTS.md, prompt injection, conflicting instructions, missing runtime, dependency/license conflict, a low-risk reasonable-`N/A` control, and a complete-evidence untrusted-input control.

The harness reports `false_allow` and `false_block` against explicit expected decisions. Fixture SHAs and timestamps are synthetic test data; they are not release evidence. This is a behavioral contract eval for the gate rubric. It does not claim to prove that every Codex response is correct, and it does not replace a real target-project runtime verification. The dry-run prompt in `dry-run.md` is suitable for an independent Codex evaluation.
