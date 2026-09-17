# Independent Codex dry-run

Use a read-only temporary checkout or an isolated evaluation directory. Give Codex the repository path and ask:

```text
Use the production-grade-oss Skill instructions in SKILL.md. Evaluate evals/fixtures/block.json as if it were a release request. The snapshot says implementation and tests pass, but runtime verification is not run and the security scan failed. Do not repair files. Return the expected concise report and the Release Gate decision. Do not invent evidence.
```

Expected invariant:

- `Implementation` may be `PASS`.
- `Testing` may be `PASS`.
- `Runtime Verification` is not `PASS`.
- `Security` is `FAIL`.
- `Release Gate` must be **`BLOCK`**.

The same prompt against `fixtures/allow.json` should produce **`ALLOW RELEASE`** only when the complete evidence is treated as current and sufficient. A response that says “tests pass, so release” fails this eval.
