# No-UI Game

A gesture-driven, no-GUI interactive story game engine.

## Project Overview

The app is built around a graph-based story model:
- Each node is a story scene with narrative text and two player options (left and right).
- Edges represent choices mapped to gestures.
- A game is saved as a zip archive with extension `.noui`.
- Each game archive includes `graph.json` and a set of generated .wav audio files.

There are two main parts to this project: the **game player** and the **game editor**.
The **game editor** lets you create games node by node, wire them into a branching graph, and save them as a .noui archive. It also includes an AI sidebar that lets you generate a full game graph from a text prompt or an attached story file using a local LLM.
The **game player** loads a .noui file and starts a no-GUI game, playable entirely through audio prompts and hand gesture input. The player hears each scene narrated aloud, then raises their left or right hand to make a choice. Progress is saved automatically if the player quits mid-game, and the player is offered the option to resume or restart on the next run.

## Main Components

- `gui/`: Game creation UI using PySide6 (home page, node editor canvas, AI generation panel).
- `graph/`: Core graph and serialization models.
- `game_generation_local_llm/`: Local LLM game and blueprint generation.
- `text2speech/`: Text-to-speech generation via Kokoro.
- `gamePlayer/`: Runtime player (audio playback + gesture loop).
- `myGestureRecognizer/`: Camera gesture recognition integration.
- `storageManager/`: Save/load zipped `.noui` games and progress tracking.

## Saved Game Format

A `.noui` file is a zip archive containing:
- `graph.json`: Serialized game graph.
- `audio/`: Node narration and helper prompts (`win.wav`, `lose.wav`, etc.).
- `progress.json`: Contains the node ID where the player left off.

Temporary extraction occurs under `storageManager/temporary/` during load.

## Player Settings
 
The game player has a configurable settings page accessible from `playerPage.py` via the ⚙ Settings button. Settings are persisted to `settings.json` in the project root.
 
### Input Device
Toggle between **Webcam (gesture)** and **Keyboard** input. When keyboard mode is selected, the camera is never opened.
 
### Gesture Bindings
Each game action can be mapped to any gesture via a dropdown. Available actions:
- Option Left
- Option Right
- Replay Main Text
- Replay Options Text
- Quit / Save Progress
 
### Keyboard Bindings
Each action can be mapped to a single key (type a character in the field). Default bindings:
 
| Action | Default Key |
|---|---|
| Option Left | A |
| Option Right | D |
| Replay Main Text | R |
| Replay Options Text | F |
| Quit / Save Progress | Q |

## Requirements

- Python 3.10+ (recommended for compatibility with scientific and ML deps)
- macOS (your current environment), Linux, or Windows
- Webcam access (for gesture controls)
- Speaker

## Python Dependencies

See requirements.txt. Key packages include:
- PySide6 — GUI framework
- mediapipe — gesture recognition
- openvino-genai — local LLM inference
- kokoro — text-to-speech
- soundfile, playsound3 — audio I/O
- pydantic — graph serialization

### AI Model

The local LLM generation pipeline uses OpenVINO and a local model folder:
- `game_generation_local_llm/model_path/`
Ensure that this folder remains present if you use AI generation.

To install the LocalLLM, use this command:
`huggingface-cli download "OpenVINO/phi-4-int4-ov" --local-dir game_generation_local_llm/model_path`

The main contribution is the package `game_generation_local_llm`. There you can find two components:

1. `graph_blueprint` - which is responsible for blueprint generation. A blueprint is the general structure of the Graph of the game. Based on users prompt, the LLM is prompted to create a blueprint of the structure of the graph.

2. `story_generator` - after a blueprint is generated, it is passed to StoryGenerator, that generates the actual contents of each individual node.

To connect these 2 packages together, a class `GameGenerator` is created, that simply takes these two classes and uses them together, exposing a public method `generate_game`, which takes in an optional `blueprint`. If `blueprint` not provided, it generates it.

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

a. For No-GUI game engine:
```bash
pip install -r ./requirements/game_engine_requirements.txt
```

b. For No-GUI game player:
```bash
pip install -r ./requirements/game_player_requirements.txt
```

3. (Optional) Download the LLM model for AI generation - as instructed above.

## Running the Project

Default entrypoint:

```bash
python main.py
```

Current `main.py` launches the GUI creator (`gui.homePage`).

### Create or Edit a Game

1. Run `python NO_GUI_engine.py`.
2. Choose:
- `Create a New Game` to start from scratch.
- `Edit Game` to load an existing `.noui` file.
3. Add/edit nodes and links.
4. Save as a `.noui` game archive.

### Play a Saved Game

You can run the player flow by launching `playerPage.py`:

```bash
python NO_GUI_player.py
```

Then:
1. Browse for a `.noui` file.
2. Run and play using gestures.

OR you can run the game directly from the terminal:

```bash
python NO_GUI_player.py path/to/your_game.noui
```

## Development Notes

- Entry script: `main.py`
- Sample games: `saved_games/`
- LLM test outputs: `game_generation_local_llm/generated_games/`
