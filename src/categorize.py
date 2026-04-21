# can later replace with another LLM classifier if we need to
def categorize(eval, text):
    eval_text = eval_text.lower()

    if "0" in eval_text:
        return "meaning lost"
    elif "1" in eval_text:
        return "partial"
    elif "2" in eval_text:
        return "correct"
    else:
        return "unknown"