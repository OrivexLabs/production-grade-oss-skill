#!/usr/bin/env python3
"""Validate the production-grade-oss Skill package without third-party code."""

from __future__ import annotations

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
    "evals/README.md",
    "evals/dry-run.md",
    "evals/fixtures/allow.json",
    "evals/fixtures/block.json",
    ".github/workflows/ci.yml",
)
REQUIRED_DIRS = ("examples", "checklists", "evals", ".github/workflows")
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
    "no fake metrics": ("stars", "downloads", "do not invent"),
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|gho|github_pat|xoxb|xoxp)-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)://[^/\s:@]+:[^@\s]+@"),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+(?:/|$)"),
    re.compile(r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}(?![\d.])"),
)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def check_frontmatter(root: Path, failures: list[str]) -> None:
    path = root / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md does not start with YAML frontmatter", failures)
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        fail("SKILL.md frontmatter is not closed", failures)
        return
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
        if not text.endswith("\n"):
            fail(f"Markdown file lacks a final newline: {path.relative_to(root)}", failures)
        for line_number, line in enumerate(text.splitlines(), 1):
            if "\t" in line:
                fail(f"Markdown contains a tab: {path.relative_to(root)}:{line_number}", failures)
            if line.rstrip() != line:
                fail(f"Markdown has trailing whitespace: {path.relative_to(root)}:{line_number}", failures)
        headings = [line for line in text.splitlines() if line.startswith("#")]
        for heading in headings:
            if not re.match(r"^#{1,6}(?:\s|$)", heading):
                fail(f"Malformed Markdown heading: {path.relative_to(root)}:{heading}", failures)


def check_secrets(root: Path, failures: list[str]) -> None:
    ignored_parts = {".git", "__pycache__"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                fail(f"possible secret, IP, or personal path in {path.relative_to(root)}", failures)
                break


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
    check_secrets(root, failures)
    if failures:
        print(f"\n{len(failures)} validation failure(s)")
        return 1
    print("PASS: Skill structure, Markdown hygiene, and secret scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
