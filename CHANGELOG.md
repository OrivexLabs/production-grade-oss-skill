# Changelog

All notable changes to this Skill are documented here.

The format follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers follow Semantic Versioning where a versioned release is made.

## [0.2.0] - 2026-09-17

### Added

- Initial public Skill for production-grade open-source engineering and release gates.
- Checklists, examples, deterministic eval fixtures, and repository validation scripts.
- CI checks for structure, Markdown hygiene, secret patterns, unit tests, and the gate eval.

### Changed

- Added explicit LOW/MEDIUM/HIGH Risk Profiles and Web/API/CLI/Library/AI Agent / Skill Project Profiles.
- Replaced handwritten lane statuses with a versioned, commit/tree-bound Evidence Schema.
- Made scoped `N/A` valid only for optional lanes or an explicit non-runnable Library Runtime exemption.
- Added bounded secret and workflow supply-chain checks with stated limitations.
- Added 12 adversarial evals, including positive low-risk `N/A` control coverage and negative false-ALLOW cases.
