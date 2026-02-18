#!/usr/bin/env python3
"""Test InferenceClient directly with different prompts and parameters"""

from huggingface_hub import InferenceClient
import os

token = os.getenv("HF_TOKEN")
client = InferenceClient(model="gpt2", token=token)

# Test different prompts and parameters
prompts = [
    "The capital of France is",
    "The weather today is sunny. What should I do?\nAnswer:",
    "Once upon a time,"
]

for prompt in prompts:
    print(f"\n--- Testing prompt: '{prompt[:30]}...' ---")
    try:
        result = client.text_generation(
            prompt,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            return_full_text=False,
        )
        print(f"✅ Success: {result}")
        break
    except StopIteration:
        print(f"❌ StopIteration with this prompt")
    except Exception as e:
        print(f"❌ Error: {repr(e)}")
