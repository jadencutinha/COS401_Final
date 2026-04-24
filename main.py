from translate import translate_text
from backtranslate import back_translate
from evaluate import evaluate_translation
from analyze import analyze_resilts
import json
import csv
import argparse

INPUT_FILE = "data/idioms.json"
OUTPUT_FILE = "data/results.csv"

def run_pipeline():
    with open(INPUT_FILE, "r") as f:
        idioms = json.load(f)
    results = []

    for item in idioms:
        source = item["source_sentence"]

        translated = translate_text(source, target_lang="es")
        back_translated = back_translate(translated, source_lang="es")

        evaluation = evaluate_translation(
            original = source,
            idiom = item["idiom"],
            meaning = item["meaning"],
            translated = translated,
            back_translated = back_translated,
            note=item["expected_translation_note"]
        )

        results.append({
            "idiom": item["idiom"],
            "original": source,
            "translated": translated,
            "back_translated": back_translated,
            **evaluation
        })

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    analyze_results(OUTPUT_FILE)

if __name__ == "__main__":
    run_pipeline()