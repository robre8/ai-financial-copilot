#!/usr/bin/env python3
"""Test various Huggingface inference endpoints"""

import requests
import os
import json

token = os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

prompt = "This document discusses financial analysis."
payload = {"inputs": prompt}

endpoints = [
    ("api-inference.huggingface.co", "https://api-inference.huggingface.co/models/gpt2"),
    ("router.huggingface.co /models", "https://router.huggingface.co/models/gpt2"),
    ("router.huggingface.co /hf-inference/models", "https://router.huggingface.co/hf-inference/models/gpt2"),
]

for name, url in endpoints:
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)}")
            break
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {repr(e)}")
