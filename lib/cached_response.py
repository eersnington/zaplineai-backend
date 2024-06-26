import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# class VectorDatabase:
#     def __init__(self):
#         self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#         self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
#         self.index = faiss.IndexFlatL2(self.dim)
#         self.cached_responses = {
#             "I want to check on it's status": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I wanna know the status": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you tell me the status of my order?": "Of course! I can do that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where is my order?": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What's the status of my order?": "I can check that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What is the shipping status of my order?": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What is the shipment status?": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where's my order?": "Alright! Based on our records, <<explain the current status of your order>> Do you need any other help?",            
#             "Where is my package?": "Alright! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where is my shipment?": "Alright! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where are my items?": "Alright! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "My order hasn't arrived yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I haven't got my order yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I haven't got my package yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I haven't got my shipment yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I haven't received my order yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",            
#             "I haven't received my package yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I haven't received my shipment yet": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you update me on my order?": "No worries! I'll check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What's the current status of my order?": "Let me find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm wondering about the status of my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Has my order been shipped?": "Let me check for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "When can I expect my order to arrive?": "I'll find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm checking on my order's delivery status.": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you track my order for me?": "Certainly! I'll track it for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'd like an update on my order's shipping status.": "I'll get that update for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where is my order currently?": "Let me find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm concerned about my order. Can you help?": "Of course! I'll look into it for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I need to know when my order will be delivered.": "I'll check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What's the deal with my order?": "Let me check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm curious about my order status.": "I'll find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm calling about my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you check on my order?": "Sure thing! I'll check on it for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I want to know when my order will arrive.": "I'll find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What's the status of my package?": "Let me check for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where's my stuff?": "I'll find out where it is. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm still waiting for my order.": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "When can I expect my order?": "Let me check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I need an update on my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm calling about my delivery.": "Sure, I'll check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you provide an update on my order?": "Of course, I'll look into that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I want to know when my package will arrive.": "Let me check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "What's going on with my order?": "I'll find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I need to track my order.": "Of course! Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm waiting for my order.": "Sorry to hear that. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Can you check the status of my shipment?": "Sure thing! I'll check on it for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "Where is my order now?": "Let me find out for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I'm trying to find out when my order will be delivered.": "I'll check on that for you. Based on our records, <<explain the current status of your order>> Do you need any other help?",
#             "I need to know when to expect my order.": "Sure thing! Based on our records, <<explain the current status of your order>> Do you need any other help?",


#             "I wanna return it": "Sure thing! Could you please let me know why you're returning the order?",
#             "I wanna refund it": "No worries!  Can you tell me what's the reason for requesting a refund?",
#             "I want to return a product": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I need to return my order": "No problem! Can you tell me what's the reason for returning the order?",
#             "I want to return my order": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I want to refund my order": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I need to refund my order": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I need a refund": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "Can I get a refund?": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I'd like to return an item": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "How do I return my order?": "Sure thing! Can you tell me what's the reason for requesting a refund?",
#             "I want to get a refund": "I can assist you with that. Can you tell me what's the reason for requesting a refund?",
#             "Well I want to refund it now": "Sure thing! Can you tell me what's the reason for requesting a refund?",
#             "Well I wanna return my order": "Sure thing! I'll help you with a return. Can you tell me what's the reason for returning the order?",
#             "I wanna return my order": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I wanna return my package": "No worries! Can you tell me what's the reason for returning the order?",
#             "I wanna return my shipment": "No worries! Can you tell me what's the reason for returning the order?",
#             "I wanna refund my order": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I wanna refund my package": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I wanna refund my shipment": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I'd like to return something I ordered": "No worries! Can you tell me what's the reason for returning the order?",
#             "Can I return my purchase?": "No worries! Could you let me know why you'd like to return the order?",
#             "How can I return my order?": "No worries! Can you tell me what's the reason for returning the order?",
#             "Can I refund my order?": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "How can I refund my order?": "No worries! Could you please tell me why you want to refund the order?",
#             "I want to get a refund for my order": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I need to return an item": "No problem! Could you please let me know why you need to return the order?",
#             "I'd like to get a refund for my purchase": "Of course! Can you tell me what's the reason for requesting a refund?",
#             "Can you help me with a return?": "No worries! I'll be happy to assist you. Can you tell me what's the reason for returning the order?",
#             "Can you help me return it?": "No worries! Could you let me know why you're returning the order?",
#             "Can you help me with a refund?": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "Can you help me refund it?": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I want to return something I bought": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "How do I return an item?": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I need to get a refund for my order": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I want to return my recent purchase": "No worries! Can you tell me what's the reason for returning the order?",
#             "I need to refund my recent purchase": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I want to return something I received": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I want to return an item I ordered": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I want to return my recent order": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I need to refund an item": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "Can you help me return an item?": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "I need to return something I purchased": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "Start a return please": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "Start a refund please": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "Start a return.": "Sure thing! Can you tell me what's the reason for returning the order?",
#             "Start a refund.": "No worries! Can you tell me what's the reason for requesting a refund?",
#             "I want to cancel my order": "Certainly! Can you please let me know the reason for the cancellation?",


#             "I need to cancel my order": "Of course! Can you please let me know the reason for the cancellation?",
#             "Can I cancel my order?": "Certainly! Can you please let me know the reason for the cancellation?",
#             "How do I cancel my order?": "Certainly! Can you please let me know the reason for the cancellation?",
#             "Can you help me cancel my order?": "Certainly! Can you please let me know the reason for the cancellation?",
#             "I'd like to cancel my order": "Certainly! Can you please let me know the reason for the cancellation?",
#             "Cancel my order": "Certainly! Can you please let me know the reason for the cancellation?",
#             "Please cancel my order": "Certainly! Can you please let me know the reason for the cancellation?",
#             "Start a cancellation": "Certainly! Can you please let me know the reason for the cancellation?",
#             "Begin a cancellation": "Certainly! Can you please let me know the reason for the cancellation?",
            

#             "Can I talk to a sales representative?": "No worries! I can transfer your call to a sales representative right away. Please hold for a moment while I connect you.",
#             "Can I speak to someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
#             "Can I speak with someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
#             "Can I speak to a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",
#             "Can I speak with a representative?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",           
#             "Can I speak to a live agent?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",
#             "Can I speak with a live agent?": "Certainly! Let me connect you with a live representative. Please hold on for a moment.",           
#             "Can you transfer me to someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
#             "I need to talk to someone about my order": "I can connect you with a live representative who can assist you with your order. Please hold on.",
#             "Please transfer my call to a representative": "Certainly! I'll transfer your call to a live representative. Please wait for a moment.",
#             "Please transfer my call": "Sure! I'll transfer your call to a live representative right away. Please hold for a moment while I connect you.",
#             "I want to talk to someone": "I can connect you with a live representative who can assist you. Please hold on.",
#             "I want to talk with someone": "I can connect you with a live representative who can assist you. Please hold on.",
#             "I need to speak to someone": "Of course! I'll transfer you to a live representative who can assist you. Please hold on.",
#             "I need to speak with someone": "Of course! I'll transfer you to a live representative who can assist you. Please hold on.",           
#             "I need to speak with a representative": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",
#             "I need to speak to a representative": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",
#             "I need to speak with a live agent": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",   
#             "I need to speak to a live agent": "Sure! I'll transfer you to a live representative who can assist you. Please hold on.",
#             "I need to speak with a sales representative": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
#             "Can you transfer my call ": "Of course! I'll transfer your call to a live representative right away. Please hold for a moment while I connect you.",


#             "No, that's all. Thank you.": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I don't need any more assistance. Thank you.": "You're welcome! If you need help in the future, don't hesitate to contact us. Have a wonderful day! You can hangup the call now.",
#             "That's everything. Thank you.": "You're welcome! We're glad we could assist you. If you need help in the future, don't hesitate to reach out.  You can hangup the call now.",
#             "I'm all set. Thank you.": "You're welcome! If you have any more questions, feel free to contact us again. Have a lovely day! You can hangup the call now.",
#             "No, I'm good. Thank you.": "You're welcome! We're here to help whenever you need us. Have a wonderful day! You can hangup the call now.",
#             "That's all for now, thanks.": "You're welcome! If you have any more questions, feel free to contact us. Have a great day! You can hangup the call now.",
#             "I think I'm good, thanks.": "You're welcome! If you need further assistance, feel free to reach out. Have a wonderful day! You can hangup the call now.",
#             "I'm all set, thank you.": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "No, that'll be all. Thank you.": "You're welcome! If you need help in the future, don't hesitate to reach out. Have a lovely day! You can hangup the call now.",
#             "I don't need anything else, thanks.": "You're welcome! If you have any more questions, feel free to contact us. Have a wonderful day! You can hangup the call now.",
#             "I'm good for now, thank you.": "You're welcome! We're here to help whenever you need us. Have a wonderful day! Have a lovely day! You can hangup the call now.",
#             "That's it, thanks.": "You're welcome! Have a great day! You can hangup the call now.",
#             "I'm good, thank you.": "You're welcome! If you need anything else, feel free to reach out. Have a great day! You can hangup the call now.",
#             "I'm good, thanks.": "You're welcome! Have a great day! You can hangup the call now.",
#             "I think I'm all set, thanks.": "You're welcome! If you have more questions later, don't hesitate to ask. Have a great day!You can hangup the call now.",
#             "Nope, that's all. Thanks.": "You're welcome! Have a good one! You can hangup the call now.",
#             "I think I'm good for now, thanks.": "You're welcome! If you need anything else, feel free to reach out. Have a great day! You can hangup the call now.",
#             "No, I don't need help": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I'm good, thanks": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I'm all set, thanks": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "No, I'm all set": "You got it! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I'm good for now": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "That's all for now": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "No, that's all": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I'm all set": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "I'm good": "You're welcome! Have a great day! You can hangup the call now.",
#             "No, I'm good": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",
#             "I'm good, thank you": "You're welcome! Have a great day! You can hangup the call now.",
#             "I'm all set, thank you": "You're welcome! If you have any more questions, feel free to contact us. Have a lovely day! You can hangup the call now.",
#             "No, that'll be all": "You're welcome! If you have any more questions later, feel free to reach out. Have a lovely day! You can hangup the call now.",

#         }
#         # Add the stored responses to the index
#         embeddings = self.model.encode(list(self.cached_responses.keys()))
#         self.index.add(np.array(embeddings))

#     def find_similar_response(self, new_query, threshold=0.6):
#         new_embedding = self.model.encode([new_query])[0]
#         D, I = self.index.search(np.array([new_embedding]), k=1)  # Search for the most similar past response
#         similarity = 1 / (1 + D[0][0])  # Calculate similarity score

#         print("Similarity Score:", similarity)

#         if similarity > threshold:
#             similar_past_query = list(self.cached_responses.keys())[I[0][0]]
#             bot_response = self.cached_responses[similar_past_query]
#             return bot_response
#         else:
#             return None
        
#     def add_response(self, query, response):
#         self.cached_responses[query] = response
#         new_embedding = self.model.encode([query])[0]
#         self.index.add(np.array([new_embedding]))


# Cached responses for different intents
cached_intent_responses = {
    "Returns Step-2": "Thank you for sharing the reason for your return. I've started the return process for you, and someone from our team will be in touch soon to assist you further. Do you need any other help?",
    "Refund Step-2": "Thanks for letting us know why you're requesting a refund. I've initiated the refund process for you, and our team will reach out soon to assist you further. Do you need any other help?",
    "Cancellation Step-3": "Thanks for letting us know why you're requesting a cancellation. I've requested to cancel the order, and our team will reach out soon to assist you further. Do you need any other help?",
    "Cancellation Step-2": "Offer them a full refund or suggest a similar product in stock (come up with it on your own based on what the customer has ordered) with a 50$ discount.",

}

cached_order_status_responses = {
    "fulfilled": "The order is already delivered to shipping address",
    "unfulfilled": "The order being prepared for shipping",
    "partially fulfilled": "Part of your order has been delivered, and rest is on the way",
    "scheduled": "Scheduled for delivery",
    "on hold": "Order is on hold. Contact customer service trhough email or transfer this call for more information",
    "none": "I couldn't find any recent orders for this phone number. If you think this is a mistake, please call again later."
}

def get_intent_response(intent):
    """Fetches the cached response for a given intent."""
    return cached_intent_responses.get(intent)

def get_order_status_response(status):
    """Fetches the cached response for a given order status."""
    return cached_order_status_responses.get(status)


def get_example_response(intent):
    """Fetches an example response for a given intent."""
    cached_example_responses = {
        "Order Status": "Say in this format- Your last order of (mention the items) on (mention date) is [explain the status]. It will arrive in [estimate the number of days].",
        "Cancellation Step-1": "Say this - I'm sorry to hear you want to cancel your order. Could you please tell me the reason for the cancellation?",
        "Cancellation Step-2": "Ask them if they want a full refund or order something else (tell any similar product) in stock with 50$ discount",
        "Cancellation Step-3": "Say this - Your cancellation request is being processed. Our support team will get back to you shortly.",
        "Returns Step-1": "Say this - I'm sorry to hear you want to return your order. Could you please tell me the reason for the return?",
        "Returns Step-2": "Say this - Your return request is being processed. Our support team will get back to you shortly.",
        "Refund Step-1": "Say this - I'm sorry to hear you're requesting a refund. Could you please tell me the reason for the refund?",
        "Refund Step-2": "Say this - Your refund request is being processed. Our support team will get back to you shortly.",
        "Product Info": "[describe the product to based on what you know about it].",
        "Transfer": "Say this - I'll transfer your call to a sales representative right away. Please hold for a moment while I connect you.",
        "Sales": "Say this - I can transfer your call right away. Please hold on for a moment while I connect you.",
        "General": "[Give a general answer]."
    }
    for item in cached_example_responses.keys():
        if item in intent:
            return cached_example_responses[item]

    return "[Give a general answer]."


# Example usage
# if __name__ == "__main__":
#     vector_db = VectorDatabase()

#     # Search for a similar response
#     while True:

#         new_query = input("Enter your query: ")
#         if new_query.lower() == "exit":
#             break

#         import time
#         start = time.time()
#         similar_response = vector_db.find_similar_response(new_query)
#         if similar_response:
#             print("Similar past response found:", similar_response)
#         else:
#             print("No similar past response found.")
#         print("Time taken:", time.time() - start)
