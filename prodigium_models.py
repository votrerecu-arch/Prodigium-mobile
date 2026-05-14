from pydantic import BaseModel
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    thinking_mode: bool = False

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    thinking: Optional[str] = None
    tokens_used: int
    mode: str
    agents_activated: List[str]

class ReasonRequest(BaseModel):
    prompt: str

class StatusResponse(BaseModel):
    status: str
    version: str
    mode: str
    cortex_connected: bool
    agents_ready: int
    uptime_seconds: float

class AuthRequest(BaseModel):
    certificate: Optional[str] = None
    api_key: Optional[str] = None

class AuthResponse(BaseModel):
    authorized: bool
    level: str
    token: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    detail: str

class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: dict
