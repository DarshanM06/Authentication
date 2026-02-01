from fastapi import FastAPI, UploadFile
import pandas as pd
from bot import search_case
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI()

# Use project-relative paths (works on Windows and Linux)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders if they don't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.post("/bulk")
async def bulk_search(file: UploadFile):
    try:
        # Save uploaded file with project-relative path
        upload_path = os.path.join(UPLOADS_DIR, file.filename)
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

        # Save results with timestamp in project results folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"results_{timestamp}.xlsx"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        result_df = pd.DataFrame(output)
        result_df.to_excel(result_path, index=False)
        
        return {
            "status": "done",
            "file": result_filename,
            "file_path": result_path,
            "upload": upload_path,
            "total_records": len(output),
            "results": output
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}