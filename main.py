# Compilation mode, support OS-specific options
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --mode=onefile
# nuitka-project-else:
#    nuitka-project: --mode=standalone
# The PySide6 plugin covers qt-plugins
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

import sys

import gamePlayer
import playerPage

if __name__ == "__main__":
    # for game player
    # if len(sys.argv) > 1:
    #     player = gamePlayer.GamePlayer()
    #     player.playGame(sys.argv[1])
    # else:
    #     playerPage.run()

    # for game engine
    from gui.homePage import run
    run()
