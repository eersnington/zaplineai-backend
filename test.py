from lib.llm_model import BERTClassifier
import time
# llm_model = LLMModel()

# chat = LLMChat(llm_model)

# while True:
#     inp = input("Enter your prompt: ")
#     start = time.time()
#     output = chat.generate_response(inp)
#     print(f"{output}\n\nTime taken: {time.time() - start}s")

bert = BERTClassifier()

while True:
    inp = input("Enter your prompt: ")
    start = time.time()
    output = bert.classify(inp)
    print(f"{output}\n\nTime taken: {time.time() - start}s")
