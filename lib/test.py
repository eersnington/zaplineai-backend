import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        self.cached_responses = {
            "How can I track my order?": "Of course! I can do that for you. Based on our records, <<explain the current status of your order>>",
            "I want to return a product": "I'd be happy to help with your return! Could you please let me know why you're returning the item? Once I have this information, I'll start the return process for you and our team will reach out shortly.",
            "I'm returning a product": "Thank you for sharing the reason for your return. I've started the return process for you, and someone from our team will be in touch soon to assist you further. Is there anything else I can assist you with?",
            "I need a refund": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund? Once I have this information, I'll initiate the refund process for you, and our team will be in touch shortly.",
            "I want my money back": "Thanks for letting us know why you're requesting a refund. I've initiated the refund process for you, and our team will reach out soon to assist you further. Is there anything else I can do for you?",
            "Can I talk to a sales representative?": "Absolutely! I can transfer your call to a live representative right away. Please hold for a moment while I connect you.",
            "Can I speak to a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment."
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
    new_query = "I want to return an item"
    similar_response = vector_db.find_similar_response(new_query)
    if similar_response:
        print("Similar past response found:", similar_response)
    else:
        print("No similar past response found.")
