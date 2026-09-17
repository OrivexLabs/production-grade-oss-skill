# Contributing

## Scope

Contributions should make the Skill more accurate, reusable, safer, or easier to validate across projects. Keep it generic: do not add private project paths, credentials, environment assumptions, unverifiable popularity claims, or vendor-specific rules without a clear general use case.

## Development

1. Make changes in a branch or isolated working tree.
2. Read `SKILL.md` and the affected checklist/example/eval before editing.
3. Keep instructions decision-useful and avoid adding process that does not improve a release decision.
4. Run the complete local checks from the repository root:

   ```bash
   python3 scripts/check_skill.py .
   python3 scripts/run_eval.py .
   python3 -m unittest discover -s tests -v
   ```

5. Review the diff for secrets, personal data, license issues, generated files, and unexplained behavior changes.

## Pull requests

Describe the user or maintainer outcome, the changed gate lane, evidence from the local checks, and any known limitation. Do not report checks that were not run. Changes to gate semantics should include a fixture or eval update that demonstrates the intended decision.

## License

By contributing, you agree that your contribution is provided under the [Apache-2.0 License](LICENSE), subject to any separate written agreement.
