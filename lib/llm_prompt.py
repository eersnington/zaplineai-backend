""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

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
{get_guidelines(call_intent, data)}

Chat History (Use this to provide context):
```
{(len(chat_history) == 0) and "No context available... (This is the begining of the conversation)" or chat_history}
```

Provide a concise response, considering the context.
Keep it direct and to the point.
<</SYS>>
{prompt}
[/INST]
    """
    return system_prompt


def mistral_prompt(prompt: str, chat_history: list | None) -> str:

    pass
