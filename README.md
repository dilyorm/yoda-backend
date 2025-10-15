Yoda Backend (FastAPI)

Environment variables:

- GENIE_API_KEY: Gemini 2.5 Flash API key (not exposed to frontend)
- VALID_CLIENT_TOKENS: Comma-separated list of allowed client tokens
- ALLOWED_ORIGINS: Comma-separated list of allowed origins (e.g., https://example.com, http://localhost:5173)

Run locally:

```
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Docker:

```
docker build -t yoda-backend .
docker run -p 8000:8000 --env-file .env yoda-backend
```

API:

- POST /v1/chat { "prompt": "..." } -> { "reply": "..." }


