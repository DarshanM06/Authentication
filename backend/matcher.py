from rapidfuzz import fuzz

def is_match(text, name, father, address):
    score = 0
    total_weight = 0

    if name:
        score += fuzz.partial_ratio(name, text) * 0.40
        total_weight += 0.40
    
    if father:
        score += fuzz.partial_ratio(father, text) * 0.35
        total_weight += 0.35
        
    if address:
        score += fuzz.partial_ratio(address, text) * 0.25
        total_weight += 0.25
        
    if total_weight == 0:
        return False
        
    # Normalize score out of 100 based on provided fields
    normalized_score = score / total_weight
    return normalized_score >= 70