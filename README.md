✨ AETHER – Automated Evaluation & Testing Helper for Endpoint Reliability
"Your heroic AI QA guardian."

🔥 What is AETHER?
AETHER is an AI-powered, self-improving API testing assistant.
It acts like a tireless QA engineer for your APIs, autonomously generating and running tests, finding edge cases, and learning from failures to continuously improve your test coverage.
Generates functional, edge, and security tests automatically.
Explains failures in plain, developer-friendly language.
Builds a regression suite from past bugs.
Continuously improves itself with every test run.
Think of AETHER as a heroic guardian watching over your APIs, ensuring reliability and security without you lifting a finger.

🛠️ How It's Built
FastAPI backend → orchestrates test generation and execution.
Async workers → handle test runs efficiently using httpx.
Database → PostgreSQL or SQLite to store test cases, results, and learned patterns.
AI Layer → LLMs (OpenAI free tier / Hugging Face models / local LLMs) for:
Generating new test variation.
Explaining failures and suggesting fixes
Dashboard/UI → FastAPI + Jinja2 templates or React for uploading API specs and viewing results.

⚙️ How AETHER Works
Input: Upload OpenAPI spec, Postman collection, or repo URL.
Analyze: Parse endpoints, schemas, auth methods.
Generate Tests:
Functional + edge cases
Security fuzzing (auth bypass, SQLi, malformed inputs)
Execute Tests: Run async tests, capture logs & metrics.
Analyze & Explain: LLM explains failures, suggests fixes.
Self-Learning:
Failed tests become regression tests.
Patterns from multiple APIs improve AI-generated test coverage.

🎯 Who Should Use AETHER?
Startups → no QA team, instant API coverage.
Small & Medium Dev Teams → reduce time writing repetitive tests.
Enterprises → supplement manual QA with continuous AI-driven testing.

💡 Why AETHER?
Saves time → no manual test writing.
Catches bugs early → AI-generated edge & security tests.
Continuous coverage → test suite evolves with your API.
Premium feel → like having a personal AI QA hero.

📦 Setup Instructions

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Choose one AI provider:
     * For Hugging Face: Get your API key from https://huggingface.co/settings/tokens
     * For OpenAI: Get your API key from https://platform.openai.com/api-keys
   - Add your API key to the `.env` file
6. Run DB migrations:
   ```
   alembic upgrade head
   ```
7. Start the server:
   ```
   uvicorn app.main:app --reload --port 8000
   ```

🧪 Testing Your AI Configuration

To test your AI configuration, you can use the provided test scripts:

For Hugging Face (using huggingface_hub library):
```
python test_hf_local.py
```

For OpenAI:
```
python test_openai.py
```

Or the original direct API approach:
```
python test_huggingface.py
```

📦 Roadmap (MVP → Future)
✅ MVP: Test generation + execution + results dashboard.
🔜 CI/CD integration (GitHub/GitLab).
🔜 Security fuzzing with OWASP payloads.
🔜 Shared "bug knowledge base" for improved AI coverage.
🔜 Multi-tenant SaaS with usage & billing.