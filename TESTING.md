# Testing

Use Python 3.10 or newer in an isolated environment.

```bash
python -m pip install -e . pytest build
python -m pytest
python -m build
```

CI runs the suite and builds on Linux, Windows and macOS with Python 3.10 and 3.13. The release workflow builds wheel and source distributions from a tag; no local build or passing test publishes anything.

## 1.1.1 acceptance

Verify ordinary stable ordering/layers and existing missing/cycle exit codes. Attempt an input-as-output, an existing report, a symlink and a missing output directory: source/existing files must stay unchanged and errors return 2 without a traceback. Permission-error behavior uses a synthetic injected failure and should also receive a real unprivileged filesystem smoke test where possible.

Read checked Markdown, sort it into Markdown/text/JSON/DOT and verify completion survives; JSON boolean completion must be validated. Completion never skips task dependencies. Reject non-string or blank IDs/text/dependencies instead of coercing them. Sort a 2,000-node directed cycle and a dependent tail without RecursionError; reported paths must follow real declared edges. Verify separate and overlapping cycle witnesses, duplicate-ID rejection and multiline DOT escaping.

Install the built wheel into a fresh environment outside the checkout. Exercise the CLI's Markdown/JSON/layers/DOT success paths, malformed-input exit 2, invalid-graph exit 1 and source/output protection. Keep synthetic inputs unchanged. Source distributions and wheels must carry the same package/version. Physical Graphviz rendering is optional; DOT is graph source, not an image.

The sorter does not execute tasks, estimate durations, enumerate all simple cycles, or make a multi-file/power-loss transaction. Reports are not lossless backups. Retain source files and inspect any partial new output after a write failure.
