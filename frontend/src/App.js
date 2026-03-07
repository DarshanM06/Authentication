import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultFile, setResultFile] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResultFile("");
    setErrorMsg("");
  };

  const uploadFile = async () => {
    if (!file) {
      setErrorMsg("Please upload an Excel file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setErrorMsg("");
    setResultFile("");

    try {
      const res = await axios.post("http://localhost:8000/bulk", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResultFile(res.data.file);
    } catch (err) {
      setErrorMsg("An error occurred during verification. Please check the backend server.");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <div className="header-section">
        <h1 className="title">eCourts Verification</h1>
        <p className="subtitle">Automated background screening against India's eCourts portal</p>
      </div>

      <div className="main-card">

        {/* Custom File Uploader */}
        <div className="upload-container">
          <label htmlFor="file-upload" className="custom-file-upload">
            <span className="upload-icon">📄</span>
            <span className="upload-text">{file ? file.name : "Select Excel File (.xlsx)"}</span>
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".xlsx, .xls"
            onChange={handleFileChange}
            disabled={loading}
          />
        </div>

        {/* Error Message */}
        {errorMsg && <div className="error-box">{errorMsg}</div>}

        {/* Submit Button */}
        <button className={`submit-btn ${loading ? 'loading' : ''}`} onClick={uploadFile} disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span> Processing...
            </>
          ) : (
            "Upload & Search Records"
          )}
        </button>

        {/* Dynamic Results */}
        {resultFile && (
          <div className="success-box">
            <p>Verification Completed Successfully!</p>
            <a
              href={`http://localhost:8000/results/${resultFile}`}
              target="_blank"
              rel="noreferrer"
              className="download-btn"
            >
              Download Result Excel
            </a>
          </div>
        )}

        {/* Instructions Section */}
        <div className="instructions-section">
          <h3>How to use:</h3>
          <ol>
            <li>Prepare an Excel file (`.xlsx`) containing the candidates you want to verify.</li>
            <li>Your file <strong>must</strong> contain a column named <strong>Name</strong> (for the search) and a column named <strong>Address</strong> (must include the State and District to unlock the portal's search).</li>
            <li>You can optionally include a <strong>Father</strong> column to increase the accuracy of the final match.</li>
            <li>Upload the file above and click 'Search records'.</li>
            <li>The system will automatically extract locations, jumble names, and search the last 10 years of records.</li>
            <li>Once complete, a download link will appear for the annotated results.</li>
          </ol>
        </div>

      </div>

      <div className="footer">
        <p>Powered by FastAPI & Selenium</p>
      </div>
    </div>
  );
}

export default App;