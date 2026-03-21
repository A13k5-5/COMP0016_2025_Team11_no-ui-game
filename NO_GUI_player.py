# nuitka-project: --mode=onefile
# nuitka-project: --windows-console-mode=disable

# for pyside6
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# recognizer file for mediapipe
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/src/myGestureRecognizer/gesture_recognizer.task=src/myGestureRecognizer/gesture_recognizer.task

# for the icon
# nuitka-project: --include-data-files=icon.ico=icon.ico
# nuitka-project: --windows-icon-from-ico=icon.ico


import sys
from src.gui_game_player import playerPage

if __name__ == "__main__":
    if len(sys.argv) > 1:
        playerPage.run(sys.argv[1])
    else:
        playerPage.run()
