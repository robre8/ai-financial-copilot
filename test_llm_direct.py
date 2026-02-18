#!/usr/bin/env python3
"""Test LLM service directly"""

import sys
import os
sys.path.insert(0, os.getcwd())

from app.services.llm_service import LLMService

try:
    print("Testing LLM service with prompt: 'The capital of France is'")
    result = LLMService.generate("The capital of France is")
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {repr(e)}")
    import traceback
    traceback.print_exc()
