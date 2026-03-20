# nuitka-project: --mode=standalone

# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# Data files required at runtime
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/myGestureRecognizer/gesture_recognizer.task=myGestureRecognizer/gesture_recognizer.task
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/game_generation_local_llm/model_path=game_generation_local_llm/model_path

# nuitka-project: --output-filename=NOGUI_engine.exe
# nuitka-project: --module-parameter=torch-disable-jit=yes
# nuitka-project: --nofollow-import-to=transformers.commands
# nuitka-project: --nofollow-import-to=transformers.generation.tf_utils
# nuitka-project: --nofollow-import-to=transformers.generation.flax_utils
# nuitka-project: --nofollow-import-to=transformers.pipelines
# nuitka-project: --nofollow-import-to=transformers.tools
# nuitka-project: --nofollow-import-to=transformers.benchmark
# nuitka-project: --nofollow-import-to=torch._dynamo
# nuitka-project: --nofollow-import-to=matplotlib
# nuitka-project: --nofollow-import-to=av
# nuitka-project: --nofollow-import-to=pyphen
# nuitka-project: --assume-yes-for-downloads

## nuitka-project: --plugin-disable=transformers
## nuitka-project: --include-package=transformers.models.albert
## nuitka-project: --include-module=transformers.models.albert.configuration_albert
## nuitka-project: --include-module=transformers.models.albert.modeling_albert

# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/.venv/Lib/site-packages/openvino/libs=openvino/libs
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/.venv/Lib/site-packages/openvino_tokenizers/lib=openvino_tokenizers/lib

# nuitka-project: --include-package=kokoro
# nuitka-project: --include-package-data=kokoro

# nuitka-project: --include-distribution-metadata=transformers

# nuitka-project: --spacy-language-model=en_core_web_sm

if __name__ == "__main__":
    # for game player
    # import sys
    # import gamePlayer
    # from src import myGestureRecognizer
    from src.gui_game_player import playerPage

    #
    # if len(sys.argv) > 1:
    #     player = gamePlayer.GamePlayer()
    #     player.play_game(sys.argv[1])
    # else:
    playerPage.run()

    # for game engine
    # import kokoro
    # from src.gui.homePage import run
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
    #
    # with open(os.path.join(os.path.dirname(__file__), "game_generation_local_llm\\generated_games", "bed_story_serial.json"), 'r') as file:
    #     serialized_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())
    # saver = GameSaver()
    # saver.save_game(os.path.join(os.path.dirname(__file__), "saved_games"), "Bed story", serialized_graph)

    # for structured output
    # from game_generation_local_llm import structured_output
    # structured_output.main()

