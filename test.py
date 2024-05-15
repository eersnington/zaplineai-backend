from lib.llm_model import ClassifierModel
from lib.llm_prompt import get_classifier_prompt
import time

classifier = ClassifierModel()

prompt = get_classifier_prompt("I want to return my order")
start = time.time()
response = classifier.classify(prompt)
end = time.time()
print(response)
print(f"Time taken: {end - start} seconds")
print(f"Throughput: {len(response) / (end - start)} tokens per second")