# nuitka-project: --mode=standalone

# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# nuitka-project: --include-data-files={MAIN_DIRECTORY}/myGestureRecognizer/gesture_recognizer.task=myGestureRecognizer/gesture_recognizer.task
if __name__ == "__main__":

    import sys
    import gamePlayer

    if len(sys.argv) > 1:
        player = gamePlayer.GamePlayer()
        player.play_game(sys.argv[1])
    else:
        import playerPage
        playerPage.run()
