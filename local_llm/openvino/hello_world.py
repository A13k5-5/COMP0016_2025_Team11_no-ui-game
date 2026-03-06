import openvino_genai as ov_genai

pipe = ov_genai.LLMPipeline("TinyLlama_1_1b_v1_ov", "CPU")  # Use CPU or GPU as devices without any other code change
print(pipe.generate("What is OpenVINO?"))
