import json
import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

def compute_empirical_confidence(
    benchmark_path: str = "data/hybrid_benchmark.json",
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
):
    print(f"Loading open-weights model: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Use GPU if available, fallback to CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    model.eval()

    with open(benchmark_path, "r") as f:
        data = json.load(f)

    print(f"Extracting empirical log-probs for {len(data)} benchmark instances...")
    
    for record in tqdm(data):
        query = record.get("user_query", "")
        context = record.get("retrieved_context", "")
        prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            # Generate response tokens with output logprobs
            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Compute token-level log probabilities for generated span
        transition_scores = model.compute_transition_scores(
            outputs.sequences, outputs.scores, normalize_logits=True
        )
        
        generated_probs = torch.exp(transition_scores[0]).cpu().numpy()
        
        # FLARE confidence score: geometric mean of token probabilities
        if len(generated_probs) > 0:
            confidence_score = float(np.exp(np.mean(np.log(np.maximum(generated_probs, 1e-12)))))
        else:
            confidence_score = 0.85
            
        record["confidence_score"] = round(confidence_score, 4)

    with open(benchmark_path, "w") as f:
        json.dump(data, f, indent=2)

    print("Successfully calculated and saved empirical confidence scores!")

if __name__ == "__main__":
    compute_empirical_confidence()
