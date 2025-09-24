import requests
import json
import time
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("Hugging Face API key not set in .env")

MODEL_NAME = "tiiuae/falcon-7b-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def generate_ai_tests(spec_json: str, max_retries: int = 3, retry_delay: int = 2):
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

Return the output as a JSON array of objects:
[{{"endpoint": "...", "method": "...", "payload": {{}}}}, ...]
"""

            result_text = ""
            for attempt in range(max_retries):
                try:
                    response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt}, timeout=30)
                    res_json = response.json()

                    if isinstance(res_json, list) and len(res_json) > 0:
                        result_text = res_json[0].get('generated_text', '')
                        break
                    elif isinstance(res_json, dict) and 'generated_text' in res_json:
                        result_text = res_json['generated_text']
                        break
                    elif isinstance(res_json, dict) and 'error' in res_json and 'loading' in res_json['error']:
                        print(f"Model loading, retrying... ({attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"Hugging Face unexpected response: {res_json}")
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
