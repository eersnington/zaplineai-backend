from lib.llm_bot import LLMModel, LLMChat
import time
llm_model = LLMModel()

chat = LLMChat(llm_model)


while True:
    inp = input("Enter your prompt: ")
    start = time.time()
    output = chat.generate_response(inp)
    print(f"{output}\n\nTime taken: {time.time() - start}s")
