from lib.llm_bot import LLMModel
import time
llm_model = LLMModel()

start = time.time()
print(llm_model.generate_text("Hello, how are you?"))

print(f"Time taken: {time.time() - start}s")
