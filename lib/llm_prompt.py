""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

order_status_guidelines = """
(If a customer asks for Order Status, take the information from the Fetch-Order-Status and respond with the status of the order)
(Financial Status is the status of the payment, and Fulfillment Status is the status of the delivery)

Fetched-Order-Status: $
"""

def get_guidelines(call_intent: str, data: str) -> str:
    if call_intent == "Order Status":
        return order_status_guidelines.replace("$", data)
    else:
        return ""


def llama_prompt(prompt: str, call_intent: str, data: str, chat_history: list | None) -> str:

    system_prompt = f"""[INST] <<SYS>>
You are an AI assistant for a clothing store, addressing customer queries only.
(Do not greet them with a hello, as the call is already connected)
(If the query is unrelated to the clothing store, you respond with a brief apology)
(If the query is a goodbye or thank you, you respond with a goodbye message, and ask them to hang up. Otherwise do not ask them to hang up the call.)

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
