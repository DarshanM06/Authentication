from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
from bot import verify_person
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("results", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/results", StaticFiles(directory="results"), name="results")

@app.post("/bulk")
async def verify(file: UploadFile):
    df = pd.read_excel(file.file)
    
    # Normalize columns to handle case sensitivity and spaces
    # Example: "Name", "NAME", " Name " -> "name"
    original_cols = df.columns.tolist()
    norm_cols = {col: str(col).strip().lower().replace(" ", "_") for col in original_cols}
    df.rename(columns=norm_cols, inplace=True)
    
    # Find dynamically matching columns
    def get_col(options):
        for opt in options:
            if opt in df.columns:
                return opt
        return None

    name_col = get_col(['name', 'party_name', 'client_name', 'full_name'])
    fname_col = get_col(['father', 'father_name', 'fathers_name'])
    addr_col = get_col(['address', 'location', 'city', 'state'])
    dob_col = get_col(['dob', 'date_of_birth', 'birth'])

    if not name_col:
        return {"error": "Excel file must contain a 'Name' column (case-insensitive)"}

    output = []

    for _, row in df.iterrows():
        # Build candidate with fallback empty strings
        candidate = {
            "Name": str(row[name_col]) if pd.notna(row[name_col]) else "",
            "Father": str(row[fname_col]) if fname_col and pd.notna(row[fname_col]) else "",
            "Address": str(row[addr_col]) if addr_col and pd.notna(row[addr_col]) else "",
            "DOB": str(row[dob_col]) if dob_col and pd.notna(row[dob_col]) else ""
        }
        
        # Skip empty rows
        if not candidate["Name"]:
            continue
            
        result = verify_person(candidate)
        output.append(result)

    out_file = "verification_results.xlsx"
    out_path = f"results/{out_file}"
    pd.DataFrame(output).to_excel(out_path, index=False)
    return {"file": out_file}