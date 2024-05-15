# type: ignore
import logging
from typing import Tuple, Optional, Union
from dotenv import load_dotenv, find_dotenv

from lib.llm_prompt import llama_prompt, get_classifier_prompt
from vllm import LLM, SamplingParams
from typing import Union
import logging
import functools
import os

load_dotenv(find_dotenv(), override=True)

@functools.cache
def get_vllm_model(model: str, 
                   gpu_memory_utilization: float,
                   quantization: Union[str, None] = None) -> Optional[LLM]:
    """
    Retrieve the vLLM model for text generation.

    Args:
    - model (str): The model name.
    - quantization (Union[str, None], optional): The quantization method. Defaults to None.

    Returns:
        Optional[LLM]: The vLLM model.
    """
    logging.info(f"Loading vLLM model: {model}")
    if os.getenv("PRODUCTION_MODE") == "False":
        logging.info("Skipping model loading in development environment")
        return None
    if quantization is None:
        llm = LLM(model=model, gpu_memory_utilization=gpu_memory_utilization)
    else:
        print("Quantization: ", quantization)
        llm = LLM(model=model, gpu_memory_utilization=gpu_memory_utilization, quantization=quantization)
    return llm


class ClassifierModel:
    def __init__(self):
        self.model = get_vllm_model("Sreenington/Phi-3-mini-4k-instruct-AWQ", 0.3, "awq")

    def classify(self, prompt: str) -> str:
        sampling_params = SamplingParams(
            temperature=0.1, max_tokens=4)

        # tqdm is a progress bar
        outputs = self.model.generate(
            prompt, sampling_params, use_tqdm=False)
        generated_text = outputs[0].outputs[0].text
        return generated_text


class LLMModel:
    def __init__(self):
        self.llm = get_vllm_model("Sreenington/Llama-3-8B-ChatQA-AWQ", 0.6, "awq")

    def generate_text(self, prompt: str, temperature=0.7, max_tokens=100) -> str:
        """
        Generate text using the vLLM model.

        Args:
        - prompt (str): The input prompt for text generation.
        - temperature (float, optional): The temperature for text generation. Defaults to 0.7.
        - max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            str: The generated text.
        """
        sampling_params = SamplingParams(
            temperature=temperature, max_tokens=max_tokens)

        # tqdm is a progress bar
        outputs = self.llm.generate(
            prompt, sampling_params, use_tqdm=False)
        generated_text = outputs[0].outputs[0].text

        return generated_text


class LLMChat:
    def __init__(self, llm_model: LLMModel, classifier: ClassifierModel):
        self.llm_model = llm_model
        self.classifier_model = classifier
        self.chat_history = []

    def add_message(self, role: str, content: str) -> None:
        self.chat_history.append({"role": role, "content": content})

    def messages_formatter(self) -> str:
        formatted_messages = []
        for message in self.chat_history:
            formatted_messages.append(f"{message['role']}: {message['content']}")
        return '\n\n'.join(formatted_messages)

    def llm_response(self, message: str, prompt: str, temperature=0.7, max_tokens=100) -> str:
        """
        Generate a response to a message using the vLLM model.

        Args:
        - message (str): The incoming message.
        - prompt (str): The prompt for text generation.
        - temperature (float, optional): The temperature for text generation. Defaults to 0.8.
        - max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            str: The generated response.
        """
        self.add_message("User", message)

        response = self.llm_model.generate_text(
            prompt, temperature, max_tokens)

        self.add_message("Assistant", response)

        return response
    
    def classifier_response(self, message: str) -> str:
        """
        Get the call type classification output for a message.

        Args:
        - message (str): The message to classify.

        Returns:
            list: The classification output.
        """
        classification_prompt = get_classifier_prompt(message)
        return self.classifier_model.classify(classification_prompt)
