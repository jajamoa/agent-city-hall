import os
os.environ['HF_HOME'] = '/storage/aoqu/huggingface'



import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, AwqConfig

model_id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"

quantization_config = AwqConfig(
    bits=4,
    fuse_max_seq_len=512, # Note: Update this as per your use-case
    do_fuse=True,
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
  model_id,
  torch_dtype=torch.float16,
  low_cpu_mem_usage=True,
  quantization_config=quantization_config
).to(device)


context = [
    {"role": "user", "content": "President Joe Biden is: A. democratic B. republican C. None of the above. Enter your choice with the letter only."},
]
inputs = tokenizer.apply_chat_template(
  context,
  tokenize=True,
  add_generation_prompt=True,
  return_tensors="pt",
  return_dict=True,
).to("cuda")

outputs = model.generate(**inputs, 
                         do_sample=False,
                         max_new_tokens=512,
                         return_dict_in_generate=True,
                         output_scores=True,
                         )
generated_ids = outputs.sequences
scores = outputs.scores

# Decode the generated tokens into text
generated_text = tokenizer.batch_decode(generated_ids[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
print("Generated Text:", generated_text)

# Collect and print logits for the generated tokens
logits = torch.stack(scores, dim=1)  # Stack scores (logits) for all generated tokens
print("outputs shape:", generated_ids.shape)  # Shape: (batch_size, num_generated_tokens, vocab_size)
print("Logits shape:", logits.shape)  # Shape: (batch_size, num_generated_tokens, vocab_size)


target_words = ["A", "B", "C"]
last_token_logits = logits[:, 0, :]  # Get the logits for the last token
next_token_probs = F.softmax(last_token_logits, dim=-1)
next_token_id = torch.argmax(next_token_probs, dim=-1)
next_token = tokenizer.decode(next_token_id)
print(next_token)
target_ids = [tokenizer.convert_tokens_to_ids(word) for word in target_words]
target_logits = last_token_logits[:, target_ids]
probabilities = F.softmax(target_logits, dim=-1)
print(target_logits)
print(probabilities)

# target_logits = last_token_logits[:, target_ids]  # Extract logits for target words
# probabilities = F.softmax(target_logits, dim=-1).squeeze()
# probability_distribution = {word: prob.item() for word, prob in zip(target_words, probabilities)}
# print(probability_distribution)
