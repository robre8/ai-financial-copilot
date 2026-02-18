#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "https://ai-financial-copilot.onrender.com"

print("=" * 60)
print("Testing AI Financial Copilot API")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health check...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Upload PDF
print("\n2. Testing PDF upload...")
try:
    with open('test_financial.pdf', 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/upload-pdf",
            files=files,
            timeout=60
        )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Wait a moment for indexing
print("\n3. Waiting for PDF to be indexed...")
time.sleep(3)

# Test 3: Ask question
print("\n4. Testing /ask endpoint...")
try:
    payload = {
        "question": "What was the revenue in Q1 2024?"
    }
    response = requests.post(
        f"{BASE_URL}/ask",
        json=payload,
        timeout=60
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Question: {payload['question']}")
        print(f"   Answer: {data.get('answer', 'No answer')[:200]}...")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
