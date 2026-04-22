import pandas as pd
from transformers import pipeline

translator = pipeline("translation_en_to_es", model = "Helsinki-NLP/opus-mt-en-es")
df = pd.read_csv("data/sentences.csv")

def translate(text):
    return translator(text)[0]['translation_text']

df["translation"] = df["sentence"].apply(translate)
df.to_csv("results/outputs.csv", index=False)