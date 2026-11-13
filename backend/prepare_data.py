
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

INPUT_FILE = DATA_DIR / "vedanta_passages.json"
OUTPUT_FILE = DATA_DIR / "prepared_passages.json"



def build_embedding_text(passage):
    """Combine useful fields into one text string for semantic search."""

    keywords = passage.get("keywords", [])

    if isinstance(keywords, list):
        keywords = ", ".join(str(word) for word in keywords)

    practical_situations = passage.get("practical_situations", [])

    if isinstance(practical_situations, list):
        practical_situations = ", ".join(
            str(item) for item in practical_situations
        )

    parts = [
        f"Topic: {passage.get('topic', '')}",
        f"Summary: {passage.get('source_summary', '')}",
        f"Core teaching: {passage.get('core_teaching', '')}",
        f"English explanation: {passage.get('english_explanation', '')}",
        f"Hindi explanation: {passage.get('hindi_explanation', '')}",
        f"Keywords: {keywords}",
        f"Practical situations: {practical_situations}",
    ]

    return "\n".join(
        part for part in parts
        if part.split(": ", 1)[-1].strip()
    )



def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        passages = json.load(file)

    prepared_passages = []

    for passage in passages:
        prepared = passage.copy()
        prepared["embedding_text"] = build_embedding_text(passage)
        prepared_passages.append(prepared)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            prepared_passages,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Prepared {len(prepared_passages)} passages.")
    print(f"Saved to: {OUTPUT_FILE}")

    # Preview the first passage
    if prepared_passages:
        first = prepared_passages[0]
        print("\nEmbedding text preview:")
        print(first["embedding_text"])


if __name__ == "__main__":
    main()
