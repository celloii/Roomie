#!/usr/bin/env python3
"""
Quick test script to check chatbot configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Chatbot Configuration Check")
print("=" * 50)

# Check API key
api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
if api_key:
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
else:
    print("✗ API Key NOT FOUND")
    print("\nTo set up your API key:")
    print("1. Get your API key from: https://console.anthropic.com/")
    print("2. Create a .env file in this directory")
    print("3. Add this line: ANTHROPIC_API_KEY=your_key_here")
    print("\nOr export it in your terminal:")
    print("  export ANTHROPIC_API_KEY=your_key_here")

# Check anthropic package
try:
    import anthropic
    print(f"✓ anthropic package installed: {anthropic.__version__}")
except ImportError:
    print("✗ anthropic package NOT installed")
    print("  Run: pip install anthropic")

# Test Knot configuration
try:
    from knot import Knot
    knot = Knot()
    try:
        config = knot.get_claude_config()
        print(f"✓ Knot configuration OK")
        print(f"  Model: {config.get('model', 'unknown')}")
    except Exception as e:
        print(f"✗ Knot configuration error: {e}")
except Exception as e:
    print(f"✗ Could not import Knot: {e}")

print("=" * 50)

