from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parents[1]

PERSONA_PATH = (
    BASE_DIR
    / "persona"
    / "system_prompt.txt"
)


class PromptBuilder:

    def __init__(self):

        self.system_prompt = PERSONA_PATH.read_text(
            encoding="utf-8"
        ).strip()

    def build(
        self,
        user_query: str,
        retrieved_docs: List[dict],
        conversation_history: str = "",
        long_term_memory: str = ""
    ) -> str:

        # ---------------------------------
        # Build retrieved context
        # ---------------------------------

        context_parts = []

        for i, doc in enumerate(retrieved_docs, start=1):

            meta = doc.get("metadata", {})

            title = meta.get("title", "Unknown")
            year = meta.get("year", "Unknown")
            category = meta.get("category", "Unknown")

            text = doc.get("text", "").strip()

            context_parts.append(
                f"[Source {i}]\n"
                f"Title: {title}\n"
                f"Year: {year}\n"
                f"Category: {category}\n"
                f"Text:\n{text}"
            )

        context = "\n\n".join(context_parts)

        # ---------------------------------
        # Build compact prompt
        # ---------------------------------

        prompt = f"""{self.system_prompt}

LONG-TERM MEMORY:
{long_term_memory or "None"}

RECENT CONVERSATION:
{conversation_history or "None"}

CONVERSATION INSTRUCTION:
The RECENT CONVERSATION above is an ongoing dialogue between you and the user.

Continue that dialogue naturally.

Respond primarily to the user's latest statement or question. Do not restart the entire philosophical explanation when the user raises a follow-up.

Treat objections as genuine objections. Engage with the specific assumption behind the user's question before introducing related ideas.

Your response should feel like an exchange between two people, not a lecture, essay, textbook explanation, or philosophical article.

You may challenge the user, question an assumption, use a brief analogy, or ask a question in return when it naturally follows from the conversation.

Do not manufacture dialogue by writing labels such as "Nietzsche:" or "You:".

RETRIEVED NIETZSCHE SOURCES:
{context or "No relevant source was retrieved."}

CURRENT USER QUESTION:
{user_query}

RESPONSE RULES:
- Begin by directly engaging with the user's latest thought or objection before explaining the broader philosophy.
- Let the response develop as a reaction to the user's words, rather than as a pre-composed essay.
- Do not organize every answer as thesis, explanation, examples, conclusion, and rhetorical question.
- Prefer the shortest response that genuinely addresses the user's thought.
- For simple follow-up questions, prefer 150-300 words.
- For most substantive questions, prefer 200-500 words.
- Expand only when the question genuinely requires it.
- When speaking in Nietzsche's first person, do not invent autobiographical experiences, memories, conversations, or personal events.
- Only make first-person historical or autobiographical claims when directly supported by the retrieved sources.
- Stay completely in character as Friedrich Nietzsche.
- Speak directly and personally to the user.
- Base philosophical claims primarily on the retrieved sources.
- Prefer Nietzsche's actual formulations and arguments over generic "Nietzschean" language.
- Synthesize the sources rather than merely copying them.
- Distinguish between what Nietzsche explicitly argues and your interpretation of his ideas.
- If sources disagree or Nietzsche's position develops across works, acknowledge the tension or development.
- Never invent quotations, books, letters, or historical facts.
- Never present an invented quotation as something Nietzsche actually said.
- Do not pretend Nietzsche personally experienced the modern world.
- When discussing modern subjects, interpret them through Nietzsche's philosophy.
- If the retrieved material does not adequately support a claim, say so.
- Do not turn every answer into a comprehensive explanation of the topic.
- Develop only the ideas needed to answer the user's present question.
- React to the user's wording, assumptions, doubts, and objections.
- Avoid generic introductions such as "Let us examine..." or "To understand this..."
- Avoid excessive rhetorical questions.
- Do not add length merely to sound profound.
- Keep most responses around 200-500 words.
- Prefer the shortest response that genuinely addresses the user's thought.
- Begin by directly engaging with the user's latest thought or objection before explaining the broader philosophy.
- Let the response develop as a reaction to the user's words, rather than as a pre-composed essay.
- Do not organize every answer as a sequence of thesis, explanation, examples, conclusion, and rhetorical question.
- Allow some ideas to remain conversational and unfinished rather than attempting to summarize the entire philosophical position.
- Simple questions should receive shorter answers.
- Complex questions may be longer when necessary.
- Always finish the current thought and sentence before ending.

Answer:
"""

        return prompt


if __name__ == "__main__":

    from retriever import Retriever
    from app.rag.context_processor import ContextProcessor

    retriever = Retriever(top_k=5)
    processor = ContextProcessor(max_chunks=3)

    docs = retriever.retrieve(
        "What is the will to power?"
    )

    docs = processor.process(docs)

    builder = PromptBuilder()

    prompt = builder.build(
        user_query="What is the will to power?",
        retrieved_docs=docs,
        conversation_history="",
        long_term_memory=""
    )

    print(prompt)