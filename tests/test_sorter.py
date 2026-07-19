import json
from pathlib import Path

from checklist_sorter.sorter import Task, load_tasks, sort_tasks


def test_orders_dependencies_stably() -> None:
    tasks = (Task("ship", "Ship", ("test",), 0), Task("write", "Write", (), 1), Task("test", "Test", ("write",), 2))
    result = sort_tasks(tasks)
    assert [task.id for task in result.ordered] == ["write", "test", "ship"]
    assert result.valid


def test_reports_missing_dependency() -> None:
    result = sort_tasks((Task("ship", "Ship", ("approve",)),))
    assert result.missing == (("ship", "approve"),)
    assert not result.valid


def test_reports_cycle_once() -> None:
    result = sort_tasks((Task("a", "A", ("b",)), Task("b", "B", ("c",)), Task("c", "C", ("a",))))
    assert result.cycles == (("a", "b", "c", "a"),)


def test_loads_json_and_markdown(tmp_path: Path) -> None:
    json_file = tmp_path / "tasks.json"
    json_file.write_text(json.dumps({"tasks": [{"id": "a", "text": "Start"}, {"id": "b", "text": "Finish", "depends_on": ["a"]}]}), encoding="utf-8")
    assert len(load_tasks(json_file)) == 2
    markdown = tmp_path / "tasks.md"
    markdown.write_text("- [ ] a: Start\n- [ ] b: Finish | after: a\n", encoding="utf-8")
    assert load_tasks(markdown)[1].depends_on == ("a",)


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "tasks.md"
    source.write_text("- [ ] a: One\n- [ ] a: Two\n", encoding="utf-8")
    try:
        load_tasks(source)
    except ValueError as exc:
        assert "Duplicate task id" in str(exc)
    else:
        raise AssertionError("Expected duplicate task validation")
