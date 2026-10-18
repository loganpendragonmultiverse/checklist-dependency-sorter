# Development handoff

The public contract is deterministic ordering with explainable failure. Preserve stable source order for otherwise equivalent tasks, identify every missing reference, and report concrete cycle paths. Every feature release must update tests, version metadata, `CHANGELOG.md`, README descriptions and limitations, GitHub release copy, repository metadata, and the Forge catalog together.

Initial verification covers stable ordering, missing dependencies, normalized cycle reporting, JSON/Markdown parsing, and duplicate IDs.

## Version 1.1 dependency layers

Validate chain/diamond/disconnected graphs, duplicate edges, stable within-layer order, missing references and cycles. Preserve default render output; JSON layers are opt-in. Test CLI exit codes and installed-wheel imports. Layers describe declared prerequisites only and never execute tasks or estimate duration.

## 1.1.1 reliability review — 2026-10-18

The October 18 review reproduced source/existing-output overwrite, uncaught destination errors, checked Markdown reset, coerced JSON fields and recursion failure on a long ring. Version 1.1.1 repairs those cases while preserving ordinary unchecked output and dependency-layer behavior. Checked status is authored data, not a command to skip prerequisites. Cycle paths are deterministic witnesses; enumerating every possible simple cycle is not required.

Acceptance on October 18: all 34 tests passed on each local Python 3.12, 3.13 and 3.14 runtime. Protected CI passed Linux, Windows and macOS with Python 3.10 and 3.13, including the Windows dangling-symlink regression. The wheel and source distribution were installed separately outside the source tree; each passed 34 tests, ten full-workflow calls and two real entry-point calls.

Run TESTING.md gates for maintenance changes. Release builds use the tag workflow; verify the actual tagged artifacts and their hashes before publication.
