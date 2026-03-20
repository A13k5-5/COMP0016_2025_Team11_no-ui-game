# nuitka-project: --mode=standalone
# nuitka-project: --windows-disable-console

# for pyside6
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# recognizer file
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/src/myGestureRecognizer/gesture_recognizer.task=src/myGestureRecognizer/gesture_recognizer.task

import sys
from src import register_file_type
from src.gui_game_player import playerPage

if __name__ == "__main__":
    register_file_type.register_noui_file_type()

    if len(sys.argv) > 1:
        playerPage.run(sys.argv[1])
    else:
        playerPage.run()
