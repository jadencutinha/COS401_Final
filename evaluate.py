from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FAILURE_TYPES = (
    "none",
    "literalized_idiom",
    "meaning_shift",
    "awkward_but_correct",
    "correct_equivalent_idiom",
    "context_insufficient",
    "ambiguous",
)

def _safe_bool(v, default = False):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"true", "yes", "y", "1"}:
            return True
        if s in {"false", "no", "n", "0"}:
            return False
    return default

def _safe_float(v, default = 0.0):
    try:
        x = float(v)
    except Exception:
        return default
    if x != x:  # NaN
        return default
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x

def evaluate_translation(
    *,
    idiom,
    meaning,
    source_sentence,
    translated_text,
    literal_meaning = "",
    expected_translation_note = "",
    back_translation = None,
    model = "gpt-4o-mini",
):
    try:
        bt = (back_translation or "").strip()
        user_payload = {
            "idiom": idiom,
            "intended_meaning": meaning,
            "source_sentence": source_sentence,
            "translated_spanish": translated_text,
            "literal_meaning": literal_meaning,
            "expected_translation_note": expected_translation_note,
            "back_translation": bt if bt else None,
            "allowed_failure_types": list(FAILURE_TYPES),
        }

        system = (
            """
            You evaluate whether an English idiom's intended meaning is preserved after translation to Spanish.
            Focus on meaning preservation, not word-for-word matching.
            Return ONLY valid JSON with these exact keys:
            {
                "meaning_preserved": boolean,
                "literal_translation": boolean,
                "confidence": number between 0 and 1,
                "failure_type": one of allowed_failure_types,
                "explanation": short string
            }
            Guidelines:
            - If the translation conveys the intended meaning (even via paraphrase or a different idiom), meaning_preserved=true.
            - If it reads like a literal rendering of the idiom (beans, bucket, sack, etc.) set literal_translation=true.
            - Use failure_type='none' when meaning_preserved=true.
            """
        )

        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        content = (res.choices[0].message.content or "").strip()
        parsed = json.loads(content) if content else {}

        meaning_preserved = _safe_bool(parsed.get("meaning_preserved"), default=False)
        literal_translation = _safe_bool(parsed.get("literal_translation"), default=False)
        confidence = _safe_float(parsed.get("confidence"), default=0.0)
        failure_type = str(parsed.get("failure_type") or "ambiguous").strip()
        if failure_type not in FAILURE_TYPES:
            failure_type = "ambiguous"
        explanation = str(parsed.get("explanation") or "").strip()
        if not explanation:
            explanation = "No explanation provided."

        # keep invariants consistent for later analysis
        if meaning_preserved and failure_type != "none":
            failure_type = "none"
        if not meaning_preserved and failure_type == "none":
            failure_type = "ambiguous"

        return {
            "meaning_preserved": meaning_preserved,
            "literal_translation": literal_translation,
            "confidence": confidence,
            "failure_type": failure_type,
            "judge_explanation": explanation,
        }
    except Exception as e:
        return {
            "meaning_preserved": False,
            "literal_translation": False,
            "confidence": 0.0,
            "failure_type": "ambiguous",
            "judge_explanation": f"evaluation error: {e}",
        }