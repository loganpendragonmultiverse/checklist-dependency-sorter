from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    text: str
    depends_on: tuple[str, ...] = ()
    source_order: int = 0

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["depends_on"] = list(self.depends_on)
        return result


@dataclass(frozen=True, slots=True)
class SortResult:
    ordered: tuple[Task, ...]
    missing: tuple[tuple[str, str], ...]
    cycles: tuple[tuple[str, ...], ...]

    @property
    def valid(self) -> bool:
        return not self.missing and not self.cycles


def load_tasks(path: Path) -> tuple[Task, ...]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"Not a file: {source}")
    if source.suffix.casefold() == ".json":
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        values = payload.get("tasks") if isinstance(payload, dict) else payload
        if not isinstance(values, list):
            raise ValueError("JSON must be an array of tasks or an object with a tasks array")
        tasks = []
        for index, item in enumerate(values):
            if not isinstance(item, dict) or not item.get("id") or not item.get("text"):
                raise ValueError(f"Task {index + 1} needs non-empty id and text fields")
            dependencies = item.get("depends_on", [])
            if not isinstance(dependencies, list) or not all(isinstance(value, str) for value in dependencies):
                raise ValueError(f"Task {item['id']} has an invalid depends_on list")
            tasks.append(Task(str(item["id"]).strip(), str(item["text"]).strip(), tuple(value.strip() for value in dependencies if value.strip()), index))
        return _validate_ids(tasks)
    return _parse_markdown(source.read_text(encoding="utf-8-sig"))


def _parse_markdown(content: str) -> tuple[Task, ...]:
    tasks = []
    pattern = re.compile(r"^\s*-\s*\[[ xX]\]\s*([A-Za-z0-9_.-]+)\s*:\s*(.+?)(?:\s*\|\s*after\s*:\s*(.*))?$", re.I)
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError(f"Line {line_number} must use '- [ ] id: text | after: dependency, ...'")
        dependencies = tuple(value.strip() for value in (match.group(3) or "").split(",") if value.strip())
        tasks.append(Task(match.group(1), match.group(2).strip(), dependencies, len(tasks)))
    if not tasks:
        raise ValueError("No checklist tasks were found")
    return _validate_ids(tasks)


def _validate_ids(tasks: list[Task]) -> tuple[Task, ...]:
    seen: set[str] = set()
    for task in tasks:
        if task.id in seen:
            raise ValueError(f"Duplicate task id: {task.id}")
        seen.add(task.id)
    return tuple(tasks)


def sort_tasks(tasks: tuple[Task, ...]) -> SortResult:
    by_id = {task.id: task for task in tasks}
    missing = sorted((task.id, dependency) for task in tasks for dependency in task.depends_on if dependency not in by_id)
    indegree = {task.id: 0 for task in tasks}
    children: dict[str, list[str]] = {task.id: [] for task in tasks}
    for task in tasks:
        for dependency in task.depends_on:
            if dependency in by_id:
                indegree[task.id] += 1
                children[dependency].append(task.id)

    ready = sorted((task for task in tasks if indegree[task.id] == 0), key=lambda task: task.source_order)
    ordered: list[Task] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for child_id in sorted(children[current.id], key=lambda value: by_id[value].source_order):
            indegree[child_id] -= 1
            if indegree[child_id] == 0:
                ready.append(by_id[child_id])
                ready.sort(key=lambda task: task.source_order)

    unresolved = {task.id for task in tasks if indegree[task.id] > 0}
    cycles = _find_cycles(by_id, unresolved)
    ordered.extend(task for task in tasks if task.id in unresolved)
    return SortResult(tuple(ordered), tuple(missing), cycles)


def _find_cycles(by_id: dict[str, Task], unresolved: set[str]) -> tuple[tuple[str, ...], ...]:
    cycles: set[tuple[str, ...]] = set()
    for start in sorted(unresolved):
        path: list[str] = []
        positions: dict[str, int] = {}

        def visit(node: str) -> None:
            if node in positions:
                cycle = path[positions[node] :] + [node]
                body = cycle[:-1]
                rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
                canonical = min(rotations)
                cycles.add(canonical + (canonical[0],))
                return
            if node not in unresolved:
                return
            positions[node] = len(path)
            path.append(node)
            for dependency in by_id[node].depends_on:
                visit(dependency)
            path.pop()
            positions.pop(node)

        visit(start)
    return tuple(sorted(cycles))
