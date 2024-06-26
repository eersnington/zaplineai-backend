import logging
logging.getLogger().setLevel(logging.INFO)
from lib.call_chat import CallChatSession
import torch
import time

bot_name = "Sunny"
store_name = "Brandify"
additional_instruct = "When introducing yourself to the customer, say there's a sale of 40% ongoing inline."

llmchat = CallChatSession(app_token="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", 
                          myshopify="quickstart-eabc790f", 
                          bot_name=bot_name, 
                          brand_name=store_name)
print(f"GPU Memory Usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

llmchat.start("1234", "+919952062221")

first_response = "Hey there! I'm {bot_name}, your virtual assistant from {store_name}. What can I help you with today?"
llmchat.llm_chat.add_message("Assistant", first_response)

print(f"Assistant: {first_response}")

while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    
    start = time.time()
    response = llmchat.get_response(user_input)
    end = time.time()
    print(f"Assistant: {response}")
    print(f"Time taken: {end - start:.3f} seconds")