import json
import os
from openvino_genai import LLMPipeline, ChatHistory, GenerationConfig, StructuredOutputConfig
from pydantic import BaseModel

class Country(BaseModel):
    name: str
    capital: str
    population: int

if __name__ == "__main__":
    model_path: str = os.path.join(os.path.dirname(__file__), "models", "TinyLlama_1_1b_v1_ov")
    prompt: str = "What is the capital of England? And what is its population?"

    config = GenerationConfig()
    config.temperature = 0.1
    config.max_new_tokens = 40
    config.structured_output_config = StructuredOutputConfig(json_schema=json.dumps(Country.model_json_schema()))

    history = ChatHistory()
    history.append({"role": "system", "content": "You are a helpful assistant."})
    history.append({"role": "user", "content": prompt})

    print("Loading model...")
    pipe: LLMPipeline = LLMPipeline(model_path, "GPU")
    print("Model loaded. Generating response...")
    decoded_results = pipe.generate(history, config)
    print(decoded_results.texts[0])
