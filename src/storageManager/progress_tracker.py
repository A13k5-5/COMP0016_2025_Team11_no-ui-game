import os
import json
import tempfile
import zipfile

from src.graph import Node

PROGRESS_FILENAME = "progress.json"

class ProgressTracker:
    """
    Class responsible for tracking/saving progress in a game when quit midway.
    """
    def save_progress(self, zip_path: str, node_id: int) -> None:
        """
        Write progress.json into the game's subfolder inside the .noui zip.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)

            game_dir = self._get_game_dir(tmp_dir)
            with open(os.path.join(game_dir, PROGRESS_FILENAME), 'w') as f:
                json.dump({"node_id": node_id}, f)

            self._zip_folder_to(tmp_dir, zip_path)

    def _get_game_dir(self, tmp_dir: str) -> str:
        """
        Returns the single game subfolder extracted from the zip.
        """
        return next(
            os.path.join(tmp_dir, d) for d in os.listdir(tmp_dir)
            if os.path.isdir(os.path.join(tmp_dir, d))
        )
    
    def _zip_folder_to(self, folder_path: str, zip_path: str) -> None:
        """
        Writes the contents of folder_path into a new zip archive at zip_path.
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_full_path = os.path.join(dirpath, filename)
                    # arcname = the path the file gets inside the zip
                    arcname = os.path.relpath(file_full_path, folder_path)
                    zf.write(file_full_path, arcname)

    def clear_progress(self, zip_path: str) -> None:
        """
        Remove progress.json from the .noui zip if it exists.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)

            game_dir = self._get_game_dir(tmp_dir)
            progress_path = os.path.join(game_dir, PROGRESS_FILENAME)
            if os.path.exists(progress_path):
                os.remove(progress_path)

            self._zip_folder_to(tmp_dir, zip_path)

    def get_progress_node(self, game_folder: str, root_node: Node) -> Node | None:
        """
        Gives the progress node if a progress.json file exists and is valid, otherwise returns None.
        :param game_folder:
        :param root_node:
        :return:
        """
        progress_path = os.path.join(game_folder, "progress.json")

        # if doesn't exist, return None
        if not os.path.exists(progress_path):
            return None

        try:
            # if error, return None
            with open(progress_path, "r") as f:
                data = json.load(f)
            saved_id = data.get("node_id")
            saved_node = self._find_node_by_id(root_node, saved_id)
        except Exception:
            return None

        if saved_node is None:
            return None

        return saved_node

    def _find_node_by_id(self, root: Node, target_id: int) -> Node | None:
        """
        BFS from root to find the node with the given ID
        """
        visited: set[int] = set()
        queue: list[Node] = [root]
        while queue:
            node = queue.pop(0)
            node_id = node.get_id()
            if node_id in visited:
                continue
            visited.add(node_id)
            if node_id == target_id:
                return node
            queue.extend(node.adjacencyList.values())
        return None
