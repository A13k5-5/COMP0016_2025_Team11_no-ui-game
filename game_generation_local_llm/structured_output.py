import argparse
import json
import os

from openvino_genai import LLMPipeline

from game_generation_local_llm.game_generator import GameGenerator
from graph.serial_graph import SerialGraph
from game_generation_local_llm.story_generator.story_generator import StoryGenerator
from game_generation_local_llm.graph_blueprint.blueprint import GraphBlueprint
from game_generation_local_llm.graph_blueprint.blueprint_generator import BlueprintGenerator


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("model_dir",
    #                     help="Path to the model directory. It should contain the OpenVINO model files.")
    # args = parser.parse_args()

    # pipe: LLMPipeline = LLMPipeline(args.model_dir, "CPU")
    # blueprint_generator: BlueprintGenerator = BlueprintGenerator(pipe)
    # game_generator: StoryGenerator = StoryGenerator(pipe)

    game_generator: GameGenerator = GameGenerator()

    print(
        "This is a smart assistant that generates an adventure game graph."
    )

    while True:
        prompt = input("> ")

        if prompt in ["exit", "quit", "bye"]:
            break

        # blueprint = blueprint_generator.generate_blueprint(prompt)
        # print(f"\nGenerated blueprint: \n{blueprint.model_dump_json(indent=2)}")

        with open(os.path.join(os.path.dirname(__file__), "graph_blueprint", "generated_blueprint.json"), "r") as f:
            blueprint_json: dict = json.load(f)

        blueprint: GraphBlueprint = GraphBlueprint.model_validate(blueprint_json)
        print(blueprint.model_dump_json(indent=2))

        # story: SerialGraph = game_generator.generate_game(prompt, blueprint)
        story: SerialGraph = game_generator.generate_game(prompt)
        print(f"\nGenerated story graph: \n{story.model_dump_json(indent=2)}")


if "__main__" == __name__:
    main()
