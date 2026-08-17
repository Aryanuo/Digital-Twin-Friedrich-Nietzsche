import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


load_dotenv()


COLLECTION_NAME = "nietzsche"


# ==========================================
# Embedding model
# ==========================================

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)


# ==========================================
# Qdrant Cloud
# ==========================================

QDRANT_URL = os.getenv(
    "QDRANT_URL"
)

QDRANT_API_KEY = os.getenv(
    "QDRANT_API_KEY"
)


if not QDRANT_URL:
    raise ValueError(
        "QDRANT_URL is not configured."
    )


if not QDRANT_API_KEY:
    raise ValueError(
        "QDRANT_API_KEY is not configured."
    )


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


class Retriever:

    def __init__(self, top_k=5):

        self.top_k = top_k


    def retrieve(self, query: str):

        # ----------------------------------
        # Generate query embedding
        # ----------------------------------

        query_embedding = model.encode(
            query,
            normalize_embeddings=True
        ).tolist()


        # ----------------------------------
        # Search Qdrant Cloud
        # ----------------------------------

        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=self.top_k
        )


        # ----------------------------------
        # Build documents
        # ----------------------------------

        documents = []


        for point in response.points:

            payload = point.payload


            documents.append({

                "score":
                    point.score,

                "text":
                    payload.get(
                        "text",
                        ""
                    ),

                "metadata": {

                    "title":
                        payload.get(
                            "title"
                        ),

                    "category":
                        payload.get(
                            "category"
                        ),

                    "year":
                        payload.get(
                            "year"
                        ),

                    "chunk_id":
                        payload.get(
                            "chunk_id"
                        ),

                    "source_file":
                        payload.get(
                            "source_file"
                        )
                }
            })


        return documents