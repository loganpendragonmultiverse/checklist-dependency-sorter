from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    text: str
    depends_on: tuple[str, ...] = ()
    source_order: int = 0
    completed: bool = False

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["depends_on"] = list(self.depends_on)
        if not self.completed:
            result.pop("completed")
        return result


@dataclass(frozen=True, slots=True)
class SortResult:
    ordered: tuple[Task, ...]
    missing: tuple[tuple[str, str], ...]
    cycles: tuple[tuple[str, ...], ...]
    layers: tuple[tuple[Task, ...], ...] = ()

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
            if (
                not isinstance(item, dict)
                or any(not isinstance(item.get(field), str) or not item[field].strip()
                       for field in ("id", "text"))
            ):
                raise ValueError(f"Task {index + 1} needs nonblank string id and text fields")
            dependencies = item.get("depends_on", [])
            if not isinstance(dependencies, list) or not all(isinstance(value, str) and value.strip() for value in dependencies):
                raise ValueError(f"Task {item['id']} depends_on must contain nonblank strings")
            completed = item.get("completed", False)
            if not isinstance(completed, bool):
                raise ValueError(f"Task {item['id']} completed must be a boolean")
            tasks.append(Task(item["id"].strip(), item["text"].strip(), tuple(value.strip() for value in dependencies), index, completed))
        return _validate_ids(tasks)
    return _parse_markdown(source.read_text(encoding="utf-8-sig"))


def _parse_markdown(content: str) -> tuple[Task, ...]:
    tasks = []
    pattern = re.compile(r"^\s*-\s*\[([ xX])\]\s*([A-Za-z0-9_.-]+)\s*:\s*(.+?)(?:\s*\|\s*after\s*:\s*(.*))?$", re.I)
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError(f"Line {line_number} must use '- [ ] id: text | after: dependency, ...'")
        dependencies = tuple(value.strip() for value in (match.group(4) or "").split(",") if value.strip())
        tasks.append(Task(match.group(2), match.group(3).strip(), dependencies, len(tasks), match.group(1).casefold() == "x"))
    if not tasks:
        raise ValueError("No checklist tasks were found")
    return _validate_ids(tasks)


def _validate_ids(tasks: list[Task] | tuple[Task, ...]) -> tuple[Task, ...]:
    seen: set[str] = set()
    for task in tasks:
        if any(not isinstance(value, str) or not value.strip() for value in (task.id, task.text)):
            raise ValueError("Task IDs and text must be nonblank strings")
        if any(not isinstance(value, str) or not value.strip() for value in task.depends_on):
            raise ValueError(f"Task {task.id} depends_on must contain nonblank strings")
        if not isinstance(task.completed, bool):
            raise ValueError(f"Task {task.id} completed must be a boolean")
        if task.id in seen:
            raise ValueError(f"Duplicate task id: {task.id}")
        seen.add(task.id)
    return tuple(tasks)


def sort_tasks(tasks: tuple[Task, ...]) -> SortResult:
    _validate_ids(tasks)
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
    depths: dict[str, int] = {}
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        depths[current.id] = 1 + max((depths[dependency] for dependency in current.depends_on if dependency in depths), default=-1)
        for child_id in sorted(children[current.id], key=lambda value: by_id[value].source_order):
            indegree[child_id] -= 1
            if indegree[child_id] == 0:
                ready.append(by_id[child_id])
                ready.sort(key=lambda task: task.source_order)

    unresolved = {task.id for task in tasks if indegree[task.id] > 0}
    cycles = _find_cycles(by_id, unresolved)
    ordered.extend(task for task in tasks if task.id in unresolved)
    layers = ()
    if not missing and not cycles:
        tasks_by_depth: dict[int, list[Task]] = {}
        for task in tasks:
            tasks_by_depth.setdefault(depths[task.id], []).append(task)
        layers = tuple(
            tuple(sorted(tasks_by_depth[depth], key=lambda task: task.source_order))
            for depth in sorted(tasks_by_depth)
        )
    return SortResult(tuple(ordered), tuple(missing), cycles, layers)


def _find_cycles(by_id: dict[str, Task], unresolved: set[str]) -> tuple[tuple[str, ...], ...]:
    """Return deterministic concrete cycle witnesses without recursive traversal.

    Back edges identify cycles; the result is not an enumeration of every possible
    simple cycle in an overlapping graph. Each node/edge is traversed once.
    """
    cycles: set[tuple[str, ...]] = set()
    finished: set[str] = set()
    for start in sorted(unresolved):
        if start in finished:
            continue
        path = [start]
        positions = {start: 0}
        stack: list[Iterator[str]] = [iter(by_id[start].depends_on)]
        while stack:
            dependency = next(stack[-1], None)
            if dependency is None:
                finished.add(path.pop())
                positions.popitem()
                stack.pop()
            elif dependency in positions:
                body = path[positions[dependency]:]
                first = body.index(min(body))
                canonical = tuple(body[first:] + body[:first])
                cycles.add(canonical + (canonical[0],))
            elif dependency in unresolved and dependency not in finished:
                positions[dependency] = len(path)
                path.append(dependency)
                stack.append(iter(by_id[dependency].depends_on))
    return tuple(sorted(cycles))
