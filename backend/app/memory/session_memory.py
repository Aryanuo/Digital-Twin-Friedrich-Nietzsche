from collections import defaultdict
from typing import Dict, List


class SessionMemory:

    def __init__(
        self,
        max_messages: int = 20,
        context_messages: int = 6
    ):
        self.max_messages = max_messages
        self.context_messages = context_messages

        self.sessions: Dict[str, List[dict]] = defaultdict(list)

    # ---------------------------------
    # Store user message
    # ---------------------------------

    def add_user_message(
        self,
        session_id: str,
        content: str
    ):

        self.sessions[session_id].append(
            {
                "role": "user",
                "content": content
            }
        )

        self._trim(session_id)

    # ---------------------------------
    # Store assistant message
    # ---------------------------------

    def add_assistant_message(
        self,
        session_id: str,
        content: str
    ):

        self.sessions[session_id].append(
            {
                "role": "assistant",
                "content": content
            }
        )

        self._trim(session_id)

    # ---------------------------------
    # Get complete stored history
    # ---------------------------------

    def get_history(self, session_id: str):

        return self.sessions[session_id]

    # ---------------------------------
    # Get only recent context
    # ---------------------------------

    def get_recent_history(
        self,
        session_id: str
    ):

        return self.sessions[session_id][-self.context_messages:]

    # ---------------------------------
    # Format recent history
    # ---------------------------------

    def format_history(self, session_id: str):

        history = self.get_recent_history(session_id)

        formatted = []

        for message in history:

            formatted.append(
                f"{message['role'].upper()}: {message['content']}"
            )

        return "\n".join(formatted)

    # ---------------------------------
    # Clear session
    # ---------------------------------

    def clear(self, session_id: str):

        self.sessions.pop(session_id, None)

    # ---------------------------------
    # Keep memory bounded
    # ---------------------------------

    def _trim(self, session_id: str):

        if len(self.sessions[session_id]) > self.max_messages:

            self.sessions[session_id] = (
                self.sessions[session_id][-self.max_messages:]
            )


if __name__ == "__main__":

    memory = SessionMemory(
        max_messages=20,
        context_messages=6
    )

    sid = "demo"

    for i in range(10):

        memory.add_user_message(
            sid,
            f"User question {i + 1}"
        )

        memory.add_assistant_message(
            sid,
            f"Nietzsche response {i + 1}"
        )

    print("Stored messages:")
    print(len(memory.get_history(sid)))

    print("\nMessages sent to Gemini:")
    print(len(memory.get_recent_history(sid)))

    print("\nFormatted history:")
    print(memory.format_history(sid))