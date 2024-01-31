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
        outputs = self.llm.generate(prompt, sampling_params, use_tqdm=False)
        generated_text = outputs[0].outputs[0].text

        return generated_text


class LLMChat:
    def __init__(self, llm_model: LLMModel):
        self.llm_model = llm_model
        self.chat_history = []

    def add_message(self, message: str):
        self.chat_history.append(message)

    def generate_response(self, prompt: str, temperature=0.8, max_tokens=100):
        self.add_message(prompt)

        # Generate the response using the LLM model and the chat history as context
        context = ' '.join(self.chat_history)
        response = self.llm_model.generate_text(
            context, temperature, max_tokens)

        self.add_message(response)

        return response
