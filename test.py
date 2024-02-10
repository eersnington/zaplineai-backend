from transformers import BertForSequenceClassification, BertTokenizer, TextClassificationPipeline

import time
# llm_model = LLMModel()

# chat = LLMChat(llm_model)


# while True:
#     inp = input("Enter your prompt: ")
#     start = time.time()
#     output = chat.generate_response(inp)
#     print(f"{output}\n\nTime taken: {time.time() - start}s")
model_path = "Sreenington/BERT-Ecommerce-Classification"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)

while True:
    inp = input("Enter your prompt: ")
    start = time.time()
    output = pipeline(inp)
    print(f"{output}\n\nTime taken: {time.time() - start}s")
