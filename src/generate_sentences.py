import pandas as pd 

def generate_sentence(idiom):
    templates = [
        # Rough / change later
        f"After weeks of silence, she finally {idiom}.",
        f"He didn't want to {idiom} during the meeting.",
        f"Everyone was waiting for him to {idiom}.",
    ]
    return templates[0] # simple for now / change later

df = pd.read_csv("data/idioms.csv")
df["sentence"] = df["idiom"].apply(generate_sequence)
df.to_csv("data/sentences.csv", index = False)
