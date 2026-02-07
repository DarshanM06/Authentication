from fastapi import FastAPI, UploadFile
import pandas as pd
from bot import verify_person
import os

app = FastAPI()
os.makedirs("results", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

@app.post("/bulk")
async def verify(file: UploadFile):
    df = pd.read_excel(file.file)
    output = []

    for _, row in df.iterrows():
        candidate = {
            "Name": row["Name"],
            "Father": row["Father"],
            "Address": row["Address"],
            "DOB": str(row["DOB"])
        }
        result = verify_person(candidate)
        output.append(result)

    out_file = "verification_results.xlsx"
    out_path = f"results/{out_file}"
    pd.DataFrame(output).to_excel(out_path, index=False)
    return {"file": out_file}