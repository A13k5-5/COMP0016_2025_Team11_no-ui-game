from config import model_path
from llama_index.llms.openvino_genai import OpenVINOGenAILLM


if __name__ == "__main__":
  ov_llm: OpenVINOGenAILLM = OpenVINOGenAILLM(
      model_path=model_path,
      device="GPU"
  )

  ov_llm.config.max_new_tokens = 100

  response = ov_llm.complete("Who is the president of the United States?")
  print(str(response))
