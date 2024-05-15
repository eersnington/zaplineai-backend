from lib.llm_model import ClassifierModel, LLMModel
from lib.llm_prompt import get_classifier_prompt, get_chat_prompt
from lib.cached_response import get_example_response
import time


classifier = ClassifierModel()
llm = LLMModel()

bot_name = "Sunny"
store_name = "Sunshine Swimsuits"

while True:
    print("")
    user_input = input("Enter your message: ")
    if user_input == "exit":
        break
    
    classifier_prompt = get_classifier_prompt(user_input)
    start = time.time()
    message_intent = classifier.classify(classifier_prompt)
    end = time.time()
    print(f"Message intent: {message_intent}")
    print(f"Time taken for classification: {end - start} seconds")

    example_response = get_example_response(message_intent)
    print(f"Example response: {example_response}")