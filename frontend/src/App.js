import { useState } from "react";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  const upload = async () => {
    if (!file) {
      setMessage("Please select a file first");
      setMessageType("error");
      return;
    }
    
    setLoading(true);
    setMessage("");
    try {
      const form = new FormData();
      form.append("file", file);
      
      const response = await fetch("http://localhost:8000/bulk", {
        method: "POST",
        body: form
      });
      
      if (response.ok) {
        setMessage("✓ Processing completed! Results saved to results.xlsx");
        setMessageType("success");
        setFile(null);
        document.getElementById("fileInput").value = "";
      } else {
        setMessage("✗ Upload failed. Please try again.");
        setMessageType("error");
      }
    } catch (error) {
      setMessage(`✗ Error: ${error.message}`);
      setMessageType("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h1>eCourts Bulk Search</h1>
          <p className="subtitle">Search case information in bulk</p>
        </div>

        <div className="content">
          <div className="upload-section">
            <label htmlFor="fileInput" className="file-label">
              <input
                id="fileInput"
                type="file"
                accept=".xlsx,.xls"
                onChange={e => setFile(e.target.files[0])}
                disabled={loading}
                className="file-input"
              />
              <span className="file-icon">📄</span>
              <span className="file-text">
                {file ? file.name : "Click to upload or drag and drop"}
              </span>
              <span className="file-subtext">
                Excel files (.xlsx, .xls) with a 'Name' column
              </span>
            </label>
          </div>

          {message && (
            <div className={`message message-${messageType}`}>
              {message}
            </div>
          )}

          <button 
            onClick={upload} 
            disabled={loading || !file}
            className="submit-btn"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <span>🚀</span>
                Upload & Start
              </>
            )}
          </button>

          <div className="instructions">
            <h3>How to use:</h3>
            <ol>
              <li>Prepare an Excel file with a column named "Name"</li>
              <li>Add the case/party names to search</li>
              <li>Upload the file using the button above</li>
              <li>Wait for processing to complete</li>
              <li>Check the results folder for results.xlsx</li>
            </ol>
          </div>
        </div>

        <div className="footer">
          <p>Powered by eCourts India | Secure & Reliable Case Search</p>
        </div>
      </div>
    </div>
  );
}