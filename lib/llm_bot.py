# type: ignore
import logging
from vllm import LLM, SamplingParams
import logging
import time
import functools


@functools.cache
def get_llm_model():
    logging.info(f"Loading Llama LLM")
    llm = LLM(model="TheBloke/Llama-2-7B-chat-AWQ", quantization="awq")
    return llm


class LLMModel:
    def __init__(self):
        self.llm = get_llm_model()

    def generate_text(self, prompt, temperature=0.9, max_tokens=100):
        sampling_params = SamplingParams(
            temperature=temperature, max_tokens=max_tokens)

        output = self.llm.generate_text(prompt, sampling_params)

        return output
