#!/usr/bin/env python3
"""Test Claude model availability"""
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("✗ API key not found")
    exit(1)

client = Anthropic(api_key=api_key)

# Test different model names
models_to_test = [
    'claude-3-sonnet-20240229',
    'claude-3-opus-20240229',
    'claude-3-haiku-20240307',
    'claude-3-5-sonnet-20240620',
]

print("Testing Claude models...")
print("=" * 50)

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{'role': 'user', 'content': 'Hi'}]
        )
        print(f"✓ {model} - WORKS!")
        break
    except Exception as e:
        print(f"✗ {model} - {str(e)[:80]}")

print("=" * 50)

