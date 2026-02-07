from rapidfuzz import fuzz

def is_match(text, name, father, address):
    score = 0
    score += fuzz.partial_ratio(name, text) * 0.35
    score += fuzz.partial_ratio(father, text) * 0.35
    score += fuzz.partial_ratio(address, text) * 0.30
    return score >= 70