# Risk and Project Profile Matrix

Use this matrix to select the smallest sufficient gate. All lanes are classified, but only required lanes must be `PASS`.

## Risk baseline

| Risk | Required baseline lanes | Typical optional lanes |
| --- | --- | --- |
| LOW | Architecture, Code Quality, Testing, Documentation | Security, Privacy, Supply Chain, CI/CD, Runtime, Regression, Adversarial |
| MEDIUM | Architecture, Code Quality, Testing, Security, Supply Chain, Documentation, Regression | Privacy, CI/CD, Runtime, Adversarial unless profile adds them |
| HIGH | All lanes | Runtime may be justified `N/A` only for a non-runnable Library with consumer evidence |

Any changed surface can promote its lane to required at LOW risk: runtime, security, privacy, dependencies, or release automation. If risk or applicability is uncertain, do not use `N/A` to make the uncertainty disappear.

## Profile focus

| Profile | Required focus when applicable |
| --- | --- |
| Web | Browser/runtime freshness, XSS/CSRF/CORS, session/auth, accessibility/responsive behavior, network failure, privacy/telemetry |
| API | Authn/authz, input/schema validation, rate/resource limits, idempotency/replay, error contracts, persistence/migrations, observability |
| CLI | Args/exit streams, sensitive output, filesystem/path/shell boundaries, permissions, portability, packaging/install, actual invocation |
| Library | Public API/semantic compatibility, consumer-visible behavior, package contents, deterministic tests, dependency/license surface |
| AI Agent / Skill | Instruction precedence, prompt injection, malicious repository text, conflicting instructions, tool/permission boundaries, secret safety, discovery metadata, real dry-run |

## Profile adjustments

- Web and API at MEDIUM/HIGH require Runtime, Privacy, and CI/CD because their user and deployment boundaries are part of the goal.
- Executable CLI changes at MEDIUM/HIGH require Runtime; a documentation-only CLI change can keep Runtime `N/A` at LOW with a reason.
- A Library may use Runtime `N/A` when it has no standalone process, but compatibility/package tests and Supply Chain evidence remain the proof.
- AI Agent / Skill behavior changes require a real dry-run plus prompt-injection/conflicting-instruction checks; at MEDIUM/HIGH they also require Security, Supply Chain, and Adversarial evidence.

The exact evaluator implementation is intentionally small and deterministic in `scripts/run_eval.py`; it is a contract check, not an AI or security scanner.
