from huggingface_hub import login
from optimum.gptq import GPTQQuantizer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

login()

dataset_id = "wikitext2"


quantizer = GPTQQuantizer(bits=4, dataset=dataset_id, model_seqlen=2048)
quantizer.quant_method = "gptq"



model_id = "meta-llama/Meta-Llama-3-8B"

model = AutoModelForCausalLM.from_pretrained(model_id, config=quantizer, torch_dtype=torch.float16, max_memory = {0: "15GIB", 1: "15GIB"})
tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)


import os
import json

quantized_model = quantizer.quantize_model(model, tokenizer)

# save the quantized model
save_folder = "quantized_llama"
quantized_model.save_pretrained(save_folder, safe_serialization=True)

# load fresh, fast tokenizer and save it to disk
tokenizer = AutoTokenizer.from_pretrained(model_id).save_pretrained(save_folder)

# save quantize_config.json for TGI
with open(os.path.join(save_folder, "quantize_config.json"), "w", encoding="utf-8") as f:
  quantizer.disable_exllama = False
  json.dump(quantizer.to_dict(), f, indent=2)


quantized_model.push_to_hub("Sreenington/Meta-llama-3-8B-GPTQ")
