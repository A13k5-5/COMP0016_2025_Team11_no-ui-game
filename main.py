# nuitka-project: --mode=standalone

# Data files required at runtime
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/myGestureRecognizer/gesture_recognizer.task=myGestureRecognizer/gesture_recognizer.task
## nuitka-project: --include-data-dir={MAIN_DIRECTORY}/game_generation_local_llm/model_path=game_generation_local_llm/model_path

if __name__ == "__main__":
    # for game player
    import sys
    import gamePlayer

    if len(sys.argv) > 1:
        player = gamePlayer.GamePlayer()
        player.play_game(sys.argv[1])
    else:
        import playerPage
        playerPage.run()

    # for video gesture recognizer
    # import myGestureRecognizer
    # from gesture import EnumGesture
    #
    # recognizer = myGestureRecognizer.VideoGestureRecogniser()
    # recognizer.get_gesture([EnumGesture.ILoveYou_Right, EnumGesture.Victory])

    # for game engine
    # import kokoro
    # from gui.homePage import run
    # run()

    # for game loading
    # from storageManager.game_load import GameLoader
    # loader = GameLoader()
    # root, game_folder = loader.load_graph("./saved_games/Lord of the rings.noui")
    # print(root)

    # for game saving
    # import os
    # from storageManager.game_save import GameSaver
    # from graph.serial_graph import SerialGraph

    # with open(os.path.join(os.path.dirname(__file__), "game_generation_local_llm\\generated_games", "harry_potter1.json"), 'r') as file:
    #     serialized_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())
    # saver = GameSaver()
    # saver.save_game(os.path.join(os.path.dirname(__file__), "saved_games"), "harry potter", serialized_graph)

    # for structured output
    # from game_generation_local_llm import structured_output
    # structured_output.main()

