import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

cached_intent_responses = {
    "Order Status": "Of course! I can do that for you. Based on our records, <<explain the current status of your order>>",
    "Returns Step1": "I'd be happy to help with your return! Could you please let me know why you're returning the item? Once I have this information, I'll start the return process for you and our team will reach out shortly.",
    "Returns Step2": "Thank you for sharing the reason for your return. I've started the return process for you, and someone from our team will be in touch soon to assist you further. Is there anything else I can assist you with?",
    "Refund Step1": "I'm here to assist you with your refund! Could you please provide me with the reason for the refund? Once I have this information, I'll initiate the refund process for you, and our team will be in touch shortly.",
    "Refund Step2": "Thanks for letting us know why you're requesting a refund. I've initiated the refund process for you, and our team will reach out soon to assist you further. Is there anything else I can do for you?",
    "Sales": "Absolutely! I can transfer your call to a live representative right away. Please hold for a moment while I connect you.",
    "Transfer": "Certainly! Let me connect you with a live representative. Please hold on for a moment."
}

cached_order_status_responses = {
    "Fulfilled": "Your order has been successfully delivered to your shipping address.",
    "Unfulfilled": "Our team is currently processing and preparing your order for shipping. We'll notify you once it's on its way.",
    "Partially Fulfilled": "Part of your order has been delivered, and we're working diligently to ship the remaining items as soon as possible.",
    "Scheduled": "Your order is scheduled for delivery. You will receive an email with the estimated time of arrival shortly.",
    "On hold": "Your order is currently on hold. Please reach out to our team via email so we can assist you in resolving this matter."
}

# Store data in Redis
for intent, message in cached_intent_responses.items():
    r.hset("intents", intent, message)

for key, message in cached_order_status_responses.items():
    r.hset("order_status_responses", key, message)


def get_intent_response(intent):
    """Fetches the cached response for a given intent."""
    message = r.hget("intents", intent)
    if message:
        return message.decode('utf-8')
    else:
        return None

def get_order_status_response(status):
    """Fetches the cached response for a given order status."""
    message = r.hget("order_status_responses", status)
    if message:
        return message.decode('utf-8')
    else:
        return None

# Example usage
import time
start = time.time()
print(get_intent_response("Sales"))
print(get_order_status_response("Fulfilled"))
redis_time = time.time() - start
print("Time taken:", redis_time)


start = time.time()
print(cached_intent_responses["Sales"])
print(cached_order_status_responses["Fulfilled"])
dict_time = time.time() - start
print("Time taken:", dict_time)


if redis_time < dict_time:
    print("Redis is faster!")
else:
    print("Dictionary is faster!")