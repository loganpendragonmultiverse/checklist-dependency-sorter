from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .sorter import SortResult, load_tasks, sort_tasks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="checklist-sort", description="Order checklist tasks by dependency and report broken relationships.")
    parser.add_argument("checklist", type=Path, help="JSON or Markdown checklist")
    parser.add_argument("--format", choices=("text", "markdown", "json", "dot"), default="text")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = sort_tasks(load_tasks(args.checklist))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"checklist-sort: {exc}", file=sys.stderr)
        return 2
    report = render(result, args.format)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote {args.format} report to {args.output}")
    else:
        print(report, end="")
    return 0 if result.valid else 1


def render(result: SortResult, format_name: str) -> str:
    if format_name == "json":
        return json.dumps({"valid": result.valid, "ordered": [task.to_dict() for task in result.ordered], "missing": [{"task": task, "dependency": dependency} for task, dependency in result.missing], "cycles": [list(cycle) for cycle in result.cycles]}, indent=2) + "\n"
    if format_name == "dot":
        lines = ["digraph checklist {"]
        for task in result.ordered:
            lines.append(f'  "{_dot(task.id)}" [label="{_dot(task.id + ": " + task.text)}"];')
            for dependency in task.depends_on:
                lines.append(f'  "{_dot(dependency)}" -> "{_dot(task.id)}";')
        return "\n".join(lines + ["}", ""])
    prefix = "- [ ] " if format_name == "markdown" else ""
    lines = [f"{prefix}{task.id}: {task.text}" for task in result.ordered]
    if result.missing:
        lines.extend(("", "Missing dependencies:", *(f"- {task} depends on unknown task {dependency}" for task, dependency in result.missing)))
    if result.cycles:
        lines.extend(("", "Dependency cycles:", *("- " + " -> ".join(cycle) for cycle in result.cycles)))
    return "\n".join(lines) + "\n"


def _dot(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    raise SystemExit(main())
