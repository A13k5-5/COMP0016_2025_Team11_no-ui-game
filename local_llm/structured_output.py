"""
Entry point for the local LLM game-generation pipeline.

Run with:
    python structured_output.py <path_to_model_dir>
"""
import argparse
import json

from openvino_genai import LLMPipeline

from game_generator import GameGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a text-adventure game using a local LLM."
    )
    parser.add_argument(
        "model_dir",
        help="Path to the OpenVINO model directory.",
    )
    args = parser.parse_args()

    pipe = LLMPipeline(args.model_dir, "GPU")
    generator = GameGenerator(pipe)

    print(
        "Local LLM game generator ready. "
        "Describe your game and press Enter (Ctrl-D to quit)."
    )

    while True:
        try:
            prompt = input("> ").strip()
        except EOFError:
            break

        if not prompt:
            continue

        nodes = generator.generate(prompt)

        print("\n=== Full game graph ===")
        print(json.dumps(nodes, indent=2))


if __name__ == "__main__":
    main()
