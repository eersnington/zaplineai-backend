import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        self.cached_responses = {
            "How can I track my order?": "You can track your order by logging into your account and checking the order status.",
            "Do you offer refunds?": "Yes, we offer refunds within 30 days of purchase. Please contact our support team for assistance.",
            "What payment methods do you accept?": "We accept credit cards, PayPal, and bank transfers for payment."
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
    new_query = "How do I get a refund?"
    import time
    start = time.time()
    similar_response = vector_db.find_similar_response(new_query)
    if similar_response:
        print("Similar past response found:", similar_response)
    else:
        print("No similar past response found.")

    print("Time taken:", time.time() - start)
