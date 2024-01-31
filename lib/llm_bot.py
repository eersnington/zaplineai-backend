# type: ignore
import logging
from vllm import LLM, SamplingParams
import logging
import functools


@functools.cache
def get_llm_model():
    logging.info(f"Loading Llama LLM")
    llm = LLM(model="TheBloke/Llama-2-7B-chat-AWQ", quantization="awq")

    return llm


class LLMModel:
    def __init__(self):
        self.llm = get_llm_model()

    def generate_text(self, prompt: str, temperature: 0.8, max_tokens=100):
        sampling_params = SamplingParams(
            temperature=temperature, max_tokens=max_tokens)

        # tqdm is a progress bar
        outputs = self.llm.generate(
            prompt, sampling_params, use_tqdm=False)
        generated_text = outputs[0].outputs[0].text

        return generated_text


class LLMChat:
    def __init__(self, llm_model: LLMModel):
        self.llm_model = llm_model
        self.chat_history = []

    def add_message(self, message: str):
        self.chat_history.append(message)

    def generate_response(self, prompt: str, temperature=0.8, max_tokens=100):
        # Generate the response using the LLM model and the chat history as context
        context = '\n'.join(self.chat_history)
        system_prompt = """[INST] <<SYS>>
        You are an AI assistant of a clothing store that answers the customers queries. 
        Do not answer questions that are not related to the clothing store. (Say sorry, you can't answer that)"""

        prompt_template = f"""
        {system_prompt}

        Here is the context(previous messages):
        ```
        {context}
        ```
        Write an appropriate response to the query below while keeping the context in mind.
        <</SYS>>
        {prompt}
        [/INST]
        """
        self.add_message(f"Customer: {prompt}")

        response = self.llm_model.generate_text(
            prompt_template, temperature, max_tokens)

        self.add_message(response)

        return response
