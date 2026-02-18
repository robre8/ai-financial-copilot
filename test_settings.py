#!/usr/bin/env python3
"""Check if HF_TOKEN is loaded in settings"""

from app.core.config import settings

print(f"HF_TOKEN from settings: {settings.HF_TOKEN[:20]}..." if settings.HF_TOKEN else "HF_TOKEN is NOT SET")
print(f"Token is valid: {len(settings.HF_TOKEN) > 0}")
