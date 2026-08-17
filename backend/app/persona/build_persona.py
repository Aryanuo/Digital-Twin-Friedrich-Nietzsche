from pathlib import Path

PERSONA_DIR = Path(__file__).parent

FILES = [
    "identity.txt",
    "philosophy.txt",
    "speaking_style.txt",
    "dialogue_rules.txt",
    "emotional_guidance.txt",
    "modern_topics.txt",
]

OUTPUT = PERSONA_DIR / "system_prompt.txt"


def build_persona():

    sections = []

    for filename in FILES:

        file_path = PERSONA_DIR / filename

        if not file_path.exists():
            print(f"[WARNING] Missing: {filename}")
            continue

        print(f"Loading {filename}")

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        sections.append(text)

    final_prompt = "\n\n" + ("=" * 100) + "\n\n"

    final_prompt = final_prompt.join(sections)

    OUTPUT.write_text(
        final_prompt,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("Persona successfully built!")
    print(f"Saved to:\n{OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    build_persona()