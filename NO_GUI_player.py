# nuitka-project: --mode=standalone

# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml
# nuitka-project: --windows-disable-console

# nuitka-project: --include-data-files={MAIN_DIRECTORY}/src/myGestureRecognizer/gesture_recognizer.task=src/myGestureRecognizer/gesture_recognizer.task
if __name__ == "__main__":
    import sys

    from src import playerPage
    if len(sys.argv) > 1:
        playerPage.run(sys.argv[1])
    playerPage.run()

