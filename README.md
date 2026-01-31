# eCourts Bulk Search

A web application for bulk searching case information from the eCourts India portal. Upload an Excel file with party names, and the app will automatically search for cases and generate results.

## Project Structure

```
Authentication--1/
├── backend/          # FastAPI server + Selenium scraper
│   ├── main.py       # API endpoints
│   ├── bot.py        # eCourts search & captcha solver
│   └── .env          # API keys (create this)
├── frontend/         # React UI
└── README.md
```

---

## Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Google Chrome** (for Selenium automation)
- **2Captcha API key** ([get one here](https://2captcha.com))


```

```


## Running the Full Application

1. **Start the backend** (in one terminal):
   ```bash
   cd Authentication--1/backend
   venv\Scripts\activate   # Windows (or source venv/bin/activate on Mac/Linux)
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd Authentication--1/frontend
   npm install
   npm start
   ```

3. Open `http://localhost:3000` in your browser.

---

## How to Use

1. Prepare an Excel file (`.xlsx` or `.xls`) with a column named **"Name"**.
2. Add the party/case names you want to search in that column.
3. Upload the file using the web interface.
4. Wait for processing to complete (each name triggers a captcha solve + search).
5. Results are saved in `backend/results/results_YYYYMMDD_HHMMSS.xlsx`.

---

## API Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/bulk`  | Upload Excel file for bulk case search. Expects `file` in form data. |

---

## Troubleshooting

- **Chrome not found:** Ensure Google Chrome is installed. Selenium uses Chrome via `webdriver-manager`.
- **Captcha errors:** Verify your 2Captcha API key is correct and has sufficient balance.
- **CORS errors:** The backend allows all origins. If issues persist, ensure both servers are running.
- **Frontend can't reach backend:** Ensure the backend is running on port 8000 (the frontend expects `http://localhost:8000`).
