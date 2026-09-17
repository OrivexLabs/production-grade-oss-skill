# Example: feature change request

## Request

> Add an export option to an existing command-line tool. Use the project's current format library if it already supports the requested output. Preserve existing output and fail safely when the destination is not writable.

## How to apply the Skill

1. State the actual goal: a user can export the requested data without changing existing output behavior.
2. Inspect current commands, output contracts, dependencies, tests, permissions, and Git status.
3. Review the architecture and blast radius before choosing an implementation.
4. Add tests for valid output, empty input, invalid options, unwritable destination, and compatibility.
5. Run the real command against a temporary fixture and independently inspect the output file and failure behavior.
6. Run security, privacy, dependency, documentation, and regression checks that apply.
7. Return `ALLOW RELEASE` only if the evidence closes the goal; otherwise return `BLOCK` with the missing proof.

## False positives to avoid

- A unit test that never invokes the command is not runtime verification.
- A successful return code without checking the output contents is not export proof.
- Adding a second format library without checking the existing dependency is not automatically production-grade.
