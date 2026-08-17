import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..chat_engine import ChatEngine
from ..auth.dependencies import get_current_user
from ..database.connection import get_db
from ..database.repository import (
    create_conversation,
    get_conversation,
    get_user_conversations,
    get_conversation_messages,
    add_message,
)


router = APIRouter()

engine = ChatEngine()


# ============================================
# Request / Response Models
# ============================================

class ChatRequest(BaseModel):
    session_id: str
    message: str


class Source(BaseModel):
    title: str
    year: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[Source]

class ConversationSummary(BaseModel):
    id: str
    title: str


class MessageResponse(BaseModel):
    role: str
    content: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse]

# ============================================
# Get User Conversations
# ============================================

@router.get(
    "/conversations",
    response_model=List[ConversationSummary]
)
def get_conversations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Guests do not have persistent conversations
    if not current_user:
        return []

    firebase_uid = current_user.get("uid")

    conversations = get_user_conversations(
        db=db,
        firebase_uid=firebase_uid
    )

    return [
        ConversationSummary(
            id=conversation.id,
            title=conversation.title
        )
        for conversation in conversations
    ]

# ============================================
# Get Individual Conversation
# ============================================

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetail
)
def get_conversation_detail(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    firebase_uid = current_user.get("uid")

    conversation = get_conversation(
        db=db,
        firebase_uid=firebase_uid,
        conversation_id=conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id
    )

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        messages=[
            MessageResponse(
                role=message.role,
                content=message.content
            )
            for message in messages
        ]
    )

# ============================================
# Normal Chat Endpoint
# ============================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    result = engine.chat(
        session_id=request.session_id,
        user_message=request.message,
        db=db,
        firebase_uid=(
            current_user.get("uid")
            if current_user
            else None
        ),
    )

    return ChatResponse(
        response=result["response"],
        sources=result["sources"]
    )


# ============================================
# Streaming Helper
# ============================================

def sse_event(data: dict) -> str:

    return (
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )



# ============================================
# Streaming Chat Endpoint
# ============================================

@router.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    def event_generator():

        try:

            # ========================================
            # AUTHENTICATION / PERSISTENCE
            # ========================================

            if current_user:

                firebase_uid = current_user.get("uid")

                print(
                    "\n[AUTHENTICATED USER]",
                    firebase_uid,
                    current_user.get("email")
                )

                # ------------------------------------
                # Find existing conversation
                # ------------------------------------

                conversation = get_conversation(
                    db=db,
                    firebase_uid=firebase_uid,
                    conversation_id=request.session_id
                )

                # ------------------------------------
                # Create conversation if needed
                # ------------------------------------

                if conversation is None:

                    conversation = create_conversation(
                        db=db,
                        firebase_uid=firebase_uid,
                        conversation_id=request.session_id,
                        title=request.message[:50]
                    )

                    print(
                        "[DB] Created conversation:",
                        request.session_id
                    )

                # ------------------------------------
                # Save user message
                # ------------------------------------

                add_message(
                    db=db,
                    conversation_id=request.session_id,
                    role="user",
                    content=request.message
                )

                print(
                    "[DB] Saved user message"
                )

            else:

                print(
                    "\n[GUEST USER]"
                )

            # ========================================
            # STREAM NIETZSCHE RESPONSE
            # ========================================

            assistant_text = []

            for event in engine.chat_stream(
                session_id=request.session_id,
                user_message=request.message,
                db=db,
                firebase_uid=(
                    current_user.get("uid")
                    if current_user
                    else None
                ),
            ):

                # Accumulate assistant tokens
                if event.get("type") == "token":

                    assistant_text.append(
                        event.get("text", "")
                    )

                # Forward existing SSE event
                yield sse_event(event)

            # ========================================
            # SAVE COMPLETE ASSISTANT RESPONSE
            # ========================================

            if current_user:

                answer = "".join(
                    assistant_text
                ).strip()

                if answer:

                    add_message(
                        db=db,
                        conversation_id=request.session_id,
                        role="assistant",
                        content=answer
                    )

                    print(
                        "[DB] Saved assistant message"
                    )

        except Exception as exc:

            print(
                "\n[STREAM ERROR]",
                repr(exc)
            )

            yield sse_event({
                "type": "error",
                "message":
                    "Nietzsche is temporarily unavailable. "
                    "Please try again shortly."
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ============================================
# Local Testing
# ============================================

if __name__ == "__main__":

    engine = ChatEngine()

    session_id = "demo"

    print("=" * 70)
    print("Nietzsche Digital Twin")
    print("Type 'exit' to quit.")
    print("=" * 70)

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in [
            "exit",
            "quit"
        ]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        response = engine.chat(
            session_id=session_id,
            user_message=user_input
        )

        print("\nNietzsche:\n")
        print(response["response"])

        print("\nSources:")

        for source in response["sources"]:

            print(
                f"- {source['title']}"
            )