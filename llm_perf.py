from lib.llm_model import LLMModel
import time

llm_model = LLMModel()
start = time.time()

while True:
    # Generate text using the LLM model
    text = input("Enter your message: ")
    llm_model.generate_text(text)
        
    end = time.time()
    print(f"Time taken: {end - start} seconds")

