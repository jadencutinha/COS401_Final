from analyze import analyze_results

import csv
import json

from evaluate import evaluate_translation
from translate import back_translate_to_english, translate_to_spanish, SYSTEM_NAME as TRANSLATION_SYSTEM_NAME

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

# toggles/controls
RUN_ISOLATED = True  # also translate the bare idiom (in addition to w/ context)
RUN_BACK_TRANSLATION = False # translate the MT output back to English
MAX_ITEMS = None # can set to an int for faster test runs

def _base_row(item, *, row_id, condition, source_sentence):
    return {
        "id": row_id,
        "idiom": item.get("idiom", ""),
        "meaning": item.get("meaning", ""),
        "source_sentence": source_sentence,
        "literal_meaning": item.get("literal_meaning", ""),
        "expected_translation_note": item.get("expected_translation_note", ""),
        "condition": condition,
        "system": TRANSLATION_SYSTEM_NAME,
        "translated_text": "",
        "back_translation": "",
        "meaning_preserved": "",
        "literal_translation": "",
        "confidence": "",
        "failure_type": "",
        "judge_explanation": "",
    }

def _safe_translate(row):
    try:
        row["translated_text"] = translate_to_spanish(row["source_sentence"])
    except Exception as e:
        # fill judge fields with a consistent fallback so analysis portion doesn't crash
        row["translated_text"] = ""
        row["judge_explanation"] = f"translation error: {e}"
        row["failure_type"] = "ambiguous"
        row["confidence"] = 0.0
        row["meaning_preserved"] = False
        row["literal_translation"] = False

def main():
    with open(INPUT_FILE, "r") as f:
        idioms = json.load(f)
    results = []

    if MAX_ITEMS is not None:
        idioms = idioms[: int(MAX_ITEMS)]

    row_id = 1
    for idx, item in enumerate(idioms, start=1):
        context_sentence = item.get("source_sentence", "") or ""
        rows_to_run = [
            _base_row(item, row_id=row_id, condition="context", source_sentence=context_sentence)
        ]
        row_id += 1

        if RUN_ISOLATED:
            isolated_sentence = item.get("idiom", "") or ""
            rows_to_run.append(
                _base_row(
                    item,
                    row_id=row_id,
                    condition="isolated",
                    source_sentence=isolated_sentence,
                )
            )
            row_id += 1

        for row in rows_to_run:
            print(f"[{idx}/{len(idioms)}] {row['condition']} | {row['idiom']} -> translating...")
            _safe_translate(row)

            if row["translated_text"] and RUN_BACK_TRANSLATION:
                try:
                    row["back_translation"] = back_translate_to_english(row["translated_text"])
                except Exception:
                    row["back_translation"] = ""

            print(f"[{idx}/{len(idioms)}] {row['condition']} | {row['idiom']} -> judging...")
            judge = evaluate_translation(
                idiom=row["idiom"],
                meaning=row["meaning"],
                source_sentence=row["source_sentence"],
                translated_text=row["translated_text"],
                literal_meaning=row["literal_meaning"],
                expected_translation_note=row["expected_translation_note"],
                back_translation=row["back_translation"] or None,
            )
            row.update(judge)
            results.append(row)

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    analyze_results(OUTPUT_FILE)

if __name__ == "__main__":
    main()