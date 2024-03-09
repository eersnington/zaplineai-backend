import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        self.cached_responses = {
    "Can you tell me the status of my order?": "Of course! I can do that for you. Based on our records, <<explain the current status of your order>>",
    "Where is my order?": "I can help with that! Based on our records, <<explain the current status of your order>>",
    "I want to return a product": "I'd be happy to help with your return! Could you please let me know why you're returning the item?",
    "I need to return my order": "No problem! Could you please let me know why you're returning the item?",
    "I need a refund": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
    "Can I get a refund?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why do you want to refund?",
    "Can I talk to a sales representative?": "Absolutely! I can transfer your call to a live representative right away. Please hold for a moment while I connect you.",
    "Can I speak to a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",
    "What's the status of my order?": "Sure, I can check that for you. Based on our records, <<explain the current status of your order>>",
    "Where's my order?": "Let me look into that for you. Based on our records, <<explain the current status of your order>>",
    "I'd like to return an item": "I'm here to assist you with your return. Can you please provide me with the reason for the return?",
    "I want to return something": "Sure, I can help with that. Based on our records, <<explain the current status of your order>>",
    "How do I return my order?": "I'd be happy to help with your return. Could you please provide me with the reason for the refund?",
    "I want to get a refund": "I can assist you with that. Could you please provide me with the reason for the refund?",
    "Can you transfer me to someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
    "I need to talk to someone about my order": "I can connect you with a representative who can assist you with your order. Please hold on.",
    "Please transfer my call to a representative": "Certainly! I'll transfer your call to a representative. Please wait for a moment.",
}


        # Add the stored responses to the index
        embeddings = self.model.encode(list(self.cached_responses.keys()))
        self.index.add(np.array(embeddings))

    def find_similar_response(self, new_query, threshold=0.8):
        new_embedding = self.model.encode([new_query])[0]
        D, I = self.index.search(np.array([new_embedding]), k=1)  # Search for the most similar past response
        similarity = 1 / (1 + D[0][0])  # Calculate similarity score

        if similarity > threshold:
            similar_past_query = list(self.cached_responses.keys())[I[0][0]]
            bot_response = self.cached_responses[similar_past_query]
            return bot_response
        else:
            return None

# Example usage
if __name__ == "__main__":
    vector_db = VectorDatabase("sentence-transformers/all-MiniLM-L6-v2")

    # Search for a similar response
    while True:

        new_query = input("Enter your query: ")
        if new_query.lower() == "exit":
            break

        import time
        start = time.time()
        similar_response = vector_db.find_similar_response(new_query)
        if similar_response:
            print("Similar past response found:", similar_response)
        else:
            print("No similar past response found.")
        print("Time taken:", time.time() - start)
