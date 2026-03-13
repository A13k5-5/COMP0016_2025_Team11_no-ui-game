# nuitka-project: --mode=standalone

# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/models=models

# nuitka-project: --nofollow-import-to=torch._dynamo
# nuitka-project: --nofollow-import-to=matplotlib

# nuitka-project: --include-package=openvino-genai
# nuitka-project: --include-package-data=openvino-genai

# nuitka-project: --include-package=openvino
# nuitka-project: --include-package-data=openvino

# nuitka-project: --include-package=openvino-tokenizers
# nuitka-project: --include-package-data=openvino-tokenizers


import json
import os
from openvino_genai import LLMPipeline, ChatHistory, GenerationConfig, StructuredOutputConfig
from pydantic import BaseModel

class Country(BaseModel):
    name: str
    capital: str
    population: int

if __name__ == "__main__":
    config = GenerationConfig()
    config.temperature = 0.1
    config.max_new_tokens = 40
    config.structured_output_config = StructuredOutputConfig(json_schema=json.dumps(Country.model_json_schema()))

    history = ChatHistory()
    history.append({"role": "system", "content": "You are a helpful assistant."})

    print("Loading model...")
    model_path: str = os.path.join(os.path.dirname(__file__), "models", "TinyLlama-1.1B-Chat-v1.0_ov")
    pipe: LLMPipeline = LLMPipeline(model_path, "GPU")
    while True:

        prompt: str = input(">> ")
        if prompt == "bye":
            break

        history.append({"role": "user", "content": prompt})

        print("Generating response...")
        decoded_results = pipe.generate(history, config)
        print(decoded_results.texts[0])

        history.pop()
