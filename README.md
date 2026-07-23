# Checklist Dependency Sorter

Checklist Dependency Sorter turns an unordered task list into a stable, dependency-respecting sequence. It also names missing task references and prints concrete cycle paths instead of returning a vague sorting error.

## Install

Python 3.10 or newer is required.

```bash
python -m venv .venv
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

JSON may be an array or an object with a `tasks` array. Each task needs `id`, `text`, and an optional string array named `depends_on`.

## Output and limitations

- Independent tasks retain their source order whenever dependency rules allow it.
- Missing dependencies and cycles produce exit code 1; malformed input produces exit code 2.
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

**Feature complete for v1.0.** Contributions should keep ordering deterministic and diagnostics specific.

Released under the [MIT License](LICENSE). Contributions follow the [organization guidelines](https://github.com/loganpendragonmultiverse/.github/blob/main/CONTRIBUTING.md).

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Browse the catalog for other released tools, source repositories, live demos, and downloads.
