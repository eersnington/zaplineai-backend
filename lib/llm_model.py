# type: ignore
import logging
from vllm import LLM, SamplingParams
from langchain_community.llms import HuggingFaceHub
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from lib.llm_prompt import llama_prompt
from typing import Union
import logging
import functools


@functools.cache
def get_vllm_model(model: str, quantization: Union[str, None] = None) -> LLM:
    logging.info(f"Loading vLLM model: {model}")
    if quantization is None:
        llm = LLM(model=model)
    else:
        llm = LLM(model=model, quantization=quantization)

    return llm


@functools.cache
def get_langchain_model(model: str) -> LLMChain:
    logging.info(f"Loading LLM model: {model}")
    llm = HuggingFaceHub(
        repo_id=model
    )

    template = """{question}"""

    prompt = PromptTemplate.from_template(template)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    return llm_chain


class BERTClassifier:
    def __init__(self):
        self.llm = get_langchain_model(
            "Sreenington/BERT-Ecommerce-Classification")

    def classify(self, text: str) -> str:
        output = self.llm.run(text)
        return output


class FalconSummarizer:
    def __init__(self):
        self.llm = get_llm_model("Falconsai/text_summarization")

    def summarize(self, text: str) -> str:
        outputs = self.llm.generate(text, use_tqdm=False)
        return outputs[0].outputs[0].text


class LLMModel:
    def __init__(self):
        self.llm = get_vllm_model("TheBloke/Llama-2-7B-chat-AWQ", "awq")

    def generate_text(self, prompt: str, temperature: 0.8, max_tokens=100) -> str:
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

    def add_message(self, message: str) -> None:
        self.chat_history.append(message)

    def generate_response(self, prompt: str, temperature=0.8, max_tokens=100) -> str:

        prompt_template = llama_prompt(prompt, self.chat_history)

        self.add_message(f"Customer: {prompt}")

        response = self.llm_model.generate_text(
            prompt_template, temperature, max_tokens)

        self.add_message(f"AI Assistant: {response}")

        return response
