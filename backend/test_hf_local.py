#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration using huggingface_hub library.
This approach allows for both API access and local model usage.
"""

import os
import json
from dotenv import load_dotenv

def test_huggingface_hub():
    """Test the Hugging Face integration using huggingface_hub library."""
    
    try:
        from huggingface_hub import InferenceApi
    except ImportError:
        print("❌ huggingface_hub package not installed.")
        print("   Install it with: pip install huggingface_hub")
        return False
    
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
    
    print(f"🔍 Testing Hugging Face integration using huggingface_hub...")
    print(f"   Model: {model_name}")
    print(f"   Model Page: https://huggingface.co/{model_name}")
    print()
    
    try:
        # Initialize the Inference API client
        inference = InferenceApi(repo_id=model_name, token=hf_api_key)
        
        # Simple test prompt
        test_prompt = "Generate a simple JSON with one test case for a GET API endpoint /users"
        
        print("📡 Sending request to Hugging Face...")
        
        # Test API connectivity
        response = inference(
            inputs=test_prompt,
            parameters={
                "max_new_tokens": 100,
                "return_full_text": False
            }
        )
        
        if isinstance(response, dict) and "error" in response:
            print(f"❌ API Error: {response['error']}")
            if "not found" in str(response['error']).lower():
                print("   This model may not be available through the Inference API")
                print("   Try a different model like 'gpt2'")
            return False
        elif isinstance(response, list) and len(response) > 0:
            print("✅ API Connection Successful!")
            print("📝 Sample Response:")
            print(json.dumps(response[0], indent=2)[:500] + "..." if len(json.dumps(response[0], indent=2)) > 500 else json.dumps(response[0], indent=2))
            return True
        else:
            print("❌ Unexpected response format:")
            print(response)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
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
    print("🧪 Hugging Face Hub Test Script")
    print("=" * 40)
    print("Using huggingface_hub library for Hugging Face integration")
    print()
    
    # Check environment file
    if not check_env_file():
        exit(1)
    
    print()
    
    # Test API
    success = test_huggingface_hub()
    
    print()
    if success:
        print("🎉 All tests passed! Your Hugging Face integration is working correctly.")
        print("   The AI test generation feature should now work in AETHER.")
    else:
        print("💥 Tests failed. Please check the errors above and fix your configuration.")
        print("   The fallback basic test generation will still work in AETHER.")
        print()
        print("💡 Tips:")
        print("   1. Install huggingface_hub: pip install huggingface_hub")
        print("   2. Try a different model if this one is not available via API")
        print("   3. Not all models on Hugging Face are available through the Inference API")