import json
from pathlib import Path

import pytest

from checklist_sorter.cli import main, render
from checklist_sorter.sorter import Task, sort_tasks


def ids(result):
    return [[task.id for task in layer] for layer in result.layers]


def test_chain_layers_preserve_default_order():
    tasks = (Task("c", "C", ("b",), 0), Task("a", "A", (), 1), Task("b", "B", ("a",), 2))
    result = sort_tasks(tasks)
    assert ids(result) == [["a"], ["b"], ["c"]]
    assert render(result, "text") == "a: A\nb: B\nc: C\n"
    assert "layers" not in json.loads(render(result, "json"))


def test_diamond_and_independent_tasks_are_stable():
    tasks = (Task("end", "End", ("left", "right"), 0), Task("right", "Right", ("start",), 1), Task("free", "Free", (), 2), Task("start", "Start", (), 3), Task("left", "Left", ("start", "start"), 4))
    result = sort_tasks(tasks)
    assert result.valid
    assert ids(result) == [["free", "start"], ["right", "left"], ["end"]]
    payload = json.loads(render(result, "json", layers=True))
    assert payload["layers_available"] is True
    assert [[t["id"] for t in layer] for layer in payload["layers"]] == ids(result)
    assert "## Layer 1\n- [ ] free: Free" in render(result, "markdown", layers=True)


@pytest.mark.parametrize("tasks", [(Task("a", "A", ("missing",)),), (Task("a", "A", ("b",)), Task("b", "B", ("a",))), (Task("a", "A", ("a",)), Task("free", "Free"))])
def test_invalid_graph_has_no_layers(tasks):
    result = sort_tasks(tasks)
    assert not result.valid and result.layers == ()
    payload = json.loads(render(result, "json", layers=True))
    assert payload["layers_available"] is False and payload["layers"] == []
    assert "Layer 1" not in render(result, "text", layers=True)
    assert "unavailable" in render(result, "text", layers=True)


def test_empty_graph():
    assert ids(sort_tasks(())) == []
    assert render(sort_tasks(()), "text", layers=True) == "No tasks.\n"


def test_cli_layers_and_exit_codes(tmp_path: Path, capsys):
    source = tmp_path / "tasks.json"
    source.write_text(json.dumps([{"id": "a", "text": "Start"}, {"id": "b", "text": "End", "depends_on": ["a"]}]))
    assert main([str(source), "--layers", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["layers_available"] is True
    source.write_text(json.dumps([{"id": "a", "text": "Start", "depends_on": ["missing"]}]))
    assert main([str(source), "--layers"]) == 1
    assert "unknown task missing" in capsys.readouterr().out
    with pytest.raises(SystemExit) as error:
        main([str(source), "--layers", "--format", "dot"])
    assert error.value.code == 2
