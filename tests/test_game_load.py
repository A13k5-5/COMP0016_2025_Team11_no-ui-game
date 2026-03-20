import sys
from pathlib import Path
import unicodedata
import zipfile

import pytest
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.graph import EnumLR, Node
from src.graph.serial_graph import SerialGraph
from src.storageManager import game_load
from src.storageManager.game_load import GameLoader
from src.storageManager.test_graphs import build_default_story_graph


def _make_game_zip(
    base_dir: Path,
    archive_name: str,
    root: Node,
    top_level_folder: str | None = "game",
) -> Path:
    archive_path = base_dir / archive_name
    serial_graph = SerialGraph.serialize_graph(root)
    prefix = f"{top_level_folder}/" if top_level_folder else ""

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{prefix}graph.json", serial_graph.model_dump_json(indent=4))
        zf.writestr(f"{prefix}audio/dummy.wav", b"fake audio")

    return archive_path


def _assert_graph_matches(expected: Node, actual: Node, seen: set[int] | None = None) -> None:
    if seen is None:
        seen = set()

    if expected.id in seen:
        return

    seen.add(expected.id)

    assert actual.id == expected.id
    assert unicodedata.normalize("NFC", actual.getText()) == unicodedata.normalize("NFC", expected.getText())
    assert actual.left_option == expected.left_option
    assert actual.right_option == expected.right_option
    assert actual.is_win == expected.is_win
    assert actual.is_losing == expected.is_losing

    for side in (EnumLR.LEFT, EnumLR.RIGHT):
        expected_child = expected.getNode(side)
        actual_child = actual.getNode(side)
        if expected_child is None:
            assert actual_child is None
        else:
            assert actual_child is not None
            _assert_graph_matches(expected_child, actual_child, seen)


def test_load_graph_extracts_nested_archive_and_rebuilds_graph(tmp_path, monkeypatch):
    temp_folder = tmp_path / "temporary"
    monkeypatch.setattr(game_load, "TEMP_FOLDER", str(temp_folder))

    root = Node("Root story", left_option="Go left", right_option="Go right")
    shared = Node("Shared path", left_option="Continue", right_option="Wait")
    win = Node("Victory")
    win.is_win = True

    root.addNode(EnumLR.LEFT, shared)
    root.addNode(EnumLR.RIGHT, shared)
    shared.addNode(EnumLR.LEFT, win)
    shared.addNode(EnumLR.RIGHT, win)

    archive = _make_game_zip(tmp_path, "nested_game.zip", root, "nested_game")

    loaded_root, game_folder, returned_zip = GameLoader().load_graph(str(archive))

    assert returned_zip == str(archive)
    assert game_folder == str(temp_folder / "nested_game")
    _assert_graph_matches(root, loaded_root)

    # The serialized graph shares nodes, so the deserialized graph should as well.
    assert loaded_root.getNode(EnumLR.LEFT) is loaded_root.getNode(EnumLR.RIGHT)
    assert loaded_root.getNode(EnumLR.LEFT).getNode(EnumLR.LEFT) is loaded_root.getNode(EnumLR.LEFT).getNode(EnumLR.RIGHT)


def test_load_graph_handles_flat_archive_without_top_level_folder(tmp_path, monkeypatch):
    temp_folder = tmp_path / "temporary"
    monkeypatch.setattr(game_load, "TEMP_FOLDER", str(temp_folder))

    original_root = Node("Flat root")
    archive = _make_game_zip(tmp_path, "flat_game.zip", original_root, None)

    loaded_root, game_folder, returned_zip = GameLoader().load_graph(str(archive))

    assert returned_zip == str(archive)
    assert game_folder == str(temp_folder)
    _assert_graph_matches(original_root, loaded_root)


def test_load_graph_raises_when_graph_json_is_missing(tmp_path, monkeypatch):
    temp_folder = tmp_path / "temporary"
    monkeypatch.setattr(game_load, "TEMP_FOLDER", str(temp_folder))

    archive = tmp_path / "missing_graph.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("game/audio/dummy.wav", b"fake audio")

    with pytest.raises(FileNotFoundError):
        GameLoader().load_graph(str(archive))


def test_load_graph_raises_on_invalid_graph_json(tmp_path, monkeypatch):
    temp_folder = tmp_path / "temporary"
    monkeypatch.setattr(game_load, "TEMP_FOLDER", str(temp_folder))

    archive = tmp_path / "bad_graph.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("game/graph.json", "not valid json")
        zf.writestr("game/audio/dummy.wav", b"fake audio")

    with pytest.raises(ValidationError):
        GameLoader().load_graph(str(archive))


def test_load_graph_recreates_temp_folder_between_loads(tmp_path, monkeypatch):
    temp_folder = tmp_path / "temporary"
    monkeypatch.setattr(game_load, "TEMP_FOLDER", str(temp_folder))

    temp_folder.mkdir()
    stale_file = temp_folder / "stale.txt"
    stale_file.write_text("stale data")

    first_archive = _make_game_zip(tmp_path, "first.zip", build_default_story_graph(), "first")
    second_root = Node("Second story")
    second_archive = _make_game_zip(tmp_path, "second.zip", second_root, "second")

    loader = GameLoader()
    loader.load_graph(str(first_archive))
    assert not stale_file.exists()

    leftover_file = temp_folder / "leftover.txt"
    leftover_file.write_text("leftover data")

    loaded_root, game_folder, returned_zip = loader.load_graph(str(second_archive))

    assert returned_zip == str(second_archive)
    assert game_folder == str(temp_folder / "second")
    assert loaded_root.getText() == "Second story"
    assert not leftover_file.exists()
