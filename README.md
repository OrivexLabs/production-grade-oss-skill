# production-grade-oss

`production-grade-oss` is a general-purpose Codex Skill for applying a production-grade open-source engineering and release gate to new, changed, refactored, reviewed, and released projects.

It keeps the important distinction between **code exists**, **tests pass**, **the real user path works**, and **the release is safe to publish**. It does not grant permissions, replace project-specific policy, or justify unnecessary engineering.

## Install

Clone the repository, then place the Skill directory in the active Codex skills directory:

```bash
git clone https://github.com/OrivexLabs/production-grade-oss-skill.git
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/production-grade-oss"
mkdir -p "$(dirname "$skill_dir")"
cp -R production-grade-oss-skill "$skill_dir"
```

If the destination already exists, inspect its Skill identity and commit first. Update only that destination when it is the same Skill; do not overwrite an unrelated Skill.

## Call

The Skill is configured for implicit discovery. It can also be invoked explicitly:

```text
$production-grade-oss
```

Example prompt:

```text
Use $production-grade-oss to review this change, run the applicable checks, verify the real user path, and make an evidence-based release-gate decision. Do not claim tests or runtime results that were not run.
```

## Rules

The Skill requires an observable goal contract and risk-appropriate evidence for:

- architecture and data/control-flow boundaries;
- code quality, compatibility, error handling, and maintainability;
- tests that cover the affected behavior and safe failure paths;
- security threat boundaries, least privilege, and secret handling;
- privacy minimization, retention, redaction, and user control;
- dependency provenance, locks, licenses, integrity, and maintenance;
- reproducible least-privilege CI/CD and exact release artifacts;
- truthful `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and changelog/release notes;
- runtime verification using fresh inputs and independent observations;
- regression and adversarial review before an important release decision.

### Risk and project profiles

Every decision records one risk profile and one project profile:

- **Risk:** `LOW`, `MEDIUM`, or `HIGH`. The level controls the required lanes; it is based on impact and trust boundaries, not line count.
- **Project:** `Web`, `API`, `CLI`, `Library`, or `AI Agent / Skill`. The profile adds the relevant runtime, compatibility, browser, protocol, filesystem, prompt, tool, or discovery checks.

The evaluator does not mechanically require every lane for every project. Optional lanes may be `N/A` only with a specific scope reason. A required lane cannot use `N/A`, except for the explicit non-runnable Library Runtime exemption. A check that ran and failed remains `FAIL` or `BLOCKED`.

### Evidence and gate semantics

Each known lane has exactly one structured record. A `PASS` must include an attributable source, exact command/method, timezone-qualified timestamp, matching full commit/tree SHA, concrete result, confidence, and freshness. A README sentence, a workflow file, a green test claim, or a handwritten `PASS` is not evidence. See [references/evidence-schema.md](references/evidence-schema.md).

`ALLOW RELEASE` is reserved for a goal that is actually proven. Missing or invalid evidence, unresolved Critical/High findings, secret or privacy exposure, incompatible licensing, unexplained breaking changes, unexpected release state, or fabricated claims produce `BLOCK`.

The Skill explicitly rejects “能跑就算完成” / “it runs, so it is done”, meaningless engineering, and invented Stars, users, downloads, benchmarks, coverage, or test results.

## Repository layout

```text
SKILL.md                         Codex instructions and Release Gate
examples/                         Reusable request and report examples
checklists/                       Compact human-review checklist
references/                       Evidence schema and risk/profile matrix
evals/                            Gate fixtures, rubric, and dry-run harness
scripts/check_skill.py            Structure, Markdown, and secret checks
scripts/run_eval.py               Deterministic behavioral gate eval
.github/workflows/ci.yml          Clean-checkout CI
```

## Validate locally

No third-party runtime dependency is required for the repository checks:

```bash
python3 scripts/check_skill.py .
python3 scripts/run_eval.py .
python3 -m unittest discover -s tests -v
```

These checks validate the package and the gate contract. They are not a substitute for applying the Skill to the target project's real runtime and release environment.

The repository checks are deliberately bounded. The helper detects selected credential patterns, personal paths, literal IPv4 addresses, sensitive filenames, mutable workflow action references, and remote-shell patterns. It is **not** a complete secret scanner, dependency vulnerability database, license classifier, provenance verifier, or malware detector. Use dedicated tools and independent review for those claims.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and local checks. See [SECURITY.md](SECURITY.md) for private vulnerability reporting. This repository is licensed under [Apache-2.0](LICENSE).
