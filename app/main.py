from fastapi import Depends, FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .auth import verify_token, is_allowed_origin
from .llm import call_gemini
from .config import get_settings
from dotenv import load_dotenv
import google.generativeai as genai


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    history: list[Message] | None = None


load_dotenv()
app = FastAPI(title="Yoda Backend", version="0.1.0")

# CORS configured from ALLOWED_ORIGINS
settings = get_settings()
allowed = settings.allowed_origins or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/v1/chat")
async def chat(req: ChatRequest, request: Request, client: str = Depends(verify_token)):
    if not is_allowed_origin(request):
        raise HTTPException(status_code=403, detail="Domain not allowed")
    reply = await call_gemini(req.prompt, req.history or [])
    return {"reply": reply}


# --- Session-based Gemini chat APIs ---
settings = get_settings()
if settings.genie_api_key:
    genai.configure(api_key=settings.genie_api_key)

_sessions: dict[int, any] = {}


@app.post("/v1/start_session")
async def start_session(request: Request, client: str = Depends(verify_token)):
    if not is_allowed_origin(request):
        raise HTTPException(status_code=403, detail="Domain not allowed")
    model_name = "gemini-2.0-flash"
    chat = genai.GenerativeModel(model_name).start_chat()
    session_id = id(chat)
    _sessions[session_id] = chat
    return {"session_id": session_id}


class SendMessageRequest(BaseModel):
    session_id: int
    message: str


@app.post("/v1/send_message")
async def send_message(req: SendMessageRequest, request: Request, client: str = Depends(verify_token)):
    if not is_allowed_origin(request):
        raise HTTPException(status_code=403, detail="Domain not allowed")
    chat = _sessions.get(req.session_id)
    print(chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    response = chat.send_message(req.message)
    return {"reply": getattr(response, 'text', '') or str(response)}


class EndSessionRequest(BaseModel):
    session_id: int


@app.post("/v1/end_session")
async def end_session(req: EndSessionRequest, request: Request, client: str = Depends(verify_token)):
    if not is_allowed_origin(request):
        raise HTTPException(status_code=403, detail="Domain not allowed")
    if req.session_id in _sessions:
        del _sessions[req.session_id]
    return {"success": True}


