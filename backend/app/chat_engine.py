from app.memory.session_memory import SessionMemory
from app.memory.long_term_memory import LongTermMemory

from app.rag.context_processor import ContextProcessor
from app.rag.retriever import Retriever
from app.rag.prompt_builder import PromptBuilder

from app.llm.gemini_client import GeminiClient

from sqlalchemy.orm import Session


class ChatEngine:

    def __init__(self):

        self.session_memory = SessionMemory(
            max_messages=20,
            context_messages=6
        )
        self.long_term_memory = LongTermMemory()

        self.context_processor = ContextProcessor(
            max_chunks=3
        )

        self.retriever = Retriever(
            top_k=5
        )

        self.prompt_builder = PromptBuilder()

        self.llm = GeminiClient()

    def chat(
        self,
        session_id: str,
        user_message: str,
        db: Session = None,
        firebase_uid: str = None,
    ) -> dict:

        # ---------------------------------
        # Get existing conversation context
        # BEFORE adding current question
        # ---------------------------------

        conversation_history = (
            self.session_memory.format_history(
                session_id
            )
        )

        # ---------------------------------
        # Get long-term memory
        # ---------------------------------

        long_term_memory = ""

        if db is not None and firebase_uid:

            long_term_memory = (
                self.long_term_memory.format_memories(
                    db=db,
                    firebase_uid=firebase_uid,
                    session_id=session_id,
                )
            )
    
        
        # ---------------------------------
        # Store current user message
        # ---------------------------------

        self.session_memory.add_user_message(
            session_id,
            user_message
        )

        # ---------------------------------
        # Retrieve Nietzsche sources
        # ---------------------------------

        retrieved_docs = self.retriever.retrieve(
            user_message
        )

        retrieved_docs = self.context_processor.process(
            retrieved_docs
        )

        # ---------------------------------
        # Build prompt
        # ---------------------------------

        prompt = self.prompt_builder.build(
            user_query=user_message,
            retrieved_docs=retrieved_docs,
            conversation_history=conversation_history,
            long_term_memory=long_term_memory
        )

        # ---------------------------------
        # Generate answer
        # ---------------------------------

        answer = self.llm.generate(
            prompt
        )
        

        # ---------------------------------
        # Store assistant response
        # ---------------------------------

        self.session_memory.add_assistant_message(
            session_id,
            answer
        )

        # ---------------------------------
        # Save meaningful long-term memory
        # ---------------------------------

        if (
            db is not None
            and firebase_uid
            and len(user_message.split()) >= 8
        ):

            self.long_term_memory.add_memory(
                db=db,
                firebase_uid=firebase_uid,
                session_id=session_id,
                content=user_message,
                importance=1.0,
            )

        # ---------------------------------
        # Return answer + sources
        # ---------------------------------

        # ---------------------------------
        # Build unique source list
        # ---------------------------------

        sources = []
        seen_sources = set()

        for doc in retrieved_docs:

            metadata = doc["metadata"]

            title = metadata.get("title", "Unknown source")
            year = metadata.get("year")

            source_key = (
                title.strip().lower(),
                year
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            sources.append(
                {
                    "title": title,
                    "year": year
                }
            )


        return {
            "response": answer,
            "sources": sources
        }
    
    def chat_stream(
        self,
        session_id: str,
        user_message: str,
        db: Session = None,
        firebase_uid: str = None,
    ):

        # ---------------------------------
        # Get existing conversation context
        # BEFORE adding current question
        # ---------------------------------

        conversation_history = (
            self.session_memory.format_history(
                session_id
            )
        )

        # ---------------------------------
        # Get long-term memory
        # ---------------------------------

        long_term_memory = ""

        if db is not None and firebase_uid:

            long_term_memory = (
                self.long_term_memory.format_memories(
                    db=db,
                    firebase_uid=firebase_uid,
                    session_id=session_id,
                )
            )

        # ---------------------------------
        # Store current user message
        # ---------------------------------

        self.session_memory.add_user_message(
            session_id,
            user_message
        )

        # ---------------------------------
        # Retrieve Nietzsche sources
        # ---------------------------------

        retrieved_docs = self.retriever.retrieve(
            user_message
        )

        retrieved_docs = self.context_processor.process(
            retrieved_docs
        )

        # ---------------------------------
        # Build prompt
        # ---------------------------------

        prompt = self.prompt_builder.build(
            user_query=user_message,
            retrieved_docs=retrieved_docs,
            conversation_history=conversation_history,
            long_term_memory=long_term_memory
        )

        # ---------------------------------
        # Stream Gemini response
        # ---------------------------------

        full_answer = []

        for chunk in self.llm.generate_stream(prompt):

            if not chunk:
                continue

            full_answer.append(chunk)

            yield {
                "type": "token",
                "text": chunk
            }

        
        # ---------------------------------
        # Complete response
        # ---------------------------------

        answer = "".join(full_answer).strip()

        # ---------------------------------
        # Store assistant response
        # ---------------------------------

        self.session_memory.add_assistant_message(
            session_id,
            answer
        )

        # ---------------------------------
        # Save meaningful long-term memory
        # ---------------------------------

        if( db is not None
            and firebase_uid
            and len(user_message.split()) >= 8
        ):

            self.long_term_memory.add_memory(
                db=db,
                firebase_uid=firebase_uid,
                session_id=session_id,
                content=user_message,
                importance=1.0
            )

        # ---------------------------------
        # Build unique source list
        # ---------------------------------

        sources = []
        seen_sources = set()

        for doc in retrieved_docs:

            metadata = doc["metadata"]

            title = metadata.get(
                "title",
                "Unknown source"
            )

            year = metadata.get("year")

            source_key = (
                title.strip().lower(),
                year
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            sources.append({
                "title": title,
                "year": year
            })

        # ---------------------------------
        # Send sources
        # ---------------------------------

        yield {
            "type": "sources",
            "sources": sources
        }

        # ---------------------------------
        # Finished
        # ---------------------------------

        yield {
            "type": "done"
        }


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
                f"- {source['title']} "
                # f"({source['year']})"
            )