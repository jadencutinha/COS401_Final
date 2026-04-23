import pandas as pd 

def analyze_results(file_path):
    df = pd.read_csv(file_path)

    avg_preserved = df["meaning_preserved"].mean()
    avg_literal = df["literal_translation"].mean()

    print("\nOverall results: ")
    print(f"Meaning preserved (avg): {avg_preserved:.2f}")
    print(f"Literal translation rate: {avg_literal:.2f}")

    print("\nWorst cases: ")
    worst = df.sort_values("meaning_preserved").head(5)
    print(worst[["idiom", "translated", "back_translated"]])

    print("\nMost Literal Failures")
    literal = df.sort_values("literal_translation", ascending=False).head(5)
    print(literal[["idiom", "translated"]])