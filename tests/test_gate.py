import json
import unittest
from pathlib import Path

from scripts.run_eval import decide


ROOT = Path(__file__).resolve().parents[1]


class ReleaseGateContractTests(unittest.TestCase):
    def test_complete_fresh_evidence_allows_release(self):
        snapshot = json.loads((ROOT / "evals/fixtures/allow.json").read_text())
        self.assertEqual(decide(snapshot), "ALLOW RELEASE")

    def test_green_tests_without_runtime_and_security_blocks(self):
        snapshot = json.loads((ROOT / "evals/fixtures/block.json").read_text())
        self.assertEqual(snapshot["testing"], "PASS")
        self.assertEqual(decide(snapshot), "BLOCK")

    def test_low_confidence_blocks_even_when_lanes_pass(self):
        snapshot = json.loads((ROOT / "evals/fixtures/allow.json").read_text())
        snapshot["confidence"] = "LOW"
        self.assertEqual(decide(snapshot), "BLOCK")


if __name__ == "__main__":
    unittest.main()
