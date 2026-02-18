#!/usr/bin/env python3
"""Test InferenceClient with direct POST call"""

from huggingface_hub import InferenceClient
import os
import json

token = os.getenv("HF_TOKEN")
client = InferenceClient(model="gpt2", token=token)

prompt = "This document discusses financial analysis."

print(f"Testing with prompt: {prompt}")
print("\n--- Trying .post() method ---")
try:
    result = client.post(
        json={"inputs": prompt}
    )
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error with .post(): {repr(e)}")

print("\n--- Trying .text_generation() with return_full_text=False ---")
try:
    result = client.text_generation(
        prompt,
        max_new_tokens=100,
        return_full_text=False,
    )
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {repr(e)}")
