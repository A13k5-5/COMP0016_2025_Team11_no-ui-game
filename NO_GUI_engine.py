# nuitka-project: --mode=standalone
# nuitka-project: --windows-disable-console

# for pyside6
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml

# recognizer file
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/src/myGestureRecognizer/gesture_recognizer.task=src/myGestureRecognizer/gesture_recognizer.task

# --------------- FOR TTS ----------------
# nuitka-project: --nofollow-import-to=transformers.generation.tf_utils
# nuitka-project: --nofollow-import-to=transformers.generation.flax_utils
# nuitka-project: --nofollow-import-to=torch._dynamo
# nuitka-project: --nofollow-import-to=matplotlib

# nuitka-project: --module-parameter=torch-disable-jit=yes

# make SURE to run phonemizer_alias before compiling

# nuitka-project: --include-distribution-metadata=phonemizer
# nuitka-project: --include-distribution-metadata=phonemizer-fork
# nuitka-project: --include-distribution-metadata=spacy
# nuitka-project: --spacy-language-model=en_core_web_sm

# --------------- FOR OPENVINO ----------------
# nuitka-project: --include-package=openvino_genai
# nuitka-project: --include-package-data=openvino_genai

# nuitka-project: --include-package=openvino_tokenizers
# nuitka-project: --include-package-data=openvino_tokenizers

from src.game_engine.gui import homePage

if __name__ == "__main__":
    homePage.run()
