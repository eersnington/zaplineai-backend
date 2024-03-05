""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

order_status_guidelines = """
(If a customer asks for Order Status, take the information from the Order-Status and respond with the status of the order)
(Financial Status is the status of the payment, and Fulfillment Status is the status of the delivery)
(Use the information below to formulate your friendly assistant response. Do not ask for any other details)
(If the order status is not available, respond with an apology)

Order-Status: $
"""

returns_guidelines = """
(If a customer asks for Return, tell them that a return will be initiated within from your side and they will be contacted soon)

"""

refund_guidelines = """
(If a customer asks for Refund, tell them that a refund will be initiated within from your side and they will be contacted soon)

"""

sales_or_transfer_guidelines = """
(If a customer asks for Sales or Transfer, tell them that they will transfer the call to a live respresentative)

"""

def get_guidelines(call_intent: str, data: str) -> str:
    if call_intent == "Order Status":
        return order_status_guidelines.replace("$", data)
    elif call_intent == "Returns":
        return returns_guidelines
    elif call_intent == "Refund":
        return refund_guidelines
    elif call_intent in ["Sales", "Transfer"]:
        return sales_or_transfer_guidelines
    elif call_intent == "Product Info":
        return "Provide the customer with the information they are looking for."
    else:
        return ""


def llama_prompt(prompt: str, call_intent: str, data: str, chat_history: list | None) -> str:

    system_prompt = f"""[INST] <<SYS>>
You are an AI assistant for a clothing store, addressing customer queries only.
(Do not greet them with a hello, as the call is already connected)
(If the query is unrelated to the clothing store, you respond with a brief apology)

Call Intent (based on Classification Model):
```
# It is the intent of the call, based on the classification model
Call Intent: {call_intent}
```
{get_guidelines(call_intent, data)}

Context:
```
{(len(chat_history) == 0) and "No context available... (This is the begining of the conversation)" or chat_history}
```

Provide a concise response related to the clothing store, considering the context.
Keep it direct and to the point.
<</SYS>>
{prompt}
[/INST]
    """
    return system_prompt


def mistral_prompt(prompt: str, chat_history: list | None) -> str:

    pass
