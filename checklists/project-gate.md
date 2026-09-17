# Production-grade OSS project gate

Mark each item with evidence or a justified `N/A`. A checked box without a source is not evidence.

## Goal and baseline

- [ ] Actual user goal, success criteria, failure criteria, and non-goals are written.
- [ ] Risk and blast radius are recorded.
- [ ] One Risk Profile (`LOW` / `MEDIUM` / `HIGH`) and one Project Profile (`Web` / `API` / `CLI` / `Library` / `AI Agent / Skill`) are recorded.
- [ ] Required lanes were calculated from those profiles; optional lanes have specific scope reasons for `N/A`.
- [ ] Project instructions, acceptance docs, entry points, dependency manifests, and Git status/HEAD were inspected.
- [ ] Unrelated user changes are preserved; the expected diff is known.

## Architecture and quality

- [ ] Modules, data flow, trust boundaries, public contracts, configuration, and failure propagation are understood.
- [ ] The smallest effective design was chosen; new layers or dependencies have a recorded reason.
- [ ] Input validation, error handling, compatibility, resource bounds, and observability are adequate.
- [ ] No dead code, fake success, silent error, or placeholder behavior remains in the shipped path.

## Tests and runtime

- [ ] Tests cover the changed behavior and relevant invalid, empty, unavailable, permission, timeout, and recovery cases.
- [ ] Tests ran from a clean or reproducible environment and assertions were not weakened.
- [ ] The real user path was exercised with fresh data when it is runnable.
- [ ] Output and at least one failure/recovery result were independently observed.

## Security, privacy, and supply chain

- [ ] Threat boundaries, authn/authz, injection, filesystem/network, and safe defaults were reviewed.
- [ ] Secrets and sensitive data are absent from source, history-relevant artifacts, logs, fixtures, and CI output.
- [ ] Collection, retention, access, redaction, deletion, and user-control implications were reviewed.
- [ ] Direct/transitive dependencies, locks, provenance, integrity, licenses, maintenance, and platform support were checked.

## CI/CD and project documents

- [ ] CI runs meaningful lint, tests, security, packaging, and eval/release checks on a clean checkout.
- [ ] Workflow permissions and third-party action/tool versions are controlled for project risk.
- [ ] `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and changelog/release notes are present and truthful.
- [ ] The exact artifact, version, metadata, rollback/recovery, and publication scope are identified.

## Evidence record

- [ ] Every known lane has exactly one record with `lane`, `status`, `kind`, `source`, `method`, timezone-qualified `timestamp`, matching full `commit_sha` and `tree_sha`, concrete `result`, `confidence`, and `freshness`.
- [ ] Every `PASS` is tied to independently attributable command, runtime, CI, scanner, boundary-test, or review evidence; a prose claim or workflow file is not enough.
- [ ] Every `N/A` has a scope-analysis record and a concrete reason; a required lane is never hidden as `N/A`.
- [ ] Stale, unknown, low-confidence, duplicate, mismatched, fabricated, and self-reported records do not produce `ALLOW RELEASE`.

## Release decision

- [ ] Regression review and adversarial review found no unresolved Critical or goal-affecting High issue.
- [ ] Required lanes are `PASS` with fresh evidence and adequate confidence.
- [ ] Release is `ALLOW RELEASE` only when all required criteria are proven; otherwise it is `BLOCK`.
- [ ] No Stars, users, downloads, benchmarks, coverage, test results, or runtime behavior are claimed without evidence.
- [ ] Bounded helper output is described as bounded; it is not represented as a complete security, license, vulnerability, provenance, or malware scan.
