"""Shared Unicode/text helpers. Everything here is deterministic and pure."""

from __future__ import annotations

import unicodedata

# Arabic-script letter blocks (letters only; digits/punct handled separately).
_ARABIC_BLOCKS = (
    (0x0600, 0x06FF),
    (0x0750, 0x077F),
    (0x08A0, 0x08FF),
    (0xFB50, 0xFDFF),
    (0xFE70, 0xFEFF),
)

# Eastern Arabic-Indic digits (U+0660-0669) and Extended (Persian) U+06F0-06F9.
_DIGIT_FOLD = {}
for i in range(10):
    _DIGIT_FOLD[chr(0x0660 + i)] = str(i)
    _DIGIT_FOLD[chr(0x06F0 + i)] = str(i)

# Arabic orthographic folding (used only when a task opts in).
_ARABIC_FOLD = {
    "أ": "ا",  # alef hamza above -> alef
    "إ": "ا",  # alef hamza below -> alef
    "آ": "ا",  # alef madda -> alef
    "ٱ": "ا",  # alef wasla -> alef
    "ى": "ي",  # alef maksura -> yeh
    "ة": "ه",  # teh marbuta -> heh
    "ؤ": "و",  # waw hamza -> waw
    "ئ": "ي",  # yeh hamza -> yeh
}

_TASHKEEL = set(
    [chr(c) for c in range(0x064B, 0x0660)]  # fathatan..sukun etc.
    + ["ٰ"]  # superscript alef
)
_TATWEEL = "ـ"


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def strip_format_chars(s: str) -> str:
    """Remove Unicode Cf chars (RLM/LRM, directional embeddings, ZWJ...)."""
    return "".join(ch for ch in s if unicodedata.category(ch) != "Cf")


def is_arabic_letter(ch: str) -> bool:
    if not ch.isalpha():
        return False
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _ARABIC_BLOCKS)


def is_latin_letter(ch: str) -> bool:
    return ch.isalpha() and "LATIN" in unicodedata.name(ch, "")


def fold_digits(s: str) -> str:
    return "".join(_DIGIT_FOLD.get(ch, ch) for ch in s)


def normalize_arabic(s: str) -> str:
    """Opt-in orthographic normalization: tashkeel/tatweel stripped, alef/yeh/teh
    marbuta/hamza-carrier variants folded, Arabic-Indic digits folded to ASCII."""
    out = []
    for ch in s:
        if ch in _TASHKEEL or ch == _TATWEEL:
            continue
        ch = _ARABIC_FOLD.get(ch, ch)
        ch = _DIGIT_FOLD.get(ch, ch)
        out.append(ch)
    return "".join(out)


def remove_tokens(text: str, tokens) -> str:
    for tok in sorted(tokens or (), key=len, reverse=True):
        if tok:
            text = text.replace(tok, " ")
    return text


def script_ratios(text: str, allowed_tokens=()) -> dict:
    """Letter-based script composition of `text`, ignoring `allowed_tokens`
    occurrences, digits (any script), punctuation, and invisible format chars."""
    text = strip_format_chars(remove_tokens(text, allowed_tokens))
    total = arabic = latin = 0
    for ch in text:
        if not ch.isalpha():
            continue
        total += 1
        if is_arabic_letter(ch):
            arabic += 1
        elif is_latin_letter(ch):
            latin += 1
    return {
        "letters": total,
        "arabic_ratio": (arabic / total) if total else 0.0,
        "latin_ratio": (latin / total) if total else 0.0,
    }
