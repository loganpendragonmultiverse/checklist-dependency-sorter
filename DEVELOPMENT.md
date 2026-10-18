# Development handoff

The public contract is deterministic ordering with explainable failure. Preserve stable source order for otherwise equivalent tasks, identify every missing reference, and report concrete cycle paths. Every feature release must update tests, version metadata, `CHANGELOG.md`, README descriptions and limitations, GitHub release copy, repository metadata, and the Forge catalog together.

Initial verification covers stable ordering, missing dependencies, normalized cycle reporting, JSON/Markdown parsing, and duplicate IDs.

## Version 1.1 dependency layers

Validate chain/diamond/disconnected graphs, duplicate edges, stable within-layer order, missing references and cycles. Preserve default render output; JSON layers are opt-in. Test CLI exit codes and installed-wheel imports. Layers describe declared prerequisites only and never execute tasks or estimate duration.

## 1.1.1 reliability review

Reproduce source/existing-output overwrite, uncaught destination errors, checked Markdown reset, coerced JSON fields and recursion failure on a long ring before fixing them. Preserve ordinary unchecked output and dependency-layer behavior. Checked status is authored data, not a command to skip prerequisites. Cycle paths are deterministic witnesses; enumerating every possible simple cycle is not required.

Run TESTING.md gates and install the built wheel outside the source tree before accepting the commands. Version 1.1.1 is a candidate patch until independent review, protected CI, normal merge and later explicit release/catalog approval. No Gold Star claim is added by this change.
