#!/usr/bin/env python3
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import argparse
from openvino_genai import LLMPipeline

from local_llm.GameGenerator import GameGenerator



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_dir", help="Path to the model directory. It should contain the OpenVINO model files.")
    args = parser.parse_args()

    pipe: LLMPipeline = LLMPipeline(args.model_dir, "CPU")
    game_generator: GameGenerator = GameGenerator(pipe)


    print(
        "This is a smart assistant that generates an adventure game graph."
    )

    while True:
        prompt = input("> ")

        if prompt in ["exit", "quit", "bye"]:
            break

        # configuring the system message and the structured output config for the pipeline
        story: str = game_generator.generate_game(prompt)
        print(f"\nGenerated story graph: \n{story}")


if "__main__" == __name__:
    main()