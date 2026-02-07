from fastapi import FastAPI, UploadFile
import pandas as pd
from bot import search_candidate
import os
from datetime import datetime
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# app.mount("/results", StaticFiles(directory="results"), name="results")

UPLOADS="uploads"
RESULTS="results"
os.makedirs(UPLOADS,exist_ok=True)
os.makedirs(RESULTS,exist_ok=True)

@app.post("/bulk")
async def bulk(file: UploadFile):
    path=f"{UPLOADS}/{file.filename}"
    with open(path,"wb") as f:
        f.write(await file.read())

    df=pd.read_excel(path)
    output=[]

    for _,row in df.iterrows():
        candidate={
            "Name":row["Name"],
            "Father":row["Father"],
            "City":row["City"],
            "State":row["State"]
        }
        cases=search_candidate(candidate)
        if cases:
            for c in cases:
                output.append({
                    "Name":candidate["Name"],
                    "State":c["state"],
                    "District":c["district"],
                    "Details":c["raw"]
                })
        else:
            output.append({
                "Name":candidate["Name"],
                "State":candidate["State"],
                "District":"",
                "Details":"No case found"
            })

    out_file=f"results_{datetime.now().strftime('%H%M%S')}.xlsx"
    out_path=f"{RESULTS}/{out_file}"
    pd.DataFrame(output).to_excel(out_path,index=False)
    return {"file":out_file}