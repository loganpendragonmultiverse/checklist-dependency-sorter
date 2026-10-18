import json
from pathlib import Path

import pytest

from checklist_sorter.cli import main, render
from checklist_sorter.sorter import Task, load_tasks, sort_tasks


def test_output_refuses_source_and_existing_file(tmp_path, capsys):
    source = tmp_path / "tasks.json"
    original = '[{"id":"a","text":"Keep original"}]'
    source.write_text(original)
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_text() == original
    destination = tmp_path / "existing.md"
    destination.write_text("Keep report")
    assert main([str(source), "--output", str(destination)]) == 2
    assert destination.read_text() == "Keep report"
    assert "checklist-sort:" in capsys.readouterr().err


def test_output_refuses_symlinks_and_missing_parent(tmp_path, capsys):
    source = tmp_path / "tasks.md"
    source.write_text("- [ ] a: Start\n")
    alias = tmp_path / "alias.md"
    try:
        alias.symlink_to(source)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable for this account")
    assert main([str(source), "--output", str(alias)]) == 2
    dangling = tmp_path / "dangling.md"
    target = tmp_path / "not-created.md"
    dangling.symlink_to(target)
    assert main([str(source), "--output", str(dangling)]) == 2
    assert not target.exists()
    assert main([str(source), "--output", str(tmp_path / "missing" / "out.md")]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_write_failure_is_an_actionable_cli_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / "tasks.md"
    source.write_text("- [ ] a: Start\n")
    original_open = Path.open

    def reject_new_output(self, mode="r", *args, **kwargs):
        if mode == "x":
            raise PermissionError("synthetic destination permission failure")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", reject_new_output)
    assert main([str(source), "--output", str(tmp_path / "report")]) == 2
    assert "permission failure" in capsys.readouterr().err


@pytest.mark.parametrize("field,value", [
    ("id", 42), ("id", True), ("id", None), ("id", "  "),
    ("text", False), ("text", ["nested"]), ("text", "  "),
    ("depends_on", [" "]), ("depends_on", [None]), ("completed", 1),
])
def test_json_rejects_invalid_field_types_and_blanks(tmp_path, field, value):
    source = tmp_path / "invalid.json"
    task = {"id": "a", "text": "Start", field: value}
    source.write_text(json.dumps([task]))
    with pytest.raises(ValueError):
        load_tasks(source)


def test_checked_markdown_survives_reports_and_json_input(tmp_path):
    source = tmp_path / "checked.md"
    source.write_text("- [ ] end: Finish | after: start\n- [X] start: Started\n")
    tasks = load_tasks(source)
    result = sort_tasks(tasks)
    assert [task.id for task in result.ordered] == ["start", "end"]
    assert [task.completed for task in result.ordered] == [True, False]
    for layers in (False, True):
        assert "- [x] start: Started" in render(result, "markdown", layers=layers)
        assert "[x] start: Started" in render(result, "text", layers=layers)
        report = json.loads(render(result, "json", layers=layers))
        assert report["ordered"][0]["completed"] is True
        restored = tmp_path / ("layers.json" if layers else "ordered.json")
        restored.write_text(json.dumps(report["ordered"]))
        assert load_tasks(restored)[0].completed is True
    assert '[label="[x] start: Started"]' in render(result, "dot")


def test_long_cycle_and_dependent_tail_report_concrete_paths():
    count = 2000
    tasks = tuple(Task(str(i), "Task", (str((i + 1) % count),), i) for i in range(count))
    tasks += (Task("tail", "Blocked by cycle", ("0",), count),)
    result = sort_tasks(tasks)
    assert not result.valid and not result.layers
    assert len(result.ordered) == count + 1
    assert len(result.cycles) == 1
    cycle = result.cycles[0]
    assert len(cycle) == count + 1 and cycle[0] == cycle[-1] == "0"
    by_id = {task.id: task for task in tasks}
    assert all(b in by_id[a].depends_on for a, b in zip(cycle, cycle[1:]))


def test_disconnected_and_overlapping_cycles_remain_deterministic():
    tasks = (
        Task("a", "A", ("b", "c")), Task("b", "B", ("a",)),
        Task("c", "C", ("a",)), Task("z", "Z", ("z",)),
    )
    first = sort_tasks(tasks)
    assert first.cycles == (("a", "b", "a"), ("a", "c", "a"), ("z", "z"))
    assert sort_tasks(tasks).cycles == first.cycles


def test_programmatic_duplicate_ids_cannot_drop_tasks():
    with pytest.raises(ValueError, match="Duplicate"):
        sort_tasks((Task("a", "One"), Task("a", "Two")))


def test_dot_escapes_multiline_json_labels():
    result = sort_tasks((Task("line\nbreak", 'A "quote"\nNext line'),))
    dot = render(result, "dot")
    assert '"line\\nbreak"' in dot
    assert 'A \\"quote\\"\\nNext line' in dot


def test_dangling_symlink_is_refused_before_any_write_open(tmp_path, monkeypatch):
    source = tmp_path / "tasks.md"
    source.write_text("- [ ] a: Task\n")
    link = tmp_path / "dangling.md"
    try:
        link.symlink_to(tmp_path / "absent.md")
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable for this account")
    original_open = Path.open

    def observe_open(self, mode="r", *args, **kwargs):
        if self == link and mode == "x":
            raise AssertionError("Existing dangling links must be refused before open")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", observe_open)
    assert main([str(source), "--output", str(link)]) == 2
    assert not (tmp_path / "absent.md").exists()
