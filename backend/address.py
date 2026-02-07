def extract_state_city(address):
    address = address.lower()
    states = ["maharashtra", "delhi", "uttar pradesh"]
    state = None

    for s in states:
        if s in address:
            state = s.title()
            break

    parts = [p.strip() for p in address.split(",")]
    city = parts[-2].title() if len(parts) >= 2 else None

    return state, city