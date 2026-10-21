import re
from typing import Tuple
 
# ── Keyword banks ──────────────────────────────────────────────────────────────
 
EMOTION_KEYWORDS = {
    "stress": [
        "stress", "stressed", "pressure", "overwhelm", "overwhelmed", "deadline",
        "too much", "can't cope", "cannot cope", "breaking point", "tense", "tension",
        "burden", "loads of work", "too many tasks", "suffocating", "swamped",
        "buried", "hectic", "chaotic", "exhausting", "drained", "losing it"
    ],
    "fatigue": [
        "tired", "exhausted", "fatigue", "sleepy", "no energy", "worn out",
        "burnt out", "burnout", "can't focus", "cannot focus", "drained", "empty",
        "sluggish", "lethargic", "numb", "foggy", "heavy", "weak", "done",
        "zoned out", "no motivation", "can't get up", "can't sleep"
    ],
    "anxiety": [
        "anxious", "anxiety", "panic", "panicking", "worried", "worry", "fear",
        "scared", "nervous", "uneasy", "restless", "heart racing", "can't breathe",
        "overthinking", "catastrophizing", "what if", "chest tight", "doom",
        "dread", "impending", "spiral", "racing thoughts", "trembling"
    ],
    "overthinking": [
        "overthinking", "over thinking", "can't stop thinking", "mind won't stop",
        "loop", "spiral", "ruminating", "rumination", "obsessing", "obsessed",
        "replaying", "going in circles", "stuck in head", "intrusive thoughts",
        "second guessing", "what if", "keep thinking about", "can't let go"
    ],
    "calm": [
        "calm", "relaxed", "peaceful", "fine", "okay", "ok", "good", "alright",
        "composed", "settled", "at ease", "serene", "tranquil", "content",
        "balanced", "centered", "grounded", "steady", "stable"
    ],
    "motivation": [
        "motivated", "excited", "inspired", "pumped", "ready", "determined",
        "focused", "energized", "enthusiastic", "driven", "ambitious", "goals",
        "let's go", "can do", "looking forward", "optimistic", "hopeful",
        "productive", "achieving", "progress", "winning"
    ],
    "sadness": [
        "sad", "unhappy", "depressed", "depression", "hopeless", "hopelessness",
        "lonely", "alone", "isolated", "miserable", "heartbroken", "crying",
        "tears", "grief", "loss", "empty inside", "worthless", "no point",
        "give up", "feel nothing", "broken"
    ],
}
 
BURNOUT_WEIGHTS = {
    "stress": 0.30,
    "fatigue": 0.25,
    "anxiety": 0.20,
    "overthinking": 0.15,
    "sadness": 0.10,
    "calm": -0.15,
    "motivation": -0.20,
    "neutral": 0.0,
}
 
def detect_emotion(text: str) -> Tuple[str, float]:
    """Returns (emotion_label, confidence 0-1)."""
    text_lower = text.lower()
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}
 
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                scores[emotion] += 1
 
    total = sum(scores.values())
    if total == 0:
        return "neutral", 0.5
 
    best = max(scores, key=scores.get)
    confidence = scores[best] / max(total, 1)
    confidence = min(confidence + 0.3, 1.0)
    return best, round(confidence, 2)
 
 
def compute_burnout_score(emotion_history: list) -> float:
    """
    emotion_history: list of dicts with 'emotion' key.
    Returns burnout percentage 0–100.
    """
    if not emotion_history:
        return 0.0
 
    total_weight = 0.0
    for entry in emotion_history:
        emotion = entry.get("emotion", "neutral")
        weight = BURNOUT_WEIGHTS.get(emotion, 0.0)
        total_weight += weight
 
    # Normalize: assume each entry can contribute max 0.30
    max_possible = len(emotion_history) * 0.30
    if max_possible == 0:
        return 0.0
 
    score = (total_weight / max_possible) * 100
    score = max(0.0, min(100.0, score))
    return round(score, 1)
 
 
EMOTION_EMOJIS = {
    "stress": "😰",
    "fatigue": "😴",
    "anxiety": "😟",
    "overthinking": "🌀",
    "calm": "😌",
    "motivation": "🚀",
    "sadness": "😢",
    "neutral": "😐",
}
 
EMOTION_COLORS = {
    "stress": "#FF6B6B",
    "fatigue": "#A78BFA",
    "anxiety": "#F59E0B",
    "overthinking": "#60A5FA",
    "calm": "#34D399",
    "motivation": "#F97316",
    "sadness": "#94A3B8",
    "neutral": "#CBD5E1",
}
 
def emotion_display(emotion: str) -> str:
    emoji = EMOTION_EMOJIS.get(emotion, "💭")
    return f"{emoji} {emotion.capitalize()}"
 