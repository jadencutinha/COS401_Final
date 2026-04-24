from analyze import analyze_results

import csv
import json

INPUT_FILE = "data/idioms.json"
OUTPUT_FILE = "data/results.csv"

# row shape: sourced fields, MT output, LLM judge output
RESULT_FIELDNAMES = [
    "id",
    "idiom",
    "meaning",
    "source_sentence",
    "literal_meaning",
    "expected_translation_note",
    "condition",
    "system",
    "translated_text",
    "back_translation",
    "meaning_preserved",
    "literal_translation",
    "confidence",
    "failure_type",
    "judge_explanation",
]


def main():
    with open(INPUT_FILE, "r") as f:
        idioms = json.load(f)
    results = []

    for item in idioms:
        pass

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    analyze_results(OUTPUT_FILE)

if __name__ == "__main__":
    main()