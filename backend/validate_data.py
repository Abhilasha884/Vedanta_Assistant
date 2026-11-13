import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "vedanta_passages.json"

REQUIRED_FIELDS = [
    "passage_id",
    "topic",
    "source_text",
    "source_summary",
    "english_explanation",
    "hindi_explanation",
    "keywords",
    "original_work",
    "source_book",
    "source_reference",
    "start_book_page",
    "end_book_page",
    "pdf_page",
]

def main():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            passages = json.load(file)
    except json.JSONDecodeError as error:
        print(f"Invalid JSON: {error}")
        return
    except FileNotFoundError:
        print(f"File not found: {DATA_FILE}")
        return

    if not isinstance(passages, list):
        print("Error: The JSON root must be a list.")
        return

    print(f"Loaded {len(passages)} passages.")

    seen_ids = set()
    issues = []

    for index, passage in enumerate(passages, start=1):
        if not isinstance(passage, dict):
            issues.append(f"Record {index}: expected a JSON object.")
            continue

        passage_id = passage.get("passage_id", f"Record {index}")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in passage:
                issues.append(f"{passage_id}: missing field '{field}'.")

        # Check duplicate IDs
        if passage_id in seen_ids:
            issues.append(f"{passage_id}: duplicate passage ID.")
        seen_ids.add(passage_id)

        
        for field in [
            "source_text",
            "source_summary",
            "english_explanation",
            "hindi_explanation",
        ]:
            if not passage.get(field):
                issues.append(f"{passage_id}: empty field '{field}'.")

       
        if not isinstance(passage.get("keywords"), list):
            issues.append(f"{passage_id}: keywords must be a list.")

      
        start_page = passage.get("start_book_page")
        end_page = passage.get("end_book_page")
        pdf_page = passage.get("pdf_page")

        if not all(isinstance(p, int) for p in [start_page, end_page, pdf_page]):
            issues.append(f"{passage_id}: page numbers must be integers.")
        elif start_page > end_page:
            issues.append(f"{passage_id}: start page is after end page.")

    print("\nValidation results:")
    if issues:
        for issue in issues:
            print(f"- {issue}")
        print(f"\nFound {len(issues)} issue(s).")
    else:
        print("All structural checks passed.")

if __name__ == "__main__":
    main()
