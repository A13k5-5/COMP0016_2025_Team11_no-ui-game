## nuitka-project: --mode=onefile
# nuitka-project: --mode=standalone
# nuitka-project: --windows-console-mode=disable

# for pyside6
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# recognizer file for mediapipe
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/src/game_player/myGestureRecognizer/gesture_recognizer.task=src/game_player/myGestureRecognizer/gesture_recognizer.task

# for the icon
# nuitka-project: --include-data-files=src/game_player/icon.ico=src/game_player/icon.ico
# nuitka-project: --windows-icon-from-ico=src/game_player/icon.ico
# nuitka-project: --output-filename=SoundLab Player.exe


import sys
from src.game_player.gui import playerPage

if __name__ == "__main__":
    if len(sys.argv) > 1:
        playerPage.run(sys.argv[1])
    else:
        playerPage.run()
