from pathlib import Path
import json

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ==========================================
# Configuration
# ==========================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"

CHUNK_DIR = DATA_DIR / "chunks"
OUTPUT_DIR = DATA_DIR / "embedding"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading embedding model...")

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

print("Model loaded.\n")


def process_file(chunk_file):

    with open(chunk_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    output = []

    for chunk, embedding in zip(chunks, embeddings):

        output.append({
            "chunk_id": chunk["chunk_id"],
            "embedding": embedding.tolist(),
            "text": chunk["text"],
            "metadata": chunk["metadata"]
        })

    out_file = OUTPUT_DIR / f"{chunk_file.stem}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ {chunk_file.name}")


def main():

    files = list(CHUNK_DIR.rglob("*_chunks.json"))

    print(f"Found {len(files)} files\n")

    for file in files:

        process_file(file)

    print("\nAll embeddings generated successfully!")


if __name__ == "__main__":
    main()