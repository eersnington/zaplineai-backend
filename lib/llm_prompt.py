""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""

sales_guidelines = """
(If a customer asks for Sales or a Sales related query, tell that the call will be transferred a live respresentative)

Follow this format for your response (Do not add anything extra):
"Sure thing! I can transfer your call right away. Please hold on for a moment while I connect you."
"""

def get_guidelines(call_intent: str, data: str) -> str:
    if call_intent == "Sales":
        return sales_guidelines
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
