from fastapi import FastAPI, UploadFile
import pandas as pd
from bot import search_case
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

@app.post("/bulk")
async def bulk_search(file: UploadFile):
    try:
        # Save uploaded file
        upload_path = f"uploads/{file.filename}"
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read the uploaded file
        df = pd.read_excel(upload_path)
        output = []

        for _, row in df.iterrows():
            name = row["Name"]
            cases = search_case(name)
            output.append({
                "Name": name,
                "Cases": " | ".join(cases) if cases else "No cases found"
            })

        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"results/results_{timestamp}.xlsx"
        result_df = pd.DataFrame(output)
        result_df.to_excel(result_filename, index=False)
        
        return {
            "status": "done",
            "file": result_filename,
            "upload": upload_path,
            "total_records": len(output)
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}