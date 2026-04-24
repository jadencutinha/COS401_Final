from deep_translator import GoogleTranslator

SYSTEM_NAME = "google-translate"

def translate_to_spanish(text):
    """Translate English text to Spanish."""
    s = (text or "").strip()
    if not s:
        return ""
    return GoogleTranslator(source="en", target="es").translate(s)

def back_translate_to_english(spanish_text):
    """Translate Spanish text back to English."""
    s = (spanish_text or "").strip()
    if not s:
        return ""
    return GoogleTranslator(source="es", target="en").translate(s)