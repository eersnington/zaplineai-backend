from lib.llm_bot import LLMModel, LLMChat
import time
llm_model = LLMModel()

chat = LLMChat(llm_model)


while True:
    start = time.time()
    print(f"Time taken: {time.time() - start}s")
