from openai import openai

client = OpenAI()

def translate_text(text, target_lan="es"):
    prompt = f"Translate the following sentence into {target_lang}:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0

    )

    return response.choices[0].message.content.strip()