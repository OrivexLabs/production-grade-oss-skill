#!/usr/bin/env python3
"""Evaluate the Skill's risk/profile-aware, evidence-backed release gate."""

from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path


LANES = (
    "architecture",
    "quality",
    "testing",
    "security",
    "privacy",
    "supply_chain",
    "ci_cd",
    "documentation",
    "runtime",
    "regression",
    "adversarial",
)
STATUSES = {"PASS", "FAIL", "BLOCKED", "N/A"}
RISKS = {"LOW", "MEDIUM", "HIGH"}
PROFILES = {"web", "api", "cli", "library", "ai_agent_skill"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ISO_RE = re.compile(r"T.*(?:Z|[+-][0-9]{2}:[0-9]{2})$")

LOW_BASELINE = {"architecture", "quality", "testing", "documentation"}
MEDIUM_BASELINE = {
    "architecture",
    "quality",
    "testing",
    "security",
    "supply_chain",
    "documentation",
    "regression",
}
HIGH_BASELINE = set(LANES)

VALID_KINDS = {
    "adversarial_review",
    "boundary_test",
    "browser_e2e",
    "ci_run",
    "codex_dry_run",
    "command",
    "dependency_audit",
    "eval_fixture",
    "manual_review",
    "package_compat",
    "privacy_review",
    "runtime_observation",
    "scanner",
    "scope_analysis",
}
REQUIRED_RECORD_FIELDS = (
    "lane",
    "status",
    "kind",
    "source",
    "method",
    "timestamp",
    "commit_sha",
    "tree_sha",
    "result",
    "confidence",
    "freshness",
)
RUNTIME_KINDS = {"runtime_observation", "browser_e2e", "codex_dry_run", "boundary_test"}


def deep_merge(base: dict, overrides: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if key == "evidence" and isinstance(value, dict) and isinstance(result.get(key), list):
            records = {record.get("lane"): record for record in result[key] if isinstance(record, dict)}
            for lane, record_override in value.items():
                if isinstance(record_override, dict) and isinstance(records.get(lane), dict):
                    records[lane] = deep_merge(records[lane], record_override)
                else:
                    records[lane] = copy.deepcopy(record_override)
            result[key] = [records.get(lane) for lane in LANES if lane in records]
            continue
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def required_lanes(snapshot: dict) -> set[str]:
    risk = snapshot["risk_profile"]
    profile = snapshot["project_profile"]
    if risk == "LOW":
        required = set(LOW_BASELINE)
    elif risk == "MEDIUM":
        required = set(MEDIUM_BASELINE)
    else:
        required = set(HIGH_BASELINE)

    if risk in {"MEDIUM", "HIGH"} and profile in {"web", "api"}:
        required.update({"runtime", "privacy", "ci_cd"})
    if risk in {"MEDIUM", "HIGH"} and profile == "cli" and snapshot.get("executable_change", True):
        required.add("runtime")
    if risk in {"MEDIUM", "HIGH"} and profile == "ai_agent_skill":
        required.update({"runtime", "security", "supply_chain", "adversarial"})

    if profile == "library" and snapshot.get("non_runnable") is True:
        required.discard("runtime")

    if snapshot.get("runtime_surface_changed"):
        required.add("runtime")
    if snapshot.get("security_surface_changed"):
        required.add("security")
    if snapshot.get("privacy_surface_changed"):
        required.add("privacy")
    if snapshot.get("dependency_changed"):
        required.add("supply_chain")
    if snapshot.get("release_automation_changed"):
        required.add("ci_cd")
    return required


def _nonempty(record: dict, key: str) -> bool:
    return isinstance(record.get(key), str) and bool(record[key].strip())


def validate_record(record: dict, lane: str, snapshot: dict) -> list[str]:
    errors: list[str] = []
    missing = [key for key in REQUIRED_RECORD_FIELDS if key not in record]
    if missing:
        errors.append(f"{lane}: missing evidence fields: {', '.join(missing)}")
        return errors
    if record.get("lane") != lane:
        errors.append(f"{lane}: evidence lane identity mismatch")
    status = record.get("status")
    if status not in STATUSES:
        errors.append(f"{lane}: invalid status")
    if record.get("kind") not in VALID_KINDS:
        errors.append(f"{lane}: invalid evidence kind")
    for key in ("source", "method", "result"):
        if not _nonempty(record, key):
            errors.append(f"{lane}: {key} must be concrete")
    for key in ("commit_sha", "tree_sha"):
        if not isinstance(record.get(key), str) or not SHA_RE.fullmatch(record[key]):
            errors.append(f"{lane}: {key} must be a full 40-character SHA")
        elif record[key] != snapshot.get(key):
            errors.append(f"{lane}: {key} does not match the reviewed snapshot")
    timestamp = record.get("timestamp")
    if not isinstance(timestamp, str) or not ISO_RE.search(timestamp):
        errors.append(f"{lane}: timestamp must be timezone-qualified ISO-8601")
    else:
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{lane}: timestamp is not parseable ISO-8601")
    if record.get("confidence") not in {"HIGH", "MEDIUM", "LOW"}:
        errors.append(f"{lane}: invalid confidence")
    if record.get("freshness") not in {"fresh", "stale", "unknown", "not_applicable"}:
        errors.append(f"{lane}: invalid freshness")

    if status == "PASS":
        if record.get("freshness") != "fresh":
            errors.append(f"{lane}: PASS evidence must be fresh")
        if record.get("confidence") == "LOW":
            errors.append(f"{lane}: PASS evidence cannot have LOW confidence")
        if record.get("kind") not in VALID_KINDS - {"manual_review"}:
            pass
        if record.get("kind") == "manual_review" and record.get("source", "").startswith("claim://"):
            errors.append(f"{lane}: self-reported claim cannot be PASS evidence")
        if record.get("result", "").strip().upper() in {"PASS", "OK", "SUCCESS", "TRUE"}:
            errors.append(f"{lane}: result must describe an observation, not only a status")
        if lane == "ci_cd":
            source = record.get("source", "")
            method = record.get("method", "").lower()
            result = record.get("result", "").lower()
            if record.get("kind") != "ci_run" or not ("run" in source and ("ci://" in source or "http" in source)):
                errors.append("ci_cd: PASS requires an attributable CI run source")
            if "clean checkout" not in method or "success" not in result:
                errors.append("ci_cd: PASS requires clean-checkout method and successful result")
        if lane == "runtime" and record.get("kind") not in RUNTIME_KINDS:
            errors.append("runtime: PASS requires real runtime or dry-run evidence")
    elif status == "N/A":
        reason = record.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            errors.append(f"{lane}: N/A requires a specific scope reason")
        else:
            lowered = reason.lower()
            if lowered.strip() in {"n/a", "not run", "unknown", "not needed", "skip"}:
                errors.append(f"{lane}: N/A reason is evasive")
            if "not run" in lowered and not any(
                phrase in lowered for phrase in ("not applicable", "not in scope", "non-runnable")
            ):
                errors.append(f"{lane}: N/A cannot hide a check that was merely not run")
        if record.get("kind") != "scope_analysis":
            errors.append(f"{lane}: N/A must use scope_analysis evidence")
        if record.get("freshness") != "not_applicable":
            errors.append(f"{lane}: N/A must use not_applicable freshness")
    return errors


def validate_snapshot(snapshot: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "project_profile",
        "risk_profile",
        "actual_goal_met",
        "expected_tree",
        "commit_sha",
        "tree_sha",
        "evidence",
        "findings",
        "profile_checks",
    }
    missing = sorted(required - snapshot.keys())
    if missing:
        return [f"snapshot missing fields: {', '.join(missing)}"]
    if snapshot["schema_version"] != 1:
        errors.append("unsupported evidence schema version")
    if snapshot["project_profile"] not in PROFILES:
        errors.append("invalid project profile")
    if snapshot["risk_profile"] not in RISKS:
        errors.append("invalid risk profile")
    for key in ("commit_sha", "tree_sha"):
        if not isinstance(snapshot[key], str) or not SHA_RE.fullmatch(snapshot[key]):
            errors.append(f"snapshot {key} must be a full 40-character SHA")
    if not isinstance(snapshot["actual_goal_met"], bool) or not isinstance(snapshot["expected_tree"], bool):
        errors.append("goal/tree fields must be boolean")
    profile_checks = snapshot["profile_checks"]
    if not isinstance(profile_checks, dict) or profile_checks.get("profile") != snapshot["project_profile"]:
        errors.append("profile_checks must identify the selected project profile")
    elif (
        not isinstance(profile_checks.get("checks"), list)
        or not profile_checks["checks"]
        or not all(isinstance(item, str) and item.strip() for item in profile_checks["checks"])
    ):
        errors.append("profile_checks must contain concrete focus checks")
    evidence = snapshot["evidence"]
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        return errors
    by_lane: dict[str, dict] = {}
    for record in evidence:
        if not isinstance(record, dict):
            errors.append("evidence entries must be objects")
            continue
        lane = record.get("lane")
        if lane in by_lane:
            errors.append(f"duplicate evidence lane: {lane}")
        by_lane[lane] = record
    if set(by_lane) != set(LANES):
        errors.append("evidence must contain exactly one record for every known lane")
    for lane in LANES:
        if lane in by_lane:
            errors.extend(validate_record(by_lane[lane], lane, snapshot))
    if not isinstance(snapshot["findings"], list):
        errors.append("findings must be a list")
    else:
        for index, finding in enumerate(snapshot["findings"]):
            if not isinstance(finding, dict) or finding.get("severity") not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                errors.append(f"finding {index} has invalid severity")
    return errors


def evaluate(snapshot: dict) -> dict:
    errors = validate_snapshot(snapshot)
    reasons = list(errors)
    required = required_lanes(snapshot) if not errors or snapshot.get("risk_profile") in RISKS and snapshot.get("project_profile") in PROFILES else set()
    records = {record.get("lane"): record for record in snapshot.get("evidence", []) if isinstance(record, dict)}
    if snapshot.get("actual_goal_met") is not True:
        reasons.append("actual goal is not proven")
    if snapshot.get("expected_tree") is not True:
        reasons.append("reviewed tree is dirty or unexpected")
    for lane in required:
        if records.get(lane, {}).get("status") != "PASS":
            reasons.append(f"required lane is not PASS: {lane}")
    for lane in set(LANES) - required:
        if records.get(lane, {}).get("status") in {"FAIL", "BLOCKED"}:
            reasons.append(f"optional lane reported failure: {lane}")
    for index, finding in enumerate(snapshot.get("findings", [])):
        if not isinstance(finding, dict):
            continue
        severity = finding.get("severity")
        if severity in {"CRITICAL", "HIGH"} or (severity == "MEDIUM" and finding.get("blocking") is True):
            reasons.append(f"blocking finding {index}: {severity}")
    return {
        "decision": "ALLOW RELEASE" if not reasons else "BLOCK",
        "reasons": reasons,
        "required_lanes": sorted(required),
        "na_lanes": sorted(lane for lane in LANES if records.get(lane, {}).get("status") == "N/A"),
    }


def decide(snapshot: dict) -> str:
    """Compatibility helper used by tests and small integrations."""
    return evaluate(snapshot)["decision"]


def load_json(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_case(path: Path) -> tuple[str, dict]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"case must be an object: {path}")
    expected = data.get("expected")
    if "base" in data:
        base = load_json(path.parent / data["base"])
        if not isinstance(base, dict):
            raise ValueError(f"base fixture must be an object: {path}")
        snapshot = deep_merge(base, data.get("overrides", {}))
    else:
        snapshot = data
    if expected not in {"ALLOW RELEASE", "BLOCK"}:
        expected = "ALLOW RELEASE" if path.name == "allow.json" else "BLOCK"
    return expected, snapshot


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    fixtures = root / "evals" / "fixtures"
    cases: list[tuple[str, str, dict]] = []
    for filename, default_expected in (("allow.json", "ALLOW RELEASE"), ("block.json", "BLOCK")):
        expected, snapshot = load_case(fixtures / filename)
        cases.append((filename, expected or default_expected, snapshot))
    adversarial = load_json(fixtures / "adversarial.json")
    if not isinstance(adversarial, list):
        print("FAIL: adversarial.json must contain a list")
        return 1
    base = load_json(fixtures / "allow.json")
    if not isinstance(base, dict):
        print("FAIL: allow fixture must be an object")
        return 1
    for case in adversarial:
        if not isinstance(case, dict) or not isinstance(case.get("name"), str):
            print("FAIL: malformed adversarial case")
            return 1
        cases.append((f"adversarial/{case['name']}", case.get("expected"), deep_merge(base, case.get("overrides", {}))))

    failures = []
    false_allow = []
    false_block = []
    for name, expected, snapshot in cases:
        result = evaluate(snapshot)
        actual = result["decision"]
        print(f"{'PASS' if actual == expected else 'FAIL'}: {name}: expected={expected}, actual={actual}")
        if actual != expected:
            failures.append(name)
        if expected == "BLOCK" and actual == "ALLOW RELEASE":
            false_allow.append(name)
        if expected == "ALLOW RELEASE" and actual == "BLOCK":
            false_block.append(name)
    print(
        f"Summary: total={len(cases)}, adversarial={len(adversarial)}, "
        f"false_allow={len(false_allow)}, false_block={len(false_block)}"
    )
    if failures:
        print("Mismatches: " + ", ".join(failures))
        return 1
    print("PASS: risk/profile/evidence release-gate eval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
