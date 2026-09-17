#!/usr/bin/env python3
"""Run the Skill's deterministic release-gate contract evaluation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_LANES = (
    "implementation",
    "architecture",
    "quality",
    "testing",
    "security",
    "privacy",
    "supply_chain",
    "ci_cd",
    "documentation",
    "runtime_verification",
    "regression",
    "adversarial",
)


def decide(snapshot: dict) -> str:
    if not snapshot.get("actual_goal_met") or not snapshot.get("expected_tree"):
        return "BLOCK"
    if snapshot.get("confidence") == "LOW" or not snapshot.get("evidence_fresh"):
        return "BLOCK"
    if snapshot.get("critical_findings", 0) or snapshot.get("high_findings", 0):
        return "BLOCK"
    if any(snapshot.get(lane) != "PASS" for lane in REQUIRED_LANES):
        return "BLOCK"
    return "ALLOW RELEASE"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    cases = (
        ("fixtures/allow.json", "ALLOW RELEASE"),
        ("fixtures/block.json", "BLOCK"),
    )
    failures = 0
    for relative, expected in cases:
        snapshot = load(root / "evals" / relative)
        actual = decide(snapshot)
        result = "PASS" if actual == expected else "FAIL"
        print(f"{result}: {relative}: expected={expected}, actual={actual}")
        if result == "FAIL":
            failures += 1
    if failures:
        return 1
    print("PASS: release-gate behavioral eval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
