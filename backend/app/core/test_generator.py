import json
import time
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# Add the parent directory to the path to find .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = parent_dir
root_dir = os.path.dirname(backend_dir)

# Load environment variables from .env file
# Try multiple possible locations
env_paths = [
    os.path.join(backend_dir, ".env"),
    os.path.join(root_dir, ".env"),
    os.path.join(root_dir, "backend", ".env"),
    ".env"
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Hugging Face Configuration
HF_API_KEY = os.getenv("HF_API_KEY")
# Using a known working model by default
MODEL_NAME = os.getenv("MODEL_NAME", "gpt2")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)

try:
    import openai
    openai.api_key = OPENAI_API_KEY
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI package not installed. Install with: pip install openai")

# Hugging Face Hub
try:
    from huggingface_hub import InferenceApi
    HUGGINGFACE_HUB_AVAILABLE = True
except ImportError:
    HUGGINGFACE_HUB_AVAILABLE = False
    print("huggingface_hub package not installed. Install with: pip install huggingface_hub")


def generate_basic_tests(spec_json: str):
    """Generate basic test cases without AI when AI is not available."""
    spec = json.loads(spec_json)
    paths = spec.get("paths", {})
    servers = spec.get("servers", [])
    base_url = servers[0]["url"] if servers else "http://localhost:8000"
    
    all_tests = []
    
    for endpoint, methods in paths.items():
        for method, details in methods.items():
            # Generate basic test cases
            basic_tests = [
                {
                    "endpoint": endpoint,
                    "method": method.upper(),
                    "payload": {}  # Empty payload as default
                }
            ]
            
            # For POST/PUT methods, add a basic payload test
            if method.upper() in ["POST", "PUT"]:
                basic_tests.append({
                    "endpoint": endpoint,
                    "method": method.upper(),
                    "payload": {"test": "data"}  # Basic payload
                })
            
            all_tests.extend(basic_tests)
    
    return all_tests


def generate_openai_tests(spec_json: str):
    """Generate test cases using OpenAI API."""
    if not OPENAI_AVAILABLE:
        raise Exception("OpenAI package not installed")
    
    spec = json.loads(spec_json)
    paths = spec.get("paths", {})
    servers = spec.get("servers", [])
    base_url = servers[0]["url"] if servers else "http://localhost:8000"

    all_tests = []

    for endpoint, methods in paths.items():
        for method, details in methods.items():
            prompt = f"""
You are an expert API tester. Generate 5 JSON test cases for the following API:

Endpoint: {method.upper()} {endpoint}
Base URL: {base_url}
Payload schema: {details.get('requestBody', {})}

Rules:
1. Include one valid payload.
2. Include one empty payload.
3. Include one payload with extremely long string.
4. Include one payload with invalid type.
5. Include one payload with special characters for security testing.

Return ONLY a JSON array of objects in this exact format:
[{{"endpoint": "...", "method": "...", "payload": {{}}}}, ...]

No other text, just the JSON array.
"""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert API tester that generates JSON test cases."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                result_text = response.choices[0].message.content.strip()
                
                try:
                    # Try to parse the response as JSON
                    test_cases = json.loads(result_text)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from the response
                    start = result_text.find("[")
                    end = result_text.rfind("]") + 1
                    if start != -1 and end > start:
                        json_text = result_text[start:end]
                        test_cases = json.loads(json_text)
                    else:
                        raise Exception("Could not extract JSON from OpenAI response")
                
                # Process GET requests to move payload to query parameters
                for t in test_cases:
                    if t["method"].upper() == "GET" and isinstance(t.get("payload"), dict):
                        if t["payload"]:
                            t["endpoint"] += "?" + urlencode(t["payload"])
                        t["payload"] = {}
                
                all_tests.extend(test_cases)
                
            except Exception as e:
                print(f"Error calling OpenAI API for endpoint {method.upper()} {endpoint}: {e}")
                continue

    return all_tests


def generate_huggingface_tests(spec_json: str, max_retries: int = 5, retry_delay: int = 5):
    """Generate test cases using Hugging Face Hub API."""
    if not HUGGINGFACE_HUB_AVAILABLE:
        raise Exception("huggingface_hub package not installed. Install with: pip install huggingface_hub")
    
    if not HF_API_KEY:
        raise Exception("HF_API_KEY not found in environment variables")
    
    print(f"Using Hugging Face model: {MODEL_NAME}")
    print(f"Model page: https://huggingface.co/{MODEL_NAME}")
    
    spec = json.loads(spec_json)
    paths = spec.get("paths", {})
    servers = spec.get("servers", [])
    base_url = servers[0]["url"] if servers else "http://localhost:8000"

    all_tests = []
    
    # Initialize the Inference API client
    inference = InferenceApi(repo_id=MODEL_NAME, token=HF_API_KEY)

    for endpoint, methods in paths.items():
        for method, details in methods.items():
            prompt = f"""
You are an expert API tester. Generate 5 JSON test cases for the following API:

Endpoint: {method.upper()} {endpoint}
Base URL: {base_url}
Payload schema: {details.get('requestBody', {})}

Rules:
1. Include one valid payload.
2. Include one empty payload.
3. Include one payload with extremely long string.
4. Include one payload with invalid type.
5. Include one payload with special characters for security testing.

Return ONLY a JSON array of objects in this exact format:
[{{"endpoint": "...", "method": "...", "payload": {{}}}}, ...]

No other text, just the JSON array.
"""

            result_text = ""
            for attempt in range(max_retries):
                try:
                    response = inference(
                        inputs=prompt,
                        parameters={
                            "max_new_tokens": 500,
                            "return_full_text": False
                        }
                    )
                    
                    if isinstance(response, dict) and "error" in response:
                        error_msg = response["error"]
                        if "loading" in str(error_msg).lower():
                            print(f"Model loading, retrying in {retry_delay}s... ({attempt+1}/{max_retries})")
                            time.sleep(retry_delay)
                            continue
                        elif "rate limit" in str(error_msg).lower():
                            print(f"Rate limited, retrying in {retry_delay}s... ({attempt+1}/{max_retries})")
                            time.sleep(retry_delay)
                            continue
                        elif "not found" in str(error_msg).lower():
                            print(f"❌ Model not found: {error_msg}")
                            print("   This model may not be available through the Inference API")
                            print("   Try a different model like 'gpt2'")
                            return []
                        else:
                            print(f"Hugging Face API error: {error_msg}")
                            break
                    elif isinstance(response, list) and len(response) > 0:
                        result_text = response[0].get('generated_text', '')
                        break
                    else:
                        print(f"Hugging Face unexpected response: {response}")
                        break
                        
                except Exception as e:
                    print(f"Error calling Hugging Face API: {e}")
                    time.sleep(retry_delay)

            if not result_text:
                print(f"No valid output from AI for endpoint {method.upper()} {endpoint}")
                continue

            try:
                start = result_text.find("[")
                end = result_text.rfind("]") + 1
                json_text = result_text[start:end]
                test_cases = json.loads(json_text)
            except Exception as e:
                print(f"Failed to parse AI output: {e}")
                test_cases = []

            for t in test_cases:
                if t["method"].upper() == "GET" and isinstance(t.get("payload"), dict):
                    if t["payload"]:
                        t["endpoint"] += "?" + urlencode(t["payload"])
                    t["payload"] = {}

            all_tests.extend(test_cases)

    return all_tests


def generate_ai_tests(spec_json: str, max_retries: int = 5, retry_delay: int = 5):
    # Try OpenAI first if configured
    if USE_OPENAI and OPENAI_AVAILABLE:
        try:
            print("Using OpenAI for test generation")
            return generate_openai_tests(spec_json)
        except Exception as e:
            print(f"OpenAI test generation failed: {e}")
            print("Falling back to Hugging Face or basic tests")
    
    # Try Hugging Face if configured
    if HF_API_KEY and HUGGINGFACE_HUB_AVAILABLE:
        try:
            print("Using Hugging Face for test generation")
            return generate_huggingface_tests(spec_json, max_retries, retry_delay)
        except Exception as e:
            print(f"Hugging Face test generation failed: {e}")
            print("Falling back to basic test generation")
    
    # Fall back to basic test generation
    print("No AI service configured or available. Generating basic tests instead.")
    return generate_basic_tests(spec_json)