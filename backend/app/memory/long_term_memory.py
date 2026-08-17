from sqlalchemy.orm import Session

from app.database.repository import (
    add_memory,
    get_memories,
)


class LongTermMemory:

    def add_memory(
        self,
        db: Session,
        firebase_uid: str,
        session_id: str,
        content: str,
        importance: float = 1.0,
    ):

        return add_memory(
            db=db,
            firebase_uid=firebase_uid,
            session_id=session_id,
            content=content,
            importance=importance,
        )

    def get_memories(
        self,
        db: Session,
        firebase_uid: str,
        session_id: str,
        limit: int = 10,
    ):

        return get_memories(
            db=db,
            firebase_uid=firebase_uid,
            session_id=session_id,
            limit=limit,
        )

    def format_memories(
        self,
        db: Session,
        firebase_uid: str,
        session_id: str,
    ):

        memories = self.get_memories(
            db=db,
            firebase_uid=firebase_uid,
            session_id=session_id,
        )

        return "\n".join(
            memory.content
            for memory in memories
        )