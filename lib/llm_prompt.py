""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

from typing import List, Union


classifier_prompt = """<|user|>
Classify a customer query from an e-commerce Shopify Store chat into the defined categories below.
I have defined each class.

Classes:
1. Order Status - Asking about the status of their order
2. Returns - Wanting to return an order
3. Refund - Wanting to refund an order
4. Cancellation - Wanting to cancel an order
5. Product Info - Asking about a product
6. Sales - Wanting to buy something
7. Transfer - Wanting to Transfer their call
8. General - A general message that doesn't fall into other categories

Customer Query to Classify: {user_query}

Only tell the name of the class the query falls under.
<|end|>
<|assistant|>
"""

def get_classifier_prompt(user_query: str) -> str:
    return classifier_prompt.format(user_query=user_query)

system_prompt = "System: You are {bot_name}, the personal AI assistant for {store_name}. This is a chat between the AI assistant and the user. The assistant provides friendly answers to the user's questions based on the context provided."
context = """Your scope is as follows: You can answer questions related to order status, handle returns, refunds or cancellations.
Context of {store_name}: Is a an e-commerce brand that clothes.
Context of the user - This user placed an Order on {date} with the item {order_items}.
The status of the order - {order_status}.
Refund, Returns and Cancellation is possible. Ask for the reason if the user requests this. Once the reason is stated, then offer a resolution and inform them the request is being processed.
Additional Instructions: {additional_instruct}

Introduce yourself in a friendly way, ask them what help would they need.
If the user says they no longer needs help, say good bye and have a nice day."""

def get_chat_prompt(bot_name: str, store_name: str, order_status: str, date: str, order_items: List, additional_instruct: Union[str, None] = None) -> str:
    prompt_template = system_prompt + f"\n\n{context}"
    if additional_instruct is None:
        return prompt_template.format(bot_name=bot_name, store_name=store_name, order_status=order_status, date=date, order_items=order_items, additional_instruct="None")
    
    return prompt_template.format(bot_name=bot_name, store_name=store_name, order_status=order_status, date=date, order_items=order_items, additional_instruct=additional_instruct)


return_guidelines = """

(If a customer wants to return a purchased item or an order, then say the following)
"I'd be happy to help with your return! May I know why you would like to return your order? Was there any issue with the product or the delivery?"

(If the customer asks anything else related to the return, then say a general statement)
"""

refund_guidelines = """

(If a customer wants to refund a purchased item or an order, then say the following)
"I'd be happy to help with your refund! May I know why you would like to refund your order? Was there any issue with the product or the delivery?"

(If the customer asks anything else related to the refund, then say a general statement)
"""

order_status_guidelines = """

(If a customer asks for the status of their order, then say the following)
"Let me check on that for you. Based on our records, <<explain the current status of your order>>"
"""

sales_guidelines = """

(If a customer asks for Sales or a Sales related query, then say the following)
"Sure thing! I can transfer your call right away. Please hold on for a moment while I connect you."
"""

def get_guidelines(call_intent: str, data: str) -> str:
    if call_intent == "Sales":
        return sales_guidelines
    elif call_intent == "Order Status":
        return order_status_guidelines.replace("<<explain the current status of your order>>", data)
    elif call_intent == "Refund":
        return refund_guidelines
    elif call_intent == "Returns":
        return return_guidelines
    elif call_intent == "Product Info":
        return "Provide the customer with the information they are looking for."
    elif call_intent == "General Inquiry":
        return "Answer Generally."
    else:
        return ""


def llama_prompt(prompt: str, call_intent: str, data: str, chat_history: list) -> str:

    system_prompt = f"""[INST] <<SYS>>
You are friendly and humanly AI assistant for a shopify store, and you are having a continuing conversation with a customer with their queries.

Guidelines for the call:
(Do not greet them with a hello or thank you, as the call is already connected and the conversation is ongoing)
(End the conversation if the customer says they no longer needs help)
{get_guidelines(call_intent, data)}

Chat History (Use this to provide context):
```
{(len(chat_history) == 0) and "No context available... (This is the begining of the conversation)" or chat_history}
```

Provide a concise response, considering the context.
Keep it direct and to the point. Be casual in the way you respond. No need to be overly formal.
<</SYS>>
{prompt}
[/INST]
    """
    return system_prompt


def mistral_prompt(prompt: str, chat_history: list | None) -> str:

    pass
