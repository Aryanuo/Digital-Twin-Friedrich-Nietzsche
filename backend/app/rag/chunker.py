import json
from pathlib import Path
from typing import List

# =====================================
# Configuration
# =====================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"

OUTPUT_DIR = DATA_DIR / "chunks"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_WORDS = 500
OVERLAP_PARAGRAPHS = 1


# =====================================
# Utilities
# =====================================

def load_document(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chunks(chunks: List[dict], output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)


def split_into_paragraphs(text: str) -> List[str]:
    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]
    return paragraphs


# =====================================
# Chunk Builder
# =====================================

def create_chunks(document: dict) -> List[dict]:

    paragraphs = split_into_paragraphs(document["text"])

    chunks = []

    current_chunk = []
    current_words = 0
    chunk_index = 1

    for paragraph in paragraphs:

        paragraph_word_count = len(paragraph.split())

        # If adding this paragraph exceeds limit
        if current_chunk and current_words + paragraph_word_count > TARGET_WORDS:

            chunk_text = "\n\n".join(current_chunk)

            chunks.append({
                "chunk_id": f"{document['category']}_{Path(document['source_file']).stem}_{chunk_index:04}",
                "text": chunk_text,
                "metadata": {
                    "title": document["title"],
                    "author": document["author"],
                    "category": document["category"],
                    "year": document["year"],
                    "language": document["language"],
                    "source_file": document["source_file"],
                    "chunk_index": chunk_index,
                    "word_count": len(chunk_text.split())
                }
            })

            chunk_index += 1

            # overlap
            overlap = current_chunk[-OVERLAP_PARAGRAPHS:] if OVERLAP_PARAGRAPHS > 0 else []

            current_chunk = overlap.copy()

            current_words = sum(len(p.split()) for p in current_chunk)

        current_chunk.append(paragraph)
        current_words += paragraph_word_count

    # Save last chunk
    if current_chunk:

        chunk_text = "\n\n".join(current_chunk)

        chunks.append({
            "chunk_id": f"{document['category']}_{Path(document['source_file']).stem}_{chunk_index:04}",
            "text": chunk_text,
            "metadata": {
                "title": document["title"],
                "author": document["author"],
                "category": document["category"],
                "year": document["year"],
                "language": document["language"],
                "source_file": document["source_file"],
                "chunk_index": chunk_index,
                "word_count": len(chunk_text.split())
            }
        })

    return chunks


# =====================================
# Process One File
# =====================================

def process_file(file_path: Path):

    document = load_document(file_path)

    chunks = create_chunks(document)

    category = document["category"]

    output_path = (
        OUTPUT_DIR /
        category /
        f"{Path(document['source_file']).stem}_chunks.json"
    )

    save_chunks(chunks, output_path)

    print(
        f"✓ {document['title']} -> {len(chunks)} chunks"
    )


# =====================================
# Main
# =====================================

def main():

    if not PROCESSED_DIR.exists():
        raise FileNotFoundError(PROCESSED_DIR)

    json_files = list(PROCESSED_DIR.rglob("*.json"))

    total_chunks = 0

    print(f"Found {len(json_files)} processed documents\n")

    for file in json_files:

        document = load_document(file)

        chunks = create_chunks(document)

        total_chunks += len(chunks)

        output_path = (
            OUTPUT_DIR /
            document["category"] /
            f"{Path(document['source_file']).stem}_chunks.json"
        )

        save_chunks(chunks, output_path)

        print(
            f"✓ {document['title']} -> {len(chunks)} chunks"
        )

    print("\n--------------------------------")
    print(f"Documents processed : {len(json_files)}")
    print(f"Total chunks created: {total_chunks}")
    print("--------------------------------")


if __name__ == "__main__":
    main()