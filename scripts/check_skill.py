#!/usr/bin/env python3
"""Run bounded package, schema, Markdown, secret, and workflow checks.

This is not a complete secret scanner, dependency vulnerability scanner, license
classifier, provenance verifier, or malware detector. It only checks the
patterns and workflow invariants implemented below.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "agents/openai.yaml",
    "scripts/check_skill.py",
    "scripts/run_eval.py",
    "examples/feature-change-request.md",
    "examples/release-gate-report.md",
    "checklists/project-gate.md",
    "references/evidence-schema.md",
    "references/risk-project-profile.md",
    "evals/README.md",
    "evals/dry-run.md",
    "evals/fixtures/allow.json",
    "evals/fixtures/block.json",
    "evals/fixtures/adversarial.json",
    ".github/workflows/ci.yml",
)
REQUIRED_DIRS = ("examples", "checklists", "references", "evals", ".github/workflows")
REQUIRED_TERMS = {
    "architecture": ("architecture",),
    "code quality": ("code quality",),
    "testing": ("testing",),
    "security": ("security",),
    "privacy": ("privacy",),
    "dependency / supply chain": ("dependency", "supply chain"),
    "ci/cd": ("ci/cd",),
    "release gate": ("release gate",),
    "runtime verification": ("runtime verification",),
    "risk profile": ("risk profile", "low", "medium", "high"),
    "project profile": ("project profile", "web", "api", "cli", "library", "ai agent / skill"),
    "evidence schema": ("evidence", "commit_sha", "tree_sha", "confidence", "freshness"),
    "no fake metrics": ("stars", "downloads", "do not invent"),
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|gho|github_pat|xoxb|xoxp)-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)://[^/\s:@]+:[^@\s]+@"),
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{16,}"),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+(?:/|$)"),
    re.compile(r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}(?![\d.])"),
)
SENSITIVE_FILENAMES = re.compile(r"(^|/)(\.env(?:\..*)?|.*\.(?:pem|key|p12|pfx|mobileprovision)|credentials(?:\..*)?)$", re.IGNORECASE)
IMMUTABLE_ACTION = re.compile(r"^\s*uses:\s*[^\s@]+@([0-9a-f]{40})\s*$")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def check_frontmatter(root: Path, failures: list[str]) -> None:
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail("SKILL.md frontmatter is missing or unclosed", failures)
        return
    end = text.find("\n---\n", 4)
    frontmatter = text[4:end]
    name = re.search(r"^name:\s*([^\n]+)$", frontmatter, re.MULTILINE)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name or name.group(1).strip() != "production-grade-oss":
        fail("SKILL.md name is not production-grade-oss", failures)
    if not description or "TODO" in description.group(1):
        fail("SKILL.md description is missing or unfinished", failures)
    lowered = text.lower()
    for label, terms in REQUIRED_TERMS.items():
        if not all(term in lowered for term in terms):
            fail(f"SKILL.md is missing required coverage: {label}", failures)


def check_markdown(root: Path, failures: list[str]) -> None:
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        if not text.endswith("\n"):
            fail(f"Markdown file lacks a final newline: {relative}", failures)
        for line_number, line in enumerate(text.splitlines(), 1):
            if "\t" in line:
                fail(f"Markdown contains a tab: {relative}:{line_number}", failures)
            if line.rstrip() != line:
                fail(f"Markdown has trailing whitespace: {relative}:{line_number}", failures)
        for heading in (line for line in text.splitlines() if line.startswith("#")):
            if not re.match(r"^#{1,6}(?:\s|$)", heading):
                fail(f"Malformed Markdown heading: {relative}:{heading}", failures)


def check_json(root: Path, failures: list[str]) -> None:
    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            fail(f"invalid JSON: {path.relative_to(root)}:{error.lineno}", failures)


def check_secrets(root: Path, failures: list[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or ".evidence" in path.parts:
            continue
        relative = str(path.relative_to(root))
        if SENSITIVE_FILENAMES.search(relative):
            fail(f"sensitive filename is not allowed in package: {relative}", failures)
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                fail(f"bounded secret/IP/personal-path scan matched {relative}", failures)
                break


def check_workflow(root: Path, failures: list[str]) -> None:
    workflow_dir = root / ".github" / "workflows"
    for path in sorted(workflow_dir.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), 1):
            if "uses:" in line and not IMMUTABLE_ACTION.match(line):
                fail(f"workflow action is not pinned to an immutable SHA: {path.relative_to(root)}:{line_number}", failures)
            if re.search(r"(?i)(curl|wget)[^\n|]*\|\s*(sh|bash)", line):
                fail(f"workflow contains remote-shell execution: {path.relative_to(root)}:{line_number}", failures)
        if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s+read\s*$", text):
            fail(f"workflow lacks least-privilege contents: read permissions: {path.relative_to(root)}", failures)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            fail(f"missing required file: {relative}", failures)
    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            fail(f"missing required directory: {relative}", failures)
    if (root / "SKILL.md").is_file():
        check_frontmatter(root, failures)
    check_markdown(root, failures)
    check_json(root, failures)
    check_secrets(root, failures)
    check_workflow(root, failures)
    if failures:
        print(f"\n{len(failures)} validation failure(s)")
        return 1
    print("PASS: structure, Markdown, JSON, bounded secret/IP scan, and workflow supply-chain checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
