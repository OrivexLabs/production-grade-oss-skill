# Example release-gate report

Use this as a shape, replacing every placeholder with current evidence.

```text
Goal / Risk Level: Publish the requested version from the reviewed tree / R2
Implementation: PASS — <test command and result>
Runtime Verification: PASS|FAIL|N/A — <fresh input, actual path, independent observation>
Architecture / Quality / Testing: PASS|FAIL|N/A — <review and test evidence>
Security / Privacy / Supply Chain: PASS|FAIL — <scan, dependency, license evidence>
CI/CD / Documentation: PASS — <clean-checkout CI and docs evidence>
Regression / Adversarial Review: PASS|FAIL — <blast-radius and red-team evidence>
Release Gate: ALLOW RELEASE|BLOCK — <one-sentence reason>
Confidence: HIGH|MEDIUM|LOW
Known Limitations: <explicit limitation, or none>
Evidence Path: <repository-local evidence path or command log>
Production Changed: NO
```

Never replace an unavailable result with a claim of success. Use `BLOCK` when the missing evidence affects a required lane or the actual release goal.
