import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultFile, setResultFile] = useState("");

  const uploadFile = async () => {
    if (!file) return alert("Upload Excel file");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/bulk", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResultFile(res.data.file);
      alert("Search completed!");
    } catch (err) {
      alert("Error occurred");
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <h1>eCourts Background Check</h1>

      <div className="card">
        <input
          type="file"
          accept=".xlsx"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={uploadFile} disabled={loading}>
          {loading ? "Searching..." : "Upload & Search"}
        </button>

        {resultFile && (
          <a
            href={`http://localhost:8000/results/${resultFile}`}
            target="_blank"
            rel="noreferrer"
            className="download"
          >
            Download Results
          </a>
        )}
      </div>
    </div>
  );
}

export default App;