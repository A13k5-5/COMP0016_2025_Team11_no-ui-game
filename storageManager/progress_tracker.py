import os
import json
import tempfile
import zipfile

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
        Mirrors GameSaver._zip_folder_to.
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_full_path = os.path.join(dirpath, filename)
                    # arcname = the path the file gets inside the zip
                    arcname = os.path.relpath(file_full_path, folder_path)
                    zf.write(file_full_path, arcname)