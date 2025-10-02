#!/usr/bin/env python3
"""
Test script to verify OpenAI API connectivity and key validity.
This provides an alternative to Hugging Face for AI test generation.
"""

import os
import json
from dotenv import load_dotenv
try:
    import openai
except ImportError:
    print("❌ OpenAI package not installed. Install with: pip install openai")
    exit(1)

def test_openai_api():
    """Test the OpenAI API connectivity and key validity."""
    
    # Load environment variables
    load_dotenv()
    
    # Also try to load from backend directory if we're in the root
    if not os.getenv("OPENAI_API_KEY"):
        backend_env_path = os.path.join("backend", ".env")
        if os.path.exists(backend_env_path):
            load_dotenv(backend_env_path)
    
    # Get API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the backend/.env file")
        return False
    
    if not openai_api_key.strip():
        print("❌ Error: OPENAI_API_KEY is empty")
        print("Please set a valid OpenAI API key in the backend/.env file")
        return False
    
    # Configure OpenAI
    openai.api_key = openai_api_key
    
    # Simple test prompt
    test_prompt = "Generate a simple JSON with one test case for a GET API endpoint /users"
    
    print(f"🔍 Testing OpenAI API connectivity...")
    print()
    
    try:
        # Test API connectivity
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert API tester that generates JSON test cases."},
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ API Connection Successful!")
        print("📝 Sample Response:")
        print(json.dumps(response.choices[0].message.content, indent=2))
        return True
            
    except openai.error.AuthenticationError:
        print("❌ Authentication Error - Invalid API key")
        print("   Please check your OPENAI_API_KEY in the backend/.env file")
        return False
    except openai.error.RateLimitError:
        print("❌ Rate Limited - Check your OpenAI plan and billing")
        return False
    except openai.error.APIConnectionError:
        print("❌ Connection Error - Could not connect to OpenAI API")
        print("   Please check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def update_env_example():
    """Add OpenAI API key example to .env.example"""
    # Check in current directory first
    env_example_path = ".env.example"
    # If not found, check in backend directory
    if not os.path.exists(env_example_path):
        env_example_path = os.path.join("backend", ".env.example")
    
    with open(env_example_path, 'a') as f:
        f.write("\n# OpenAI API Configuration (Alternative to Hugging Face)\n")
        f.write("# Get your API key from https://platform.openai.com/api-keys\n")
        f.write("OPENAI_API_KEY=your_openai_api_key_here\n")

def check_env_file():
    """Check if .env file exists and has the required variables."""
    # Check in current directory first
    env_path = ".env"
    # If not found, check in backend directory
    if not os.path.exists(env_path):
        env_path = os.path.join("backend", ".env")
    
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        print("   Please create a backend/.env file with your API key")
        return False
    
    # Check contents
    with open(env_path, 'r') as f:
        content = f.read()
        
    if "OPENAI_API_KEY=" not in content and "HF_API_KEY=" not in content:
        print("❌ No API key found in .env file")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 OpenAI API Test Script")
    print("=" * 40)
    
    # Check environment file
    if not check_env_file():
        exit(1)
    
    # Update .env.example to include OpenAI
    update_env_example()
    
    # Test API
    success = test_openai_api()
    
    print()
    if success:
        print("🎉 All tests passed! Your OpenAI API is configured correctly.")
    else:
        print("💥 Tests failed. Please check the errors above and fix your configuration.")