import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        self.cached_responses = {
            "Can you tell me the status of my order?": "Of course! I can do that for you. Based on our records, <<explain the current status of your order>>",
            "Where is my order?": "I can help with that! Based on our records, <<explain the current status of your order>>",
            "What's the status of my order?": "I can check that for you. Based on our records, <<explain the current status of your order>>",
            "What is the shipping status of my order?": "I can help with that! Based on our records, <<explain the current status of your order>>",
            "What is the shipment status?": "I can help with that! Based on our records, <<explain the current status of your order>>",
            "Where's my order?": "Let me look into that for you. Based on our records, <<explain the current status of your order>>",            
            "Where is my package?": "Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "Where is my shipment?": "Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "Where are my items?": "Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "My order hasn't arrived yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "I haven't got my order yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "I haven't got my package yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "I haven't got my shipment yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "I haven't received my order yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",            
            "I haven't received my package yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",
            "I haven't received my shipment yet": "I'm sorry to hear that. Let me look into that for you. Based on our records, <<explain the current status of your order>>",


            "I want to return a product": "I'd be happy to help with your return! Could you please let me know why you're returning the item?",
            "I need to return my order": "No problem! Could you please let me know why you're returning the order?",
            "I want to return my order": "I'd be happy to help with your return! Could you please let me know why you're returning your order?",
            "I want to refund my order": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "I need to refund my order": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "I need a refund": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "Can I get a refund?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why do you want to refund?",
            "Can I talk to a sales representative?": "Absolutely! I can transfer your call to a live representative right away. Please hold for a moment while I connect you.",
            "I'd like to return an item": "I'm here to assist you with your return. Can you please provide me with the reason for the return?",
            "How do I return my order?": "I'd be happy to help with your return. Could you please provide me with the reason for the refund?",
            "I want to get a refund": "I can assist you with that. Could you please provide me with the reason for the refund?",
            
            
            "Can I speak to a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",
            "Can I speak with a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",           
            "Can I speak to a live agent?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",
            "Can I speak with a live agent?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",           
            "Can you transfer me to someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
            "I need to talk to someone about my order": "I can connect you with a representative who can assist you with your order. Please hold on.",
            "Please transfer my call to a representative": "Certainly! I'll transfer your call to a representative. Please wait for a moment.",
            "Please transfer my call": "Sure! I'll transfer your call to a live representative right away. Please hold for a moment while I connect you.",
            "I want to talk to someone": "I can connect you with a representative who can assist you. Please hold on.",
            "I want to talk with someone": "I can connect you with a representative who can assist you. Please hold on.",
            "I need to speak to someone": "Of course! I'll transfer you to a representative who can assist you. Please hold on.",
            "I need to speak with someone": "Of course! I'll transfer you to a representative who can assist you. Please hold on.",           
            "I need to speak with a representative": "Sure! I'll transfer you to a representative who can assist you. Please hold on.",
            "I need to speak to a representative": "Sure! I'll transfer you to a representative who can assist you. Please hold on.",
            "I need to speak with a live agent": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",   
            "I need to speak to a live agent": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",
            "I need to speak with a sales representative": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
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


# Cached responses for different intents
cached_intent_responses = {
    "Returns Step2": "Thank you for sharing the reason for your return. I've started the return process for you, and someone from our team will be in touch soon to assist you further. Is there anything else I can assist you with?",
    "Refund Step2": "Thanks for letting us know why you're requesting a refund. I've initiated the refund process for you, and our team will reach out soon to assist you further. Is there anything else I can do for you?",
}

cached_order_status_responses = {
    "Fulfilled": "Your order has been successfully delivered to your shipping address.",
    "Unfulfilled": "Our team is currently processing and preparing your order for shipping. We'll notify you once it's on its way.",
    "Partially Fulfilled": "Part of your order has been delivered, and we're working diligently to ship the remaining items as soon as possible.",
    "Scheduled": "Your order is scheduled for delivery. You will receive an email with the estimated time of arrival shortly.",
    "On hold": "Your order is currently on hold. Please reach out to our team via email so we can assist you in resolving this matter."
}

def get_intent_response(intent):
    """Fetches the cached response for a given intent."""
    return cached_intent_responses.get(intent)

def get_order_status_response(status):
    """Fetches the cached response for a given order status."""
    return cached_order_status_responses.get(status)


# Example usage
if __name__ == "__main__":
    vector_db = VectorDatabase()

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
