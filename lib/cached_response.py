import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.dim = self.model.encode(["dummy"]).shape[1]  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        self.cached_responses = {
            "I wanna know the status": "I can help with that! Based on our records, <<explain the current status of your order>>",
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
            "Can you update me on my order?": "Absolutely! I'll check on that for you. Based on our records, <<explain the current status of your order>>",
            "What's the current status of my order?": "Let me find out for you. Based on our records, <<explain the current status of your order>>",
            "I'm wondering about the status of my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>>",
            "Has my order been shipped?": "Let me check for you. Based on our records, <<explain the current status of your order>>",
            "When can I expect my order to arrive?": "I'll find out for you. Based on our records, <<explain the current status of your order>>",
            "I'm checking on my order's delivery status.": "I can help with that! Based on our records, <<explain the current status of your order>>",
            "Can you track my order for me?": "Certainly! I'll track it for you. Based on our records, <<explain the current status of your order>>",
            "I'd like an update on my order's shipping status.": "I'll get that update for you. Based on our records, <<explain the current status of your order>>",
            "Where is my order currently?": "Let me find out for you. Based on our records, <<explain the current status of your order>>",
            "I'm concerned about my order. Can you help?": "Of course! I'll look into it for you. Based on our records, <<explain the current status of your order>>",
            "I need to know when my order will be delivered.": "I'll check on that for you. Based on our records, <<explain the current status of your order>>",
            "What's the deal with my order?": "Let me check on that for you. Based on our records, <<explain the current status of your order>>",
            "I'm curious about my order status.": "I'll find out for you. Based on our records, <<explain the current status of your order>>",
            "I'm calling about my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>>",
            "Can you check on my order?": "Sure thing! I'll check on it for you. Based on our records, <<explain the current status of your order>>",
            "I want to know when my order will arrive.": "I'll find out for you. Based on our records, <<explain the current status of your order>>",
            "What's the status of my package?": "Let me check for you. Based on our records, <<explain the current status of your order>>",
            "Where's my stuff?": "I'll find out where it is. Based on our records, <<explain the current status of your order>>",
            "I'm still waiting for my order.": "I'm sorry to hear that. Let me check on it for you. Based on our records, <<explain the current status of your order>>",
            "When can I expect my order?": "Let me check on that for you. Based on our records, <<explain the current status of your order>>",
            "I need an update on my order.": "No problem! I'll look into that for you. Based on our records, <<explain the current status of your order>>",
            "I'm calling about my delivery.": "Sure, I'll check on that for you. Based on our records, <<explain the current status of your order>>",
            "Can you provide an update on my order?": "Of course, I'll look into that for you. Based on our records, <<explain the current status of your order>>",
            "I want to know when my package will arrive.": "Let me check on that for you. Based on our records, <<explain the current status of your order>>",
            "What's going on with my order?": "I'll find out for you. Based on our records, <<explain the current status of your order>>",
            "I need to track my order.": "I can help with that! Based on our records, <<explain the current status of your order>>",
            "I'm waiting for my order.": "I'm sorry to hear that. Let me check on it for you. Based on our records, <<explain the current status of your order>>",
            "Can you check the status of my shipment?": "Sure thing! I'll check on it for you. Based on our records, <<explain the current status of your order>>",
            "Where is my order now?": "Let me find out for you. Based on our records, <<explain the current status of your order>>",
            "I'm trying to find out when my order will be delivered.": "I'll check on that for you. Based on our records, <<explain the current status of your order>>",
            "I need to know when to expect my order.": "I'll find out for you. Based on our records, <<explain the current status of your order>>",

            "I wanna return it": "I'd be happy to help with your return! Could you please let me know why you're returning the order?",
            "I wanna refund it": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're refunding the order?",
            "I want to return a product": "I'd be happy to help with your return! Could you please let me know why you're returning the item?",
            "I need to return my order": "No problem! Could you please let me know why would you like to return the order?",
            "I want to return my order": "I'd be happy to help with your return! May I know why you would like to return your order? Was there any issue with the product or the delivery?",
            "I want to refund my order": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "I need to refund my order": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "I need a refund": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "Can I get a refund?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why do you want to refund?",
            "I'd like to return an item": "I'm here to assist you with your return. Can you please provide me with the reason for the return?",
            "How do I return my order?": "I'd be happy to help with your return. Could you please provide me with the reason for the refund?",
            "I want to get a refund": "I can assist you with that. Could you please provide me with the reason for the refund?",
            "Well I want to refund it now": "I apologize for any inconvenience you've experienced with your order. May I know why you would like to refund it now? Was there any issue with the product or the delivery?",
            "Well I wanna return my order": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're returning the item?",
            "I wanna return my order": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're returning the item?",
            "I wanna return my package": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're returning the item?",
            "I wanna return my shipment": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're returning the item?",
            "I wanna refund my order": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're refunding the item?",
            "I wanna refund my package": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're refunding the item?",
            "I wanna refund my shipment": "I apologize for any inconvenience you've experienced with your order. Could you please let me know why you're refunding the item?",
            "I'd like to return something I ordered": "I'd be happy to assist with that. Could you please provide me with the reason for the return?",
            "Can I return my purchase?": "Absolutely! I just need a bit more information to process your return. Could you let me know why you'd like to return the item?",
            "How can I return my order?": "I'll be glad to help you with that. Could you please tell me why you want to return the order?",
            "Can I refund my order?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why you're requesting a refund?",
            "How can I refund my order?": "I'll be glad to help you with that. Could you please tell me why you want to refund the order?",
            "I want to get a refund for my order": "I can help with that. Could you please provide me with the reason for the refund?",
            "I need to return an item": "No problem! Could you please let me know why you need to return the item?",
            "I'd like to get a refund for my purchase": "Of course! I just need a bit more information to process your refund. Could you let me know why you're requesting a refund?",
            "Can you help me with a return?": "Absolutely! I'll be happy to assist you. Could you please tell me why you're returning the item?",
            "Can you help me return it?": "Absolutely! I just need a bit more information to process your return. Could you let me know why you're returning the item?",
            "Can you help me with a refund?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why you're requesting a refund?",
            "Can you help me refund it?": "Absolutely! I just need a bit more information to process your refund. Could you let me know why you're requesting a refund?",
            "I want to return something I bought": "I'd be happy to help with your return! Could you please let me know why you're returning the item?",
            "How do I return an item?": "I'd be happy to help with your return. Can you please provide me with the reason for the return?",
            "I need to get a refund for my order": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund?",
            "I want to return my recent purchase": "I'm here to assist you with your return. Can you please provide me with the reason for the return?",
            "I need to refund my recent purchase": "I'm here to assist you with your refund. Could you please provide me with the reason for the refund?",
            "I want to return something I received": "I'd be happy to help with your return. Could you please let me know why you're returning the item?",
            "I want to return an item I ordered": "I'd be happy to help with your return. Can you please provide me with the reason for the return?",
            "I want to return my recent order": "I'd be happy to help with your return. Can you please provide me with the reason for the return?",
            "I need to refund an item": "I'm here to assist you with your refund. Could you please provide me with the reason for the refund?",
            "Can you help me return an item?": "I'd be happy to help with your return. Can you please provide me with the reason for the return?",
            "I need to return something I purchased": "I'd be happy to help with your return. Can you please provide me with the reason for the return?",


            "Can I talk to a sales representative?": "Absolutely! I can transfer your call to a live representative right away. Please hold for a moment while I connect you.",
            "Can I speak to someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
            "Can I speak with someone in sales?": "Of course! I'll transfer you to a sales representative. Please hold for a moment.",
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
        

            "No, that's all. Thank you.": "You're welcome! If you have any more questions later, feel free to reach out. You can hang up the call if you don't need any more help.",
            "I don't need any more assistance. Thank you.": "You're welcome! If you need help in the future, don't hesitate to contact us. Have a wonderful day! You can hang up the call if you don't need any more help.",
            "That's everything. Thank you.": "You're welcome! We're glad we could assist you. If you need help in the future, don't hesitate to reach out. You can hang up the call if you don't need any more help.",
            "I'm all set. Thank you.": "You're welcome! If you have any more questions, feel free to contact us again. You can hang up the call if you don't need any more help.",
            "No, I'm good. Thank you.": "You're welcome! We're here to help whenever you need us. Have a wonderful day! You can hang up the call if you don't need any more help.",
            "That's all for now, thanks.": "You're welcome! If you have any more questions, feel free to contact us. Have a great day! You can hang up the call if you don't need any more help.",
            "I think I'm good, thanks.": "You're welcome! If you need further assistance, feel free to reach out. Have a wonderful day! You can hang up the call if you don't need any more help.",
            "I'm all set, thank you.": "You're welcome! If you have any more questions, feel free to contact us. You can hang up the call if you don't need any more help.",
            "No, that'll be all. Thank you.": "You're welcome! If you need help in the future, don't hesitate to reach out. Have a great day! You can hang up the call if you don't need any more help.",
            "I don't need anything else, thanks.": "You're welcome! If you have any more questions, feel free to contact us. Have a wonderful day! You can hang up the call if you don't need any more help.",
            "I'm good for now, thank you.": "You're welcome! We're here to help whenever you need us. Have a wonderful day! You can hang up the call if you don't need any more help.",
            "That's it, thanks.": "You're welcome! Have a great day! You can hang up the call if you don't need any more help.",
            "I'm good, thank you.": "You're welcome! If you need anything else, just let us know. Have a great day! You can hang up the call if you don't need any more help.",
            "I'm good, thanks.": "You're welcome! Have a great day! You can hang up the call if you don't need any more help.",
            "I think I'm all set, thanks.": "You're welcome! If you have more questions later, don't hesitate to ask. Have a great day! You can hang up the call if you don't need any more help.",
            "Nope, that's all. Thanks.": "You're welcome! Have a good one! You can hang up the call if you don't need any more help.",
            "I think I'm good for now, thanks.": "You're welcome! If you need anything else, just give us a shout. Have a great day! You can hang up the call if you don't need any more help."


        }
        # Add the stored responses to the index
        embeddings = self.model.encode(list(self.cached_responses.keys()))
        self.index.add(np.array(embeddings))

    def find_similar_response(self, new_query, threshold=0.6):
        new_embedding = self.model.encode([new_query])[0]
        D, I = self.index.search(np.array([new_embedding]), k=1)  # Search for the most similar past response
        similarity = 1 / (1 + D[0][0])  # Calculate similarity score

        print("Similarity Score:", similarity)

        if similarity > threshold:
            similar_past_query = list(self.cached_responses.keys())[I[0][0]]
            bot_response = self.cached_responses[similar_past_query]
            return bot_response
        else:
            return None
        
    def add_response(self, query, response):
        self.cached_responses[query] = response
        new_embedding = self.model.encode([query])[0]
        self.index.add(np.array([new_embedding]))


# Cached responses for different intents
cached_intent_responses = {
    "Returns Step2": "Thank you for sharing the reason for your return. I've started the return process for you, and someone from our team will be in touch soon to assist you further. Is there anything else I can assist you with?",
    "Refund Step2": "Thanks for letting us know why you're requesting a refund. I've initiated the refund process for you, and our team will reach out soon to assist you further. Is there anything else I can do for you?",
}

cached_order_status_responses = {
    "fulfilled": "Your order has been successfully delivered to your shipping address.",
    "unfulfilled": "Our team is currently processing and preparing your order for shipping. We'll notify you once it's on its way.",
    "partially fulfilled": "Part of your order has been delivered, and we're working diligently to ship the remaining items as soon as possible.",
    "scheduled": "Your order is scheduled for delivery. You will receive an email with the estimated time of arrival shortly.",
    "on hold": "Your order is currently on hold. Please reach out to our team via email so we can assist you in resolving this matter.",
    "none": "I couldn't find any recent orders for this phone number. If you think this is a mistake, please call again later."
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
