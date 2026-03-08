#!/usr/bin/env python3
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import argparse
import json

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory
from pydantic import BaseModel

from enum_gesture import EnumGesture


class SerialNode(BaseModel):
    id: int
    text: str
    left_option: str = ""
    right_option: str = ""
    adjacency_list: dict[EnumGesture, int]
    is_win: bool = False

class SerialGraph(BaseModel):
    nodes: dict[int, SerialNode]

sys_message: str = (
    "You generate JSON objects based on the user's request. You will generate a list of JSON objects that follow the SerialNode schema. "
    "A SerialNode object represents a node in a graph of a text-based game. The user will give you their ideas"
    " about how many nodes should be in the game, and what should be their high-level content. "
    "It is your job to generate the full story. Make sure to follow the JSON schema for the SerialNode. "
    "To help you understand the SerialNode class better, i will explain what each field means: "
    "- id: a unique integer identifier for the node. It should start from 0 and increment by 1 for each new node. "
    "- text: the text that will be shown to the player when they reach this node."
    "- left_option: the text that will be shown to the player for the left option. This field can be empty if there is no left option. "
    "- right_option: the text that will be shown to the player for the right option."
    "adjacency_list: a dictionary that maps the player's choice left(1) or right(0) to the id of the next node. "    
    "it is absolutely necessary to make sure that the id of the next node exists in the generated JSON objects. "
    "- is_win: a boolean that indicates whether this node is a winning node or not."
    "Please use double quotes for JSON keys and values. "
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_dir", help="Path to the model directory. It should contain the OpenVINO model files.")
    args = parser.parse_args()

    device = "CPU"  # GPU can be used as well
    pipe = LLMPipeline(args.model_dir, device)

    config = GenerationConfig()

    print(
        "This is a smart assistant that generates structured output in JSON format. "
        "You can ask to generate information about a person, car, or bank transaction. "
        'For example, you can ask: "Please generate jsons for 3 persons and 1 transaction."'
    )

    while True:
        try:
            prompt = input("> ")
        except EOFError:
            break

        # configuring the system message and the structured output config for the pipeline
        history = ChatHistory()
        history.append({"role": "system", "content": sys_message})
        config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(SerialGraph.model_json_schema())
        )
        config.do_sample = True
        config.temperature = 0.8
        history.append({"role": "user", "content": prompt})

        decoded_results = pipe.generate(history, config)
        json_response = decoded_results.texts[0]
        print(json_response)


if "__main__" == __name__:
    main()