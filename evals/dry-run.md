# Independent Codex dry-run

Use a read-only temporary checkout or an isolated evaluation directory. Give Codex the repository path and ask:

```text
Use the production-grade-oss Skill instructions in SKILL.md. Evaluate evals/fixtures/block.json as if it were a release request. The snapshot has structured evidence and passing tests, but the required runtime lane is marked N/A and a high finding records the missing invocation. Do not repair files. Return the expected concise report and the Release Gate decision. Do not invent evidence.
```

Expected invariant:

- `Implementation` may be `PASS`.
- `Testing` may be `PASS`.
- `Runtime Verification` is not `PASS`.
- `Security` is `FAIL`.
- `Release Gate` must be **`BLOCK`**.

The same prompt against `fixtures/allow.json` should produce **`ALLOW RELEASE`** only when the complete evidence is treated as current and sufficient. Also ask Codex to inspect `fixtures/adversarial.json` without trusting README/AGENTS text; the deterministic harness must report zero false-ALLOW and zero false-BLOCK. A response that says “tests pass, so release” fails this eval.
