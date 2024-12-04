import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, AwqConfig

model_id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"
quantization_config = AwqConfig(
    bits=4,
    fuse_max_seq_len=2048,
    do_fuse=True,
)

class LLaMAClient:
  def __init__(self):
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    self.tokenizer = AutoTokenizer.from_pretrained(model_id)
    self.model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.float16,
      low_cpu_mem_usage=True,
      quantization_config=quantization_config
    ).to(self.device)
    
  def chat(self, messages):
    inputs = self.tokenizer.apply_chat_template(
      messages,
      tokenize=True,
      add_generation_prompt=True,
      return_tensors="pt",
      return_dict=True,
    ).to(self.device)
    outputs = self.model.generate(**inputs, 
                         do_sample=False,
                         max_new_tokens=2048,
                         return_dict_in_generate=True,
                         output_scores=True,
                         return_legacy_cache=True
                         )
    generated_ids = outputs.sequences
    scores = outputs.scores
    generated_text = self.tokenizer.batch_decode(generated_ids[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
    return generated_text
  
  def get_logits(self, messages, target_words):
    inputs = self.tokenizer.apply_chat_template(
      messages,
      tokenize=True,
      add_generation_prompt=True,
      return_tensors="pt",
      return_dict=True,
    ).to(self.device)
    outputs = self.model.generate(**inputs, 
                         do_sample=False,
                         max_new_tokens=2048,
                         return_dict_in_generate=True,
                         output_scores=True,
                         return_legacy_cache=True
                         )
    scores = outputs.scores
    logits = torch.stack(scores, dim=1)
    last_token_logits = logits[:, 0, :]
    target_ids = [self.tokenizer.convert_tokens_to_ids(word) for word in target_words]
    target_logits = last_token_logits[:, target_ids]
    probabilities = F.softmax(target_logits, dim=-1)
    return target_logits, probabilities


# if __name__ == '__main__':
#   prompt = "President Joe Biden is: A. democratic B. republican C. None of the above. Enter your choice with the letter only."
#   messages = [
#     {"role": "user", "content": prompt},
#   ]
#   llama_client = LLaMAClient()
#   generated_text = llama_client.chat(messages)
#   print("Original Prompt:", prompt)
#   print("Generated Text:", generated_text)
#   target_words = ["A", "B", "C"]
#   target_logits, probabilities = llama_client.get_logits(messages, target_words)
#   print("Target Logits:", target_logits)
#   print("Probabilities:", probabilities)

# prompt = "President Joe Biden is: A. democratic B. republican C. None of the above. Enter your choice with the letter only."
# context = [
#     {"role": "user", "content": prompt},
# ]
# inputs = tokenizer.apply_chat_template(
#   context,
#   tokenize=True,
#   add_generation_prompt=True,
#   return_tensors="pt",
#   return_dict=True,
# ).to("cuda")

# outputs = model.generate(**inputs, 
#                          do_sample=False,
#                          max_new_tokens=512,
#                          return_dict_in_generate=True,
#                          output_scores=True,
#                          )
# generated_ids = outputs.sequences
# scores = outputs.scores

# # Decode the generated tokens into text
# generated_text = tokenizer.batch_decode(generated_ids[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# print("Original Prompt:", prompt)
# print("Generated Text:", generated_text)

# # Collect and print logits for the generated tokens
# logits = torch.stack(scores, dim=1)  # Stack scores (logits) for all generated tokens
# # print("outputs shape:", generated_ids.shape)  # Shape: (batch_size, num_generated_tokens, vocab_size)
# # print("Logits shape:", logits.shape)  # Shape: (batch_size, num_generated_tokens, vocab_size)


# target_words = ["A", "B", "C"]
# last_token_logits = logits[:, 0, :]  # Get the logits for the last token
# next_token_probs = F.softmax(last_token_logits, dim=-1)
# next_token_id = torch.argmax(next_token_probs, dim=-1)
# next_token = tokenizer.decode(next_token_id)
# # print(next_token)
# target_ids = [tokenizer.convert_tokens_to_ids(word) for word in target_words]
# target_logits = last_token_logits[:, target_ids]
# probabilities = F.softmax(target_logits, dim=-1)
# print("Target Logits:", target_logits)
# print("Probabilities:", probabilities)

# # target_logits = last_token_logits[:, target_ids]  # Extract logits for target words
# # probabilities = F.softmax(target_logits, dim=-1).squeeze()
# # probability_distribution = {word: prob.item() for word, prob in zip(target_words, probabilities)}
# # print(probability_distribution)
