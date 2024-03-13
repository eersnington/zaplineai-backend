# type: ignore
import logging
from dotenv import load_dotenv, find_dotenv
from vllm import LLM, SamplingParams
from transformers import BertForSequenceClassification, BertTokenizer, TextClassificationPipeline
from typing import Union
import logging
import functools
import os

load_dotenv(find_dotenv(), override=True)

@functools.cache
def get_vllm_model(model: str, quantization: Union[str, None] = None) -> LLM:
    logging.info(f"Loading vLLM model: {model}")
    if os.getenv("PRODUCTION_MODE") == "False":
        logging.info("Skipping model loading in development environment")
        return None
    if quantization is None:
        llm = LLM(model=model)
    else:
        llm = LLM(model=model, quantization=quantization)
    return llm


@functools.cache
def get_bert_model(model_path: str) -> BertForSequenceClassification:
    logging.info(f"Loading BERT model: {model_path}")
    if os.getenv("PRODUCTION_MODE") == "False":
        logging.info("Skipping model loading in development environment")
        return None, None
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    return model, tokenizer


class BERTClassifier:
    def __init__(self):
        model, tokenizer = get_bert_model(
            "Sreenington/BERT-Ecommerce-Classification")
        self.model = TextClassificationPipeline(model=model, tokenizer=tokenizer)

    def classify(self, text: str) -> str:
        output = self.model(text)[0]['label']
        return output

    def get_pipeline_output(self, text: str) -> list:
        return self.model(text) # [{'label': 'Order Status', 'score': 0.65}]


# class FalconSummarizer:
#     def __init__(self):
#         self.llm = get_vllm_model("Falconsai/text_summarization")

#     def summarize(self, text: str) -> str:
#         outputs = self.llm.generate(text, use_tqdm=False)
#         return outputs[0].outputs[0].text


class LLMModel:
    def __init__(self):
        self.llm = get_vllm_model("TheBloke/Llama-2-7B-chat-AWQ", "awq")

    def generate_text(self, prompt: str, temperature=0.8, max_tokens=100) -> str:
        sampling_params = SamplingParams(
            temperature=temperature, max_tokens=max_tokens)

        # tqdm is a progress bar
        outputs = self.llm.generate(
            prompt, sampling_params, use_tqdm=False)
        generated_text = outputs[0].outputs[0].text

        return generated_text


class LLMChat:
    def __init__(self, llm_model: LLMModel, classifier: BERTClassifier):
        self.llm_model = llm_model
        self.classifier = classifier
        self.chat_history = []

    def add_message(self, message: str) -> None:
        self.chat_history.append(message)

    def generate_response(self, message: str, prompt: str, temperature=0.8, max_tokens=100) -> str:

        self.add_message(f"Customer: {message}")

        response = self.llm_model.generate_text(
            prompt, temperature, max_tokens)

        self.add_message(f"AI Assistant: {response}")

        return response
    
    def get_call_type(self, message: str) -> list:
        return self.classifier.get_pipeline_output(message)
