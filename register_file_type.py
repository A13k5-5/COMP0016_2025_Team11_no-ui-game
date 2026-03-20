import winreg
import sys
import ctypes
from pathlib import Path

DEFAULT_ICON: Path = Path(__file__).parent / "gameIcon.ico"

def register_file_type(
    extension: str,          # e.g. ".myext"
    prog_id: str,            # e.g. "MyApp.Document"
    description: str,        # e.g. "My App Document"
    icon_path: str = str(DEFAULT_ICON),   # path to .ico file or exe,index e.g. "C:\app.exe,0"
):
    """
    Register a custom file type in the Windows registry (current user only).
    No admin rights required.
    This app should be run once at startup to ensure the file type is registered, but it will be a no-op if already registered.
    """
    if _is_registered(extension, prog_id):
        return

    exe_path = sys.executable  # points to your compiled .exe when built with Nuitka

    # 1. Register the ProgID and its shell open command
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
        winreg.SetValue(key, "", winreg.REG_SZ, description)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key:
        winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')

    # 2. Optionally register an icon
    if icon_path:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, icon_path)

    # 3. Associate the file extension with the ProgID
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{extension}") as key:
        winreg.SetValue(key, "", winreg.REG_SZ, prog_id)

    # 4. Tell the shell the association has changed
    _notify_shell_assoc_changed()

    print(f"Registered {extension} -> {prog_id} for {exe_path}")


def _is_registered(extension: str, prog_id: str) -> bool:
    """Check if the file type is already registered."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{extension}") as key:
            value, _ = winreg.QueryValueEx(key, "")
            return value == prog_id
    except FileNotFoundError:
        return False

def _notify_shell_assoc_changed() -> None:
    SHCNE_ASSOCCHANGED = 0x08000000
    SHCNF_IDLIST = 0x0000
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)


def _delete_tree(root: int, subkey: str) -> None:
    """Best-effort recursive registry delete for HKCU\\Software\\Classes entries."""
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    child_name = winreg.EnumKey(key, 0)
                except OSError:
                    break
                _delete_tree(root, f"{subkey}\\{child_name}")
    except FileNotFoundError:
        return

    try:
        winreg.DeleteKey(root, subkey)
    except FileNotFoundError:
        pass
    except OSError:
        # Leave non-empty/locked keys untouched instead of failing the whole unregister.
        pass


def _normalize_extension(extension: str) -> str:
    ext = extension.strip()
    if not ext:
        raise ValueError("extension must not be empty")
    return ext if ext.startswith(".") else f".{ext}"


def unregister_file_type(extension: str, prog_id: str):
    """
    Unregisters filetype for the current user. Here for testing purposes.
    :param extension:
    :param prog_id:
    :return:
    """
    ext = _normalize_extension(extension)

    # Remove all per-user links for this extension so apps are fully unlinked from it.
    extension_link_paths = [
        rf"Software\Classes\{ext}",
        rf"Software\Classes\SystemFileAssociations\{ext}",
        rf"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{ext}",
    ]
    for path in extension_link_paths:
        _delete_tree(winreg.HKEY_CURRENT_USER, path)

    # Remove this app's ProgID registration itself.
    _delete_tree(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}")

    _notify_shell_assoc_changed()


# --- Call this at startup ---
if __name__ == "__main__":
    EXT = ".noui"
    PROG_ID = "NoGui.noui"

    unregister_file_type(EXT, PROG_ID)

    register_file_type(
        extension=EXT,
        prog_id=PROG_ID,
        description="NoGUI Game File",
    )