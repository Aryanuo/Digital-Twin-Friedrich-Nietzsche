from typing import List


class ContextProcessor:

    # Lower number = higher priority.
    # Used only as a tie-breaker after similarity.
    SOURCE_PRIORITY = {
        "books": 1,
        "letters": 2,
        "lectures": 2,
        "essays": 2,
        "notebooks": 3,
        "biographies": 4,
        "Walter Kaufmann": 5,
        "academic_papers": 5,
        "secondary_sources": 5,
    }

    def __init__(self, max_chunks: int = 3):
        self.max_chunks = max_chunks

    def process(self, documents: List[dict]) -> List[dict]:

        if not documents:
            return []

        # ----------------------------
        # Remove duplicate chunks
        # ----------------------------

        seen = set()
        unique_docs = []

        for doc in documents:

            text = doc.get("text", "").strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)
            unique_docs.append(doc)

        # ----------------------------
        # Rank primarily by similarity
        # ----------------------------

        unique_docs.sort(
            key=lambda d: (
                -d.get("score", 0),
                self.SOURCE_PRIORITY.get(
                    d.get("metadata", {}).get("category", ""),
                    99
                )
            )
        )

        # ----------------------------
        # Keep only strongest chunks
        # ----------------------------

        return unique_docs[:self.max_chunks]


if __name__ == "__main__":

    from retriever import Retriever

    retriever = Retriever(top_k=5)
    processor = ContextProcessor(max_chunks=3)

    docs = retriever.retrieve(
        "What is the will to power?"
    )

    docs = processor.process(docs)

    for i, doc in enumerate(docs, start=1):

        print("=" * 80)
        print(f"Result {i}")
        print(f"Title : {doc['metadata']['title']}")
        print(f"Score : {doc['score']:.4f}")
        print(f"Category : {doc['metadata']['category']}")
        print("-" * 80)
        print(doc["text"][:600])
        print()