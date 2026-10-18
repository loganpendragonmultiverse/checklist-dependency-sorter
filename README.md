# Checklist Dependency Sorter

Checklist Dependency Sorter turns an unordered task list into a stable, dependency-respecting sequence. It also names missing task references and prints concrete cycle paths instead of returning a vague sorting error.

## Install

Python 3.10 or newer is required.

```bash
python -m venv .venv
# Activate .venv with your shell, then:
python -m pip install -e .
```

## Three-minute use

Markdown input:

```markdown
- [ ] draft: Write the draft
- [ ] test: Test the commands | after: draft
- [ ] release: Publish the release | after: test
```

Sort it or export a graph:

```bash
checklist-sort tasks.md
checklist-sort tasks.json --format markdown --output ordered.md
checklist-sort tasks.json --format dot --output dependencies.dot
```

JSON may be an array or an object with a `tasks` array. Each task needs nonblank string `id` and `text` fields and an optional array of nonblank strings named `depends_on`. JSON may include a boolean `completed` field; omitted means false. Markdown accepts `[ ]`, `[x]` and `[X]`. Checked tasks remain checked in reports; completion does not remove tasks or bypass prerequisites.

## Output and limitations

- Independent tasks retain their source order whenever dependency rules allow it.
- Missing dependencies and cycles produce exit code 1; malformed input and file I/O errors produce exit code 2.
- `--output` creates a new file only. Existing files, the source input and symlink destinations are refused; choose a new output name. A failed write can leave a partial new report, so inspect that path and use a different name when retrying.
- Cycle diagnostics give deterministic concrete witnesses, not every possible simple cycle in an overlapping graph. Long cyclic checklists do not depend on the Python recursion limit.
- Reports are views of the input, not lossless backups: Markdown omits dependency annotations and JSON reports wrap the task array under `ordered`. Keep the original file; use that array as JSON task input if needed.
- Text, Markdown, JSON, and Graphviz DOT reports are supported.
- The sorter does not estimate duration, assign people, infer hidden dependencies, or replace a project manager.
- DOT output is a graph description; rendering it requires Graphviz or another compatible viewer.

## Development

```bash
python -m pip install -e . pytest build
python -m pytest
python -m build
```

## Project status

**Feature complete for v1.1.** Contributions should keep ordering deterministic and diagnostics specific.

### 1.1.1 — October 18, 2026

Preserve checked tasks, protect source files and existing reports, validate task fields and diagnose long cycles without recursive traversal. Ordinary unchecked output and dependency-layer behavior stay compatible.

Released under the [MIT License](LICENSE). Contributions follow the [organization guidelines](https://github.com/loganpendragonmultiverse/.github/blob/main/CONTRIBUTING.md).

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Browse the catalog for other released tools, source repositories, live demos, and downloads.

## Dependency layers (1.1.0)

Use `checklist-sort tasks.json --layers` or add `--format markdown` / `--format json`.
A layer groups tasks whose declared prerequisites occur in earlier layers. Tasks in a
layer retain source order. This is dependency evidence, not a guarantee that tasks can
safely execute concurrently: undeclared dependencies and shared resources are unknown.
The ordinary ordered output stays unchanged. Missing references or cycles make layers
unavailable (exit 1); JSON includes `layers_available: false` and an empty `layers` array.
DOT remains the existing graph and cannot be combined with `--layers` (exit 2).
