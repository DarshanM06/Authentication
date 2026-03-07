# eCourts Search Portal Requirements

The LIVE portal requires the following specific sequence of actions and data points to perform a "Party Name" search.

## 1. Top-Level Mandatory Selections
Before the search tabs even unlock, the user MUST select:
- **State**: Selected from a dropdown.
- **District**: Selected from a dropdown (loads dynamically after State is selected).

*(Optional)*
- **Court Complex**: Can be selected to narrow down results, but is not mandatory.

## 2. 'Party Name' Tab Mandatory Fields
Once on the Party Name tab, the following fields are strictly required:

### Party Name Input
- Requires **minimum 3 characters**.
- Is partially matched by the server (e.g. searching "Ramesh" will return "Ramesh Narayan").
- Jumbling names is still required to account for completely reversed data entry (e.g., "Narayan Ramesh").

### Registration Year Input
- **CRITICAL BOTTLENECK**: This is a text input field, and it **ONLY accepts a single 4-digit year** (e.g., "2023"). 
- It does **not** accept year ranges (like 2015-2025). 
- To search 10 years deep, a bot MUST submit the entire form 10 separate times, solving 10 separate captchas per name variation.

### Case Status Radio Button
- Must select one: `Pending`, `Disposed`, or `Both`.
- `Both` is the recommended default for background checks.

### Captcha
- A 5-6 alphanumeric image captcha must be solved and entered for every single submission.

## Conclusion & Project Status
Our bot `bot.py` currently handles:
- State & District selection (Dynamically via `districts.py` and `address.py`)
- Party Name Jumbling (Handled via permutations generator)
- Case Status (Selects `Both` implicitly via defaults or clicks)
- Captcha Solving (Via 2Captcha API)

Our bot **intentionally skips** explicit year-by-year 10-year loops because the user approved bypassing it to save 10x 2Captcha API costs, relying instead on whatever default results the portal surfaces when Year is left blank. If Year *must* be filled to get any results at all for certain courts, we must implement the loop.
