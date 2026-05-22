import os
import random

_keys_raw = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
GEMINI_KEYS = [k.strip() for k in _keys_raw.split(",") if k.strip()]

_o_keys_raw = os.getenv("OPENAI_API_KEYS", os.getenv("OPENAI_API_KEY", ""))
OPENAI_KEYS = [k.strip() for k in _o_keys_raw.split(",") if k.strip()]

def get_gemini_key():
    if not GEMINI_KEYS:
        return None
    return random.choice(GEMINI_KEYS)

def get_openai_key():
    if not OPENAI_KEYS:
        return None
    return random.choice(OPENAI_KEYS)
