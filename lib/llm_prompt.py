""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""


def llama_prompt(prompt: str, chat_history: list | None) -> str:

    system_prompt = f"""[INST] <<SYS>>
You are an AI assistant for a clothing store, addressing customer queries only.
(If unrelated, respond with a brief apology)

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
