from lib.llm_model import ClassifierModel, LLMModel
from lib.llm_prompt import get_classifier_prompt, get_chat_prompt
from lib.cached_response import get_example_response
import torch
import time


classifier = ClassifierModel()
llm = LLMModel()
print(f"GPU Memory Usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

bot_name = "Sunny"
store_name = "Sunshine Swimsuits"

message_history = []
def add_message(role, content):
  message_history.append({"role": role, "content": content})

def messages_formatter(messages):
  formatted_messages = []
  for message in messages:
    formatted_messages.append(f"{message['role']}: {message['content']}")
  return '\n\n'.join(formatted_messages)

while True:
    print("")
    user_input = input("Enter your message: ")
    if user_input == "exit":
        break
    
    add_message("User", user_input)
    
    classifier_prompt = get_classifier_prompt(user_input)
    start = time.time()
    message_intent = classifier.classify(classifier_prompt)
    end = time.time()
    print(f"Message intent: {message_intent}")
    print(f"Time taken for classification: {end - start} seconds")

    example_response = get_example_response(message_intent)
    print(f"Example response: {example_response}")

    chat_prompt = get_chat_prompt(bot_name, store_name) + "\n\n" + messages_formatter(message_history)
    # print(chat_prompt + f"\n\n(Example response - {example_response})\n\nAssistant: ")
    start = time.time()
    llm_input = chat_prompt + f"\n\n(Example response that can help you frame your answer - {example_response})\n\nAssistant: "
    llm_response = llm.generate_text(llm_input)
    add_message("Assistant", llm_response)
    end = time.time()
    print(f"Generated response: {llm_response}")
    print(f"Time taken for generation: {end - start} seconds")

print("Conversation ended.")
chat_prompt = get_chat_prompt(bot_name, store_name) + "\n" + messages_formatter(message_history)
print(chat_prompt)