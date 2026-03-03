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
    # from gui.homePage import run
    # run()

    # for game loading
    # from storageManager.game_load import GameLoader
    # loader = GameLoader()
    # root, game_folder = loader.load_graph("./saved_games/Lord of the rings.noui")
    # print(root)

    # for game saving
    import os
    from storageManager.game_save import GameSaver
    import storageManager.test_graphs
    from graph import Node

    saver = GameSaver()
    root: Node = storageManager.test_graphs.build_default_story_graph()
    saver.save_game(os.path.join(os.path.dirname(__file__), "saved_games"), "lord_of_the_rings", root)

