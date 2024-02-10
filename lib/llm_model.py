# type: ignore
import logging
from vllm import LLM, SamplingParams
from transformers import pipeline, BertForSequenceClassification, BertTokenizerFast
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
def get_bert_model(model: str) -> BertForSequenceClassification:
    logging.info(f"Loading BERT model: {model}")
    model = BertForSequenceClassification.from_pretrained(model)
    tokenizer = BertTokenizerFast.from_pretrained(model)
    return model, tokenizer


class BERTClassifier:
    def __init__(self):
        model, tokenizer = get_bert_model(
            "Sreenington/BERT-Ecommerce-Classification")
        self.model = pipeline("sentiment-analysis",
                              model=model, tokenizer=tokenizer)

    def classify(self, text: str) -> str:
        output = self.model(text)
        return output


class FalconSummarizer:
    def __init__(self):
        self.llm = get_vllm_model("Falconsai/text_summarization")

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
