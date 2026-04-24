import csv

OUTPUT_DIR = "analysis/"

def analyze_results(results_file):
    with open(results_file, "r") as f:
        reader = csv.DictReader(f)
        results = list(reader)

    return results