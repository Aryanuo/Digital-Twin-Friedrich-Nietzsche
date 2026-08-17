from dataclasses import dataclass

@dataclass
class DocumentChunk:
    text: str
    source: str
    title: str
    category: str
    year: int | None
    chapter: str | None
    section: str | None