from lib.call_chat import CallChatSession
from lib.llm_prompt import get_chat_prompt
from lib.cached_response import get_example_response
import torch



bot_name = "Sunny"
store_name = "Sunshine Swimsuits"
additional_instruct = "When introducing yourself to the customer, say there's a sale of 40% ongoing inline."

llmchat = CallChatSession(app_token="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", 
                          myshopify="b59bb6-2", 
                          bot_name=bot_name, 
                          brand_name=store_name)
print(f"GPU Memory Usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

llmchat.start("1234", "+919952062221")

first_response = "Hey there! I'm {bot_name}, your virtual assistant from {store_name}. What can I help you with today?"
llmchat.llm_chat.add_message("Assistant", first_response)

while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    
    response = llmchat.get_response(user_input)
    print(f"Assistant: {response}")