""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

order_status_guidelines = """
(If a customer asks for Order Status, take the information from the Fetch-Order-Status and respond with the status of the order)
(Financial Status is the status of the payment, and Fulfillment Status is the status of the delivery)

Fetched-Order-Status: $
"""

def get_guidelines(call_type: str, data: str) -> str:
    if call_type[0]["label"] == "Order Status":
        return order_status_guidelines.replace("$", data)
    else:
        return ""


def llama_prompt(prompt: str, call_type: str, data: str, chat_history: list | None) -> str:

    system_prompt = f"""[INST] <<SYS>>
You are an AI assistant for a clothing store, addressing customer queries only.
(If unrelated, respond with a brief apology)
(If the customer says goodbye, end the conversation and ask them to hang up)

Call Type (based on Classification Model):
```
# Label - The type of call
# Score - The confidence level of the classification
{call_type}
```
{get_guidelines(call_type, data)}

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
