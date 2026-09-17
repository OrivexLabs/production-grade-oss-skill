import copy
import json
import unittest
from pathlib import Path

from scripts.run_eval import LANES, decide, deep_merge, evaluate, load_case, required_lanes, validate_snapshot


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "fixtures"


def fixture(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def snapshot_fixture(name: str) -> dict:
    return load_case(FIXTURES / name)[1]


class ReleaseGateTests(unittest.TestCase):
    def test_complete_evidence_allows_release(self):
        self.assertEqual(decide(fixture("allow.json")), "ALLOW RELEASE")

    def test_required_na_blocks_release(self):
        result = evaluate(snapshot_fixture("block.json"))
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(any("required lane is not PASS: runtime" in reason for reason in result["reasons"]))

    def test_handwritten_status_without_evidence_cannot_allow(self):
        old_style_snapshot = {
            "actual_goal_met": True,
            "expected_tree": True,
            "testing": "PASS",
            "runtime": "PASS",
            "security": "PASS",
        }
        self.assertEqual(decide(old_style_snapshot), "BLOCK")

    def test_stale_pass_cannot_allow(self):
        snapshot = fixture("allow.json")
        snapshot["evidence"] = [
            {**record, "freshness": "stale"} if record["lane"] == "runtime" else record
            for record in snapshot["evidence"]
        ]
        result = evaluate(snapshot)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(any("runtime: PASS evidence must be fresh" in reason for reason in result["reasons"]))

    def test_na_reason_must_explain_scope(self):
        snapshot = fixture("allow.json")
        for record in snapshot["evidence"]:
            if record["lane"] == "privacy":
                record.update(
                    status="N/A",
                    kind="scope_analysis",
                    result="The check was not run.",
                    reason="not run",
                    freshness="not_applicable",
                )
        self.assertEqual(decide(snapshot), "BLOCK")

    def test_profile_matrix_adds_only_relevant_lanes(self):
        base = fixture("allow.json")
        web = {**base, "project_profile": "web", "risk_profile": "MEDIUM"}
        api = {**base, "project_profile": "api", "risk_profile": "MEDIUM"}
        cli = {**base, "project_profile": "cli", "risk_profile": "MEDIUM", "executable_change": True}
        library = {
            **base,
            "project_profile": "library",
            "risk_profile": "HIGH",
            "non_runnable": True,
        }
        agent_skill = {**base, "project_profile": "ai_agent_skill", "risk_profile": "MEDIUM"}
        self.assertTrue({"runtime", "privacy", "ci_cd"}.issubset(required_lanes(web)))
        self.assertTrue({"runtime", "privacy", "ci_cd"}.issubset(required_lanes(api)))
        self.assertIn("runtime", required_lanes(cli))
        self.assertNotIn("runtime", required_lanes(library))
        self.assertTrue({"runtime", "security", "supply_chain", "adversarial"}.issubset(required_lanes(agent_skill)))

    def test_non_runnable_is_required_for_high_risk_library_runtime_exemption(self):
        snapshot = fixture("allow.json")
        snapshot.update(project_profile="library", risk_profile="HIGH")
        self.assertIn("runtime", required_lanes(snapshot))
        self.assertNotIn("runtime", required_lanes({**snapshot, "non_runnable": True}))

    def test_profile_checks_must_be_structured(self):
        snapshot = fixture("allow.json")
        snapshot["profile_checks"]["checks"] = ["", 42]
        self.assertTrue(any("profile_checks" in error for error in validate_snapshot(snapshot)))
        self.assertEqual(decide(snapshot), "BLOCK")

    def test_adversarial_fixture_expectations(self):
        cases = fixture("adversarial.json")
        self.assertEqual(len(cases), 12)
        for case in cases:
            snapshot = fixture("allow.json")
            result = decide(deep_merge(copy.deepcopy(snapshot), case.get("overrides", {})))
            self.assertEqual(result, case["expected"], case["name"])

    def test_every_known_lane_is_required_in_high_risk_default(self):
        snapshot = fixture("allow.json")
        snapshot.update(risk_profile="HIGH", project_profile="cli")
        self.assertEqual(required_lanes(snapshot), set(LANES))


if __name__ == "__main__":
    unittest.main()
