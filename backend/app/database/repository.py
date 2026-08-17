from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Conversation, Message, Memory


def create_conversation(
    db: Session,
    firebase_uid: str,
    conversation_id: str,
    title: str = "New Dialogue",
) -> Conversation:

    conversation = Conversation(
        id=conversation_id,
        firebase_uid=firebase_uid,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    firebase_uid: str,
    conversation_id: str,
) -> Optional[Conversation]:

    statement = (
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.firebase_uid == firebase_uid,
        )
    )

    return db.scalar(statement)


def get_user_conversations(
    db: Session,
    firebase_uid: str,
) -> list[Conversation]:

    statement = (
        select(Conversation)
        .where(
            Conversation.firebase_uid == firebase_uid
        )
        .order_by(
            Conversation.updated_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def add_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    # Update conversation timestamp
    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation:

        conversation.updated_at = (
            datetime.now(timezone.utc)
        )

    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: str,
) -> list[Message]:

    statement = (
        select(Message)
        .where(
            Message.conversation_id ==
            conversation_id
        )
        .order_by(
            Message.created_at.asc()
        )
    )

    return list(
        db.scalars(statement).all()
    )

def add_memory(
    db: Session,
    firebase_uid: str,
    session_id: str,
    content: str,
    importance: float = 1.0,
) -> Memory:

    memory = Memory(
        firebase_uid=firebase_uid,
        session_id=session_id,
        content=content,
        importance=importance,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def get_memories(
    db: Session,
    firebase_uid: str,
    session_id: str,
    limit: int = 10,
) -> list[Memory]:

    statement = (
        select(Memory)
        .where(
            Memory.firebase_uid == firebase_uid,
            Memory.session_id == session_id,
        )
        .order_by(
            Memory.importance.desc(),
            Memory.created_at.desc(),
        )
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )