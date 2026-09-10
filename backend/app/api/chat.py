import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.auth.deps import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionOut,
    ChatMessageOut,
    ConversationCreate,
    ConversationUpdate,
    ConversationSummaryOut
)
from app.ai.engine import ai_service

router = APIRouter(prefix="/chat", tags=["Chatbot"])

# =====================================================================
# CHAT INTERACTION (POST /api/chat and POST /api/chat/message)
# =====================================================================
@router.post("", response_model=ChatResponse)
@router.post("/message", response_model=ChatResponse)
async def chat_interaction(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        user_id = user.id if user else None
        return await ai_service.process_message(request=request, db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process chat inquiry: {str(e)}"
        )

# =====================================================================
# CONVERSATIONS LIST (GET /api/chat/conversations)
# =====================================================================
@router.get("/conversations", response_model=List[ConversationSummaryOut])
def get_conversations(
    search: Optional[str] = Query(None, description="Search query across title and message contents"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Returns user's conversations with message counts and last message snippet.
    Authenticated users only access their own conversations.
    Guest users access guest sessions.
    Supports searching by title and message content.
    """
    if user:
        query = db.query(ChatSession).filter(ChatSession.user_id == user.id)
    else:
        query = db.query(ChatSession).filter(ChatSession.user_id.is_(None))

    if search and search.strip():
        term = f"%{search.strip()}%"
        # Search by title OR message content
        query = query.filter(
            or_(
                ChatSession.title.ilike(term),
                ChatSession.messages.any(ChatMessage.content.ilike(term))
            )
        )

    sessions = query.order_by(
        ChatSession.updated_at.desc(),
        ChatSession.created_at.desc()
    ).limit(50).all()

    summaries = []
    for s in sessions:
        msgs = s.messages
        last_msg = msgs[-1].content if msgs else None
        created_str = (s.created_at or datetime.datetime.utcnow()).isoformat()
        updated_str = (s.updated_at or s.created_at or datetime.datetime.utcnow()).isoformat()

        summaries.append(ConversationSummaryOut(
            id=s.id,
            title=s.title or "New Conversation",
            language=s.language or "en",
            location_name=s.location_name or "Guntur, Andhra Pradesh",
            message_count=len(msgs),
            last_message=last_msg,
            created_at=created_str,
            updated_at=updated_str
        ))

    return summaries

# =====================================================================
# CREATE NEW CONVERSATION (POST /api/chat/conversations)
# =====================================================================
@router.post("/conversations", response_model=ChatSessionOut)
def create_conversation(
    conv_data: ConversationCreate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Creates a new conversation session explicitly.
    """
    now = datetime.datetime.utcnow()
    new_session = ChatSession(
        user_id=user.id if user else None,
        title=conv_data.title or "New Conversation",
        language=conv_data.language or "en",
        location_name=conv_data.location_name or "Guntur, Andhra Pradesh",
        latitude=conv_data.latitude,
        longitude=conv_data.longitude,
        created_at=now,
        updated_at=now
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return ChatSessionOut(
        id=new_session.id,
        title=new_session.title,
        language=new_session.language,
        location_name=new_session.location_name,
        created_at=new_session.created_at.isoformat(),
        updated_at=new_session.updated_at.isoformat() if new_session.updated_at else new_session.created_at.isoformat(),
        messages=[]
    )

# =====================================================================
# GET CONVERSATION DETAILS (GET /api/chat/conversations/{conversation_id})
# =====================================================================
@router.get("/conversations/{conversation_id}", response_model=ChatSessionOut)
def get_conversation_details(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Loads the complete conversation history for a specific conversation.
    Verifies ownership if user is authenticated.
    """
    session = db.query(ChatSession).filter(ChatSession.id == conversation_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Ensure users can ONLY access their own conversations
    if user and session.user_id is not None and session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access another user's conversation")

    msgs = [
        ChatMessageOut(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            intent=m.intent,
            location_referenced=m.location_referenced,
            source_attribution=m.source_attribution,
            timestamp=m.timestamp.isoformat(),
            created_at=m.timestamp.isoformat()
        ) for m in session.messages
    ]

    created_str = (session.created_at or datetime.datetime.utcnow()).isoformat()
    updated_str = (session.updated_at or session.created_at or datetime.datetime.utcnow()).isoformat()

    return ChatSessionOut(
        id=session.id,
        title=session.title or "New Conversation",
        language=session.language or "en",
        location_name=session.location_name or "Guntur, Andhra Pradesh",
        created_at=created_str,
        updated_at=updated_str,
        messages=msgs
    )

# =====================================================================
# UPDATE CONVERSATION (PATCH /api/chat/conversations/{conversation_id})
# =====================================================================
@router.patch("/conversations/{conversation_id}", response_model=ChatSessionOut)
def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Updates conversation title.
    """
    session = db.query(ChatSession).filter(ChatSession.id == conversation_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if user and session.user_id is not None and session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot modify another user's conversation")

    if update_data.title and update_data.title.strip():
        session.title = update_data.title.strip()
        session.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(session)

    msgs = [
        ChatMessageOut(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            intent=m.intent,
            location_referenced=m.location_referenced,
            source_attribution=m.source_attribution,
            timestamp=m.timestamp.isoformat(),
            created_at=m.timestamp.isoformat()
        ) for m in session.messages
    ]

    created_str = (session.created_at or datetime.datetime.utcnow()).isoformat()
    updated_str = (session.updated_at or session.created_at or datetime.datetime.utcnow()).isoformat()

    return ChatSessionOut(
        id=session.id,
        title=session.title,
        language=session.language or "en",
        location_name=session.location_name,
        created_at=created_str,
        updated_at=updated_str,
        messages=msgs
    )

# =====================================================================
# DELETE CONVERSATION (DELETE /api/chat/conversations/{conversation_id})
# =====================================================================
@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Deletes conversation and associated messages.
    """
    session = db.query(ChatSession).filter(ChatSession.id == conversation_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if user and session.user_id is not None and session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot delete another user's conversation")

    db.delete(session)
    db.commit()
    return {"message": "Conversation deleted successfully", "id": conversation_id}

# =====================================================================
# BACKWARDS COMPATIBILITY ALIASES (GET /sessions, DELETE /sessions)
# =====================================================================
@router.get("/sessions", response_model=List[ChatSessionOut])
def get_user_sessions(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    if not user:
        sessions = db.query(ChatSession).filter(ChatSession.user_id.is_(None)).order_by(ChatSession.created_at.desc()).limit(15).all()
    else:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).order_by(ChatSession.created_at.desc()).limit(30).all()

    results = []
    for s in sessions:
        msgs = [
            ChatMessageOut(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                intent=m.intent,
                location_referenced=m.location_referenced,
                source_attribution=m.source_attribution,
                timestamp=m.timestamp.isoformat(),
                created_at=m.timestamp.isoformat()
            ) for m in s.messages
        ]
        created_str = (s.created_at or datetime.datetime.utcnow()).isoformat()
        updated_str = (s.updated_at or s.created_at or datetime.datetime.utcnow()).isoformat()
        results.append(ChatSessionOut(
            id=s.id,
            title=s.title,
            language=s.language or "en",
            location_name=s.location_name,
            created_at=created_str,
            updated_at=updated_str,
            messages=msgs
        ))
    return results

@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
def get_session_details(session_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_user_optional)):
    return get_conversation_details(conversation_id=session_id, db=db, user=user)

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_user_optional)):
    return delete_conversation(conversation_id=session_id, db=db, user=user)
