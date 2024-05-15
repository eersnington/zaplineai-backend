from lib.llm_model import ClassifierModel
from lib.llm_prompt import get_classifier_prompt

classifier = ClassifierModel()

prompt = get_classifier_prompt("I want to return my order")
response = classifier.classify(prompt)
print(response)