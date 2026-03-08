#!/usr/bin/env python3
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from graph.serial_graph import SerialGraph
from prompts import SYS_MESSAGE



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_dir", help="Path to the model directory. It should contain the OpenVINO model files.")
    args = parser.parse_args()

    device = "CPU"  # GPU can be used as well
    pipe = LLMPipeline(args.model_dir, device)

    config = GenerationConfig()

    print(
        "This is a smart assistant that generates an adventure game graph."
    )

    while True:
        try:
            prompt = input("> ")
        except EOFError:
            break

        if prompt in ["exit", "quit", "bye"]:
            break

        # configuring the system message and the structured output config for the pipeline
        history = ChatHistory()
        history.append({"role": "system", "content": SYS_MESSAGE})

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