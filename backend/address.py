from districts import STATES_DISTRICTS

def extract_state_city(address):
    address = address.lower()
    state = None

    for s in STATES_DISTRICTS.keys():
        if s.lower() in address:
            state = s
            break

    parts = [p.strip() for p in address.split(",")]
    city = parts[-2].title() if len(parts) >= 2 else None

    return state, city