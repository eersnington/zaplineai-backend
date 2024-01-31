""""summary:
    This file contains the prompt for the LLM model in different prompt formats.
"""


def llama_prompt(prompt: str, chat_history: list | None) -> str:
    system_prompt = f"""[INST] <<SYS>>
        You are an AI assistant of a clothing store that answers the customers queries. 
        Do not answer questions that are not related to the clothing store. (Say sorry, you can't answer that)
        
        Here is the context(previous messages):
        ```
        {chat_history}
        ```

        Write an *appropriate and brief*~ response to the query below while keeping the context in mind.
        <</SYS>>
        {prompt}
        [/INST]
    """
    return system_prompt


def mistral_prompt(prompt: str, chat_history: list | None) -> str:

    pass
