#!/usr/bin/env python3
"""
Test script to verify Hugging Face API connectivity and key validity.
This script will help diagnose issues with the AI test generation feature.
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_huggingface_api():
    """Test the Hugging Face API connectivity and key validity."""
    
    # Load environment variables
    load_dotenv()
    
    # Also try to load from backend directory if we're in the root
    if not os.getenv("HF_API_KEY"):
        backend_env_path = os.path.join("backend", ".env")
        if os.path.exists(backend_env_path):
            load_dotenv(backend_env_path)
    
    # Get API key and model from environment
    hf_api_key = os.getenv("HF_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt2")  # Using a simpler, known working model
    
    if not hf_api_key:
        print("❌ Error: HF_API_KEY not found in environment variables")
        print("Please set your Hugging Face API key in the backend/.env file")
        return False
    
    if not hf_api_key.strip():
        print("❌ Error: HF_API_KEY is empty")
        print("Please set a valid Hugging Face API key in the backend/.env file")
        return False
    
    # API configuration
    api_url = f"https://huggingface.co/{model_name}"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    
    # Simple test prompt
    test_prompt = "Generate a simple JSON with one test case for a GET API endpoint /users"
    
    print(f"🔍 Testing Hugging Face API connectivity...")
    print(f"   Model: {model_name}")
    print(f"   API URL: {api_url}")
    print()
    
    try:
        # Test API connectivity
        response = requests.post(
            api_url,
            headers=headers,
            json={
                "inputs": test_prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "return_full_text": False
                }
            },
            timeout=30
        )
        
        print(f"📡 HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ API Connection Successful!")
                print("📝 Sample Response:")
                print(json.dumps(result, indent=2))
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print("   Response content:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
                return False
        elif response.status_code == 400:
            print("❌ Bad Request - Check your request format")
            print("   Response:", response.text)
            return False
        elif response.status_code == 401:
            print("❌ Unauthorized - Invalid API key")
            print("   Please check your HF_API_KEY in the backend/.env file")
            return False
        elif response.status_code == 403:
            print("❌ Forbidden - API key doesn't have access to this model")
            return False
        elif response.status_code == 404:
            print("❌ Model Not Found - The specified model does not exist")
            print("   Try a different model like 'gpt2' or 'facebook/blenderbot-400M-distill'")
            return False
        elif response.status_code == 429:
            print("❌ Rate Limited - Too many requests")
            return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print("   Response:", response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request Timeout - The API took too long to respond")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Could not connect to Hugging Face API")
        print("   Please check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has the required variables."""
    # Check in current directory first
    env_path = ".env"
    # If not found, check in backend directory
    if not os.path.exists(env_path):
        env_path = os.path.join("backend", ".env")
    
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        print("   Please create a backend/.env file with your Hugging Face API key")
        print("   You can copy backend/.env.example to backend/.env and fill in your key")
        return False
    
    # Check contents
    with open(env_path, 'r') as f:
        content = f.read()
        
    if "HF_API_KEY=" not in content:
        print("❌ HF_API_KEY not found in .env file")
        return False
        
    if "HF_API_KEY=your_hugging_face_api_key_here" in content:
        print("⚠️  Warning: .env file contains placeholder value")
        print("   Please replace 'your_hugging_face_api_key_here' with your actual API key")
        return False
    
    print("✅ .env file found and appears to have API key")
    return True

if __name__ == "__main__":
    print("🧪 Hugging Face API Test Script")
    print("=" * 40)
    
    # Check environment file
    if not check_env_file():
        exit(1)
    
    print()
    
    # Test API
    success = test_huggingface_api()
    
    print()
    if success:
        print("🎉 All tests passed! Your Hugging Face API is configured correctly.")
        print("   The AI test generation feature should now work in AETHER.")
    else:
        print("💥 Tests failed. Please check the errors above and fix your configuration.")
        print("   The fallback basic test generation will still work in AETHER.")