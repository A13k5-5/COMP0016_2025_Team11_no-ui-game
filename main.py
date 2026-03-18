# Compilation mode, support OS-specific options
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --mode=onefile
# nuitka-project-else:
#    nuitka-project: --mode=standalone
# The PySide6 plugin covers qt-plugins
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

if __name__ == "__main__":
    # for game player
    # import sys
    # import gamePlayer
    # import playerPage
    #
    # if len(sys.argv) > 1:
    #     player = gamePlayer.GamePlayer()
    #     player.play_game(sys.argv[1])
    # else:
    #     playerPage.run()

    # for game engine
    # import kokoro
    from src.gui.homePage import run
    run()

    # for game loading
    # from storageManager.game_load import GameLoader
    # loader = GameLoader()
    # root, game_folder = loader.load_graph("./saved_games/Lord of the rings.noui")
    # print(root)

    # for game saving
    # import os
    # from storageManager.game_save import GameSaver
    # from graph.serial_graph import SerialGraph
    #
    # with open(os.path.join(os.path.dirname(__file__), "game_generation_local_llm\\generated_games", "bed_story_serial.json"), 'r') as file:
    #     serialized_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())
    # saver = GameSaver()
    # saver.save_game(os.path.join(os.path.dirname(__file__), "saved_games"), "Bed story", serialized_graph)

    # for structured output
    # from game_generation_local_llm import structured_output
    # structured_output.main()

