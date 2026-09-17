---
name: production-grade-oss
description: Apply a production-grade open-source engineering and release gate to new, changed, refactored, reviewed, or released projects; require evidence for architecture, quality, testing, security, privacy, supply chain, CI/CD, documentation, and runtime behavior.
---

# Production Grade OSS

Use this skill by default for any new project, feature, bug fix, refactor, review, or release. It is a decision aid, not permission to broaden scope: preserve the user's requested platform, data, repository state, and authorization boundaries.

## Operating contract

Before editing, write a compact contract:

- **Actual goal:** the user-visible outcome, separate from the requested implementation.
- **Success criteria:** observable facts, with a command, test, or runtime observation that can prove each one.
- **Failure criteria:** false positives, unsafe behavior, missing recovery, stale data, untested paths, and unresolved high-risk findings.
- **Non-goals:** work that is not necessary for the goal.
- **Risk:** choose the smallest risk-appropriate verification set; do not manufacture architecture, dependencies, or process for low-risk work.

Inspect the current repository before changing it: project instructions, goal and acceptance docs, README, build/test configuration, dependency manifests and locks, runtime entry points, Git status/HEAD, and recent history. Preserve unrelated user changes. Do not reset, clean, discard, or overwrite work without explicit authorization.

## Gate lanes

Run the applicable lanes below. Record `PASS`, `FAIL`, `BLOCKED`, or `N/A` with evidence, source, timestamp, method, confidence, and freshness. `N/A` needs a short reason; it is not a silent omission.

### Architecture

- Map modules, trust boundaries, data flow, public contracts, configuration, persistence, external services, and ownership.
- Check separation of concerns, dependency direction, failure propagation, observability, migration/compatibility impact, portability, and rollback/recovery.
- Prefer the smallest design that satisfies the actual goal. Record why a new abstraction, service, framework, or dependency is necessary.

### Code quality

- Keep behavior explicit, cohesive, readable, and idiomatic for the existing stack.
- Validate untrusted input at boundaries; handle errors deliberately; preserve useful diagnostics without leaking sensitive data.
- Remove dead paths, accidental duplication, silent catches, test-only success paths, placeholder behavior, and unbounded resource use.
- Preserve compatible interfaces and historical data unless a breaking change, migration, and recovery path are intentional and documented.

### Testing

- Select tests from the risk and blast radius: unit, integration, contract, persistence, end-to-end, and failure-path checks as applicable.
- Include invalid, empty, unavailable-dependency, timeout, permission, restart/recovery, and compatibility cases when they can affect the goal.
- Run from the repository root with a fresh or reproducible environment where practical. Never weaken assertions, delete failing tests, or replace a required real path with a mock.
- A green test suite proves only the tested behavior; it does not prove runtime, deployment, security, or user success by itself.

### Security

- Identify assets, actors, trust boundaries, abuse cases, authentication, authorization, injection, serialization, filesystem, network, and supply-chain risks.
- Enforce least privilege, safe defaults, explicit validation, secure transport where applicable, bounded resources, and useful failure responses.
- Scan source, history-relevant release paths, generated artifacts, logs, CI configuration, and dependencies for secrets and dangerous defaults. Never print, commit, or repeat credentials.

### Privacy

- Minimize collection, exposure, retention, and access to personal or sensitive data.
- Document purpose, user control/consent where relevant, deletion/export behavior, redaction, telemetry choices, and data residency or processor assumptions when applicable.
- Treat identifiers, logs, fixtures, screenshots, crash reports, and analytics as possible personal data. Do not use real user data in tests unless explicitly authorized and protected.

### Dependency and supply chain

- Inventory direct and transitive dependencies, lock versions, package sources, licenses, provenance, integrity checks, and platform support.
- Prefer mature, maintained, license-compatible components and existing standard-library/platform capabilities. Before adding one, record capability, maintenance, security, license, size, and operational trade-offs.
- Review new versions, transitive changes, install/build scripts, generated code, vendored code, and release artifacts. Do not copy GPL/AGPL or commercially restricted code into an incompatible project.

### CI/CD

- CI must reproduce the meaningful checks from a clean checkout: format/lint, tests, dependency/security checks, documentation/packaging checks, and the eval or release gate when present.
- Pin or otherwise control third-party actions and tool versions according to project risk; use least-privilege workflow permissions; avoid secrets in logs; retain actionable artifacts.
- Build once and verify the exact artifact that would be released. Define branch/tag/release triggers, failure visibility, provenance, rollback, and deployment authorization where applicable.

### README, LICENSE, CONTRIBUTING, SECURITY

For a project being created, shared, or released, verify that these documents exist and describe the real project (or document a justified exception):

- `README.md`: purpose, scope, supported environment, installation, usage, configuration, tests, limitations, and truthful status.
- `LICENSE`: the actual license and any required third-party notices; do not claim a license that is not present.
- `CONTRIBUTING.md`: setup, development checks, change expectations, tests, review, and conduct/reporting route as appropriate.
- `SECURITY.md`: supported versions, private vulnerability-reporting route, response expectations, and what not to disclose publicly.
- `CHANGELOG.md` or release notes: user-visible changes, compatibility, migrations, known limitations, and exact version scope.

Do not invent stars, users, downloads, benchmarks, coverage, tests, endorsements, or adoption. Say `unknown`, `not measured`, or `not run` when evidence is unavailable.

### Runtime verification

Trace the real path where risk warrants it: trigger → processing → output → error handling → recovery. Use fresh inputs and actual processes, files, requests, database reads, UI interaction, listeners, or deployment observations appropriate to the project. Cross-check the implementation's result with an independent observation. Verify at least one safe failure path. Clearly separate code/test evidence from runtime evidence; “能跑就算完成” is not an acceptance criterion.

## Release Gate

Return **`ALLOW RELEASE`** only when:

1. The actual goal and acceptance criteria are met.
2. Required lanes are `PASS` with fresh, reproducible evidence and no low-confidence critical claim.
3. No unresolved Critical or goal-affecting High finding remains.
4. The expected diff/tree is reviewed; artifacts, version, metadata, documentation, and license are consistent.
5. Runtime behavior is verified when the project has a runnable path, or the limitation is explicit and accepted for a non-runnable artifact.
6. CI/CD, rollback/recovery, and publication authorization are adequate for the requested release scope.

Return **`BLOCK`** for a failed or missing required check, unverifiable core behavior, secret/privacy exposure, incompatible license, unsafe dependency, unexplained breaking change, dirty or unexpected release state, fabricated evidence, or any unresolved Critical/High finding. Do not hide a failure by relabeling it `N/A`.

## No meaningless engineering

Do not add layers, tools, metrics, dependencies, abstractions, tests, documentation, or workflows merely to make a project look mature. Every change must serve correctness, safety, user value, operability, maintainability, or a stated acceptance criterion. Stop when the goal is proven and remaining work has low marginal value.

## Expected report

Use concise, claim-level evidence and finish with:

```text
Goal / Risk Level:
Implementation: PASS|FAIL
Runtime Verification: PASS|FAIL|N/A
Architecture / Quality / Testing: PASS|FAIL|N/A
Security / Privacy / Supply Chain: PASS|FAIL|N/A
CI/CD / Documentation: PASS|FAIL|N/A
Regression / Adversarial Review: PASS|FAIL
Release Gate: ALLOW RELEASE|BLOCK
Confidence: HIGH|MEDIUM|LOW
Known Limitations:
Evidence Path:
Production Changed: YES|NO
```

Use [checklists/project-gate.md](checklists/project-gate.md) for a compact review and [examples/release-gate-report.md](examples/release-gate-report.md) for report shape. Use [evals/README.md](evals/README.md) when validating the gate itself.
