from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    conversation_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    local_time: Optional[str] = None
    local_date: Optional[str] = None
    language: Optional[str] = "en"
    user_type: Optional[str] = "General User"

class WeatherGroundedFacts(BaseModel):
    location: str
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    condition: Optional[str] = None
    rain_probability: Optional[int] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[float] = None
    visibility: Optional[float] = None
    uv_index: Optional[float] = None
    alerts_count: int = 0
    source: str
    updated_at: str

class ChatResponse(BaseModel):
    session_id: int
    conversation_id: Optional[int] = None
    message: str
    answer: Optional[str] = None
    role: str = "assistant"
    intent: str
    requires_weather_data: bool = False
    language: str = "en"
    location: Optional[Dict[str, Any]] = None
    sources: List[str] = []
    data_timestamp: Optional[str] = None
    generated_at: Optional[str] = None
    tool_results: List[Dict[str, Any]] = []
    grounded_weather: Optional[WeatherGroundedFacts] = None
    advisory: Optional[str] = None
    source_attribution: str
    updated_at: str
    suggested_questions: List[str] = []

    def __init__(self, **data):
        if "answer" not in data or not data["answer"]:
            data["answer"] = data.get("message", "")
        if "conversation_id" not in data or data["conversation_id"] is None:
            data["conversation_id"] = data.get("session_id")
        super().__init__(**data)

class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    intent: Optional[str] = None
    location_referenced: Optional[str] = None
    source_attribution: Optional[str] = None
    timestamp: str
    created_at: Optional[str] = None

    def __init__(self, **data):
        if "created_at" not in data or not data["created_at"]:
            data["created_at"] = data.get("timestamp")
        super().__init__(**data)

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    language: Optional[str] = "en"
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ConversationUpdate(BaseModel):
    title: str

class ConversationSummaryOut(BaseModel):
    id: int
    title: str
    language: str
    location_name: Optional[str] = None
    message_count: int = 0
    last_message: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class ChatSessionOut(BaseModel):
    id: int
    title: str
    language: Optional[str] = "en"
    location_name: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    messages: List[ChatMessageOut] = []

    class Config:
        from_attributes = True
