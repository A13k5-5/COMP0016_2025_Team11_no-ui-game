import sys
from pathlib import Path
import zipfile

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.graph import EnumLR, Node
from src.graph.serial_graph import SerialGraph
from src.storageManager import config
from src.storageManager.game_save import GameSaver


def _build_simple_graph(root_text: str = "Start") -> Node:
    root = Node(root_text, left_option="Left", right_option="Right")
    left = Node("Left node")
    right = Node("Right node")
    root.addNode(EnumLR.LEFT, left)
    root.addNode(EnumLR.RIGHT, right)
    return root


def _fake_generate_audio(self, serial_graph: SerialGraph, game_path: str, voice: str):
    audio_dir = Path(game_path) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "dummy.wav").write_bytes(b"fake audio")


def _make_existing_valid_game_zip(path: Path, game_name: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{game_name}/graph.json", '{"nodes":{}}')
        zf.writestr(f"{game_name}/audio/dummy.wav", b"fake audio")


def test_save_game_creates_zip_file(tmp_path, monkeypatch):
    monkeypatch.setattr(GameSaver, "_generate_audio", _fake_generate_audio)

    saver = GameSaver()
    root = _build_simple_graph()
    game_name = "my_game"

    saver.save_game(str(tmp_path), game_name, root, "voice")

    zip_path = tmp_path / f"{game_name}{config.FILE_EXTENSION}"
    assert zip_path.exists()
    assert zipfile.is_zipfile(zip_path)


def test_save_game_archive_contains_graph_and_audio(tmp_path, monkeypatch):
    monkeypatch.setattr(GameSaver, "_generate_audio", _fake_generate_audio)

    saver = GameSaver()
    root = _build_simple_graph("Archive test")
    game_name = "archive_game"

    saver.save_game(str(tmp_path), game_name, root, "voice")

    zip_path = tmp_path / f"{game_name}{config.FILE_EXTENSION}"
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

    assert f"{game_name}/graph.json" in names
    assert any(name.startswith(f"{game_name}/audio/") for name in names)


def test_save_game_overwrites_existing_valid_game_zip(tmp_path, monkeypatch):
    monkeypatch.setattr(GameSaver, "_generate_audio", _fake_generate_audio)

    game_name = "overwrite_game"
    zip_path = tmp_path / f"{game_name}{config.FILE_EXTENSION}"
    _make_existing_valid_game_zip(zip_path, game_name)

    saver = GameSaver()
    root = _build_simple_graph("New story")
    saver.save_game(str(tmp_path), game_name, root, "voice")

    with zipfile.ZipFile(zip_path, "r") as zf:
        graph_text = zf.read(f"{game_name}/graph.json").decode("utf-8")

    serial_graph = SerialGraph.model_validate_json(graph_text)
    root_node = serial_graph.nodes[root.id]
    assert root_node.text == "New story"


def test_save_game_raises_if_non_game_file_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(GameSaver, "_generate_audio", _fake_generate_audio)

    saver = GameSaver()
    game_name = "blocked_game"
    zip_path = tmp_path / f"{game_name}{config.FILE_EXTENSION}"
    zip_path.write_text("not a zip")

    with pytest.raises(Exception, match="not a valid game zip"):
        saver.save_game(str(tmp_path), game_name, _build_simple_graph(), "voice")

