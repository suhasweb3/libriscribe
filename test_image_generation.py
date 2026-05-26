#!/usr/bin/env python
"""Test image generation with available models"""

import subprocess
import json
from pathlib import Path

def test_ollama_image_generation():
    """Test if Ollama can generate images"""
    
    print("🎨 Testing Image Generation\n")
    
    # Test 1: Check available models
    print("1. Checking available Ollama models...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try generating with flux2-klein (if available)
    print("\n2. Testing flux2-klein:4b...")
    try:
        result = subprocess.run(
            ['ollama', 'run', 'x/flux2-klein:4b', 
             'A simple black and white illustration of a book'],
            capture_output=True, 
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✓ flux2-klein works!")
            print(result.stdout[:200])
        else:
            print("✗ flux2-klein failed:")
            print(result.stderr[:500])
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Alternative - use Stable Diffusion via API
    print("\n3. Alternative: We can use Stable Diffusion API")
    print("   Options:")
    print("   - Stability AI API (paid)")
    print("   - Replicate API (pay-per-use)")
    print("   - Local Stable Diffusion (requires GPU)")
    print("   - DALL-E API (OpenAI, paid)")
    
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print("For book illustrations, I recommend:")
    print("1. Use Replicate API (cheap, $0.002 per image)")
    print("2. Or use DALL-E 3 via OpenAI ($0.04 per image)")
    print("3. Or skip images for now and add them manually later")
    print("\nWould you like me to integrate one of these options?")

if __name__ == "__main__":
    test_ollama_image_generation()
