import json
import re
from pathlib import Path
from tqdm import tqdm

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"

RAW_DATA = DATA_DIR / "raw"
PROCESSED_DATA = DATA_DIR / "processed"

PROCESSED_DATA.mkdir(
    parents=True,
    exist_ok=True
)
AUTHOR = "Friedrich Nietzsche"


# -----------------------------
# Metadata
# -----------------------------

BOOK_YEARS = {
    "Beyond_Good_and_Evil": 1886,
    "Thus_Spake_Zarathustra_A_Book_for_All_and_None": 1883,
    "The_Dawn_of_Day": 1881,
    "The_Birth_of_Tragedy": 1872,
    "Human,_All_Too_Human_A_Book_for_Free_Spirits": 1878,
    "The_Genealogy_of_Morals": 1887,
    "The_Joyful_Wisdom_(La_Gaya_Scienza)": 1882,
    "Ecce_Homo": 1888,
    "The_Antichrist": 1888,
    "The_Twilight_of_the_Idols;_or,_How_to_Philosophize_with_the_Hammer": 1888,
}


# -----------------------------
# Cleaning
# -----------------------------

def remove_gutenberg(text: str) -> str:
    """
    Removes Project Gutenberg header/footer.
    """

    start = re.search(r"\*\*\* START OF.*?\*\*\*", text, re.DOTALL)
    end = re.search(r"\*\*\* END OF.*?\*\*\*", text, re.DOTALL)

    if start:
        text = text[start.end():]

    if end:
        text = text[:end.start()]

    return text


def normalize_whitespace(text: str) -> str:

    text = text.replace("\r", "")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_page_numbers(text: str):

    lines = []

    for line in text.split("\n"):

        if re.fullmatch(r"\d+", line.strip()):
            continue

        lines.append(line)

    return "\n".join(lines)


def clean_text(text: str):

    text = remove_gutenberg(text)

    text = remove_page_numbers(text)

    text = normalize_whitespace(text)

    return text


# -----------------------------
# Metadata Extraction
# -----------------------------

def get_year(filename):

    stem = Path(filename).stem

    return BOOK_YEARS.get(stem)


def build_metadata(file_path: Path, category: str):

    return {
        "title": file_path.stem.replace("_", " "),
        "author": AUTHOR,
        "category": category,
        "year": get_year(file_path.name),
        "language": "English",
        "source_file": file_path.name,
    }


# -----------------------------
# Processing
# -----------------------------

def process_file(file_path: Path, category: str):

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    metadata = build_metadata(file_path, category)

    stats = {
    "characters": len(cleaned),
    "words": len(cleaned.split()),
    "paragraphs": len([p for p in cleaned.split("\n\n") if p.strip()])
    }

    document = {
        **metadata,
        "stats": stats,
        "text": cleaned,
    }

    output_dir = PROCESSED_DATA / category

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{file_path.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=4)


# -----------------------------
# Main
# -----------------------------

def main():

    if not RAW_DATA.exists():

        raise FileNotFoundError(RAW_DATA)

    categories = [d for d in RAW_DATA.iterdir() if d.is_dir()]

    total = 0

    for category in categories:

        files = list(category.glob("*.txt"))

        for file in tqdm(files, desc=category.name):

            process_file(file, category.name)

            total += 1

    print(f"\nProcessed {total} files successfully.")


if __name__ == "__main__":
    main()