from typing import Optional
import os
import httpx
from .config import get_settings


async def call_gemini(prompt: str, history: list[dict] | None = None) -> str:
    settings = get_settings()
    api_key = settings.genie_api_key or os.getenv("GENIE_API_KEY")
    if not api_key:
        # Fail closed with a clear message if the key is missing
        return "[Backend] Missing GENIE_API_KEY; cannot contact Gemini."

    # Allow overriding the model via env; default to a flash model
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    contents: list[dict] = []
    # Convert simple history to Gemini parts
    # Expecting history items like {role: 'user'|'assistant', content: '...'}
    if history:
        for m in history[-20:]:  # limit context
            role = 'user' if m.get('role') == 'user' else 'model'
            contents.append({
                "role": role,
                "parts": [{"text": (m.get('content') or '')[:8000]}]
            })

    contents.append({
        "role": "user",
        "parts": [{"text": prompt[:8000]}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.7}
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if resp.status_code != 200:
            # Return a concise error surface for troubleshooting
            return f"[Gemini error {resp.status_code}] {resp.text[:300]}"
        data = resp.json()
        # Safely extract the first candidate's text
        try:
            candidates = data.get("candidates") or []
            if not candidates:
                return "[Gemini] No candidates returned."
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            text = "\n".join(t for t in texts if t).strip()
            return text or "[Gemini] Empty response."
        except Exception:
            return "[Gemini] Unexpected response format."


