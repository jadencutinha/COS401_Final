import pandas
from openai import OpenAI 

client = OpenAI()

def evaluate(row)
    prompt = f"""
    Idiom: {row['idiom']}
    Meaning: {row['meaning']}
    Original sentence: {row['sentence']}
    Spanish translation: {row['translation']}

    Does the translation preserve the intended meaning?
    Answer with:
    - score: 0 (wrong), 1 (partial), 2 (correct)
    - explanation:
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        message=[{"role": "user", "content": prompt}]
    )
    return reponse.choices[0].message.content

df = pd.read_csv("results/outputs.csv")
df["evaluation"] = df.apply(evaluate, axis=1)
df.to_csv("results/outputs_scored.csv", index=False)