# Evidence Schema

The Release Gate consumes evidence records, not prose statuses. The following JSON shape is the minimum record for every lane:

```json
{
  "lane": "runtime",
  "status": "PASS",
  "kind": "runtime_observation",
  "source": "runtime://isolated-run/42",
  "method": "invoke the command with a fresh fixture and inspect the output file",
  "timestamp": "2026-01-01T00:00:00Z",
  "commit_sha": "0123456789012345678901234567890123456789",
  "tree_sha": "1234567890123456789012345678901234567890",
  "result": "command exited 0 and the independently inspected output contains the expected record",
  "confidence": "HIGH",
  "freshness": "fresh"
}
```

## Required fields

| Field | Rule |
| --- | --- |
| `lane` | One known lane, exactly once per snapshot. |
| `status` | `PASS`, `FAIL`, `BLOCKED`, or `N/A`. |
| `kind` | Evidence type such as `command`, `ci_run`, `runtime_observation`, `manual_review`, `scope_analysis`, or `adversarial_review`. `self_report` is never valid for `PASS`. |
| `source` | Independent source: command output, CI run, runtime observation, diff review, scanner, or boundary test. |
| `method` | Exact command or review/runtime method; “checked” is insufficient. |
| `timestamp` | ISO-8601 timestamp with timezone. |
| `commit_sha` / `tree_sha` | Full 40-character Git SHAs for the reviewed snapshot. A `PASS` cannot use a missing or mismatched identity. |
| `result` | Concrete observation, not only `PASS`, `OK`, or `success`. |
| `confidence` | `HIGH`, `MEDIUM`, or `LOW`; a release-critical `PASS` cannot be `LOW`. |
| `freshness` | `fresh`, `stale`, `unknown`, or `not_applicable`; a `PASS` must be `fresh`. |

## `N/A` rule

`N/A` is a scoped applicability result, not a skipped check. It must include a `reason` field and a concrete statement of why the lane does not apply. The reason must not be only `N/A`, `not run`, `unknown`, or `not needed`. A required lane with `N/A` remains `BLOCK`; profile exemptions are computed before evaluation.

Example:

```json
{
  "lane": "runtime",
  "status": "N/A",
  "kind": "scope_analysis",
  "source": "review://project-profile",
  "method": "inspect package type and changed surface",
  "timestamp": "2026-01-01T00:00:00Z",
  "commit_sha": "0123456789012345678901234567890123456789",
  "tree_sha": "1234567890123456789012345678901234567890",
  "result": "No standalone process exists for this Library-only API change.",
  "reason": "Runtime is not applicable: consumer behavior is covered by package compatibility tests.",
  "confidence": "HIGH",
  "freshness": "not_applicable"
}
```

## Trust and limits

The schema proves attribution and freshness, not truth by itself. Evidence must still be independently reviewed. A static “no findings” claim is not a complete security scan; a CI file is not a CI run; a test result is not runtime proof. The package helper reports only bounded pattern and workflow checks and must state that boundary.
