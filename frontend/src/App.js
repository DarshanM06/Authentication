import { useState } from "react";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [results, setResults] = useState(null);
  const [filePath, setFilePath] = useState("");

  const upload = async () => {
    if (!file) {
      setMessage("Please select a file first");
      setMessageType("error");
      return;
    }
    
    setLoading(true);
    setMessage("");
    setResults(null);
    setFilePath("");
    try {
      const form = new FormData();
      form.append("file", file);
      
      const response = await fetch("http://localhost:8000/bulk", {
        method: "POST",
        body: form
      });
      
      const data = await response.json().catch(() => ({}));
      
      if (response.ok && data.status === "done") {
        setMessage(`✓ Processing completed! ${data.total_records} records processed.`);
        setMessageType("success");
        setFilePath(data.file_path || data.file || "");
        setResults(data.results || []);
        setFile(null);
        const fileInput = document.getElementById("fileInput");
        if (fileInput) fileInput.value = "";
      } else {
        setMessage(data.message || "✗ Upload failed. Please try again.");
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

          {filePath && (
            <div className="message message-success file-location">
              <strong>Result file saved to:</strong><br />
              <code>{filePath}</code>
            </div>
          )}

          {results && results.length > 0 && (
            <div className="results-section">
              <h3>Results Preview</h3>
              <div className="results-table-wrapper">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Cases</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, idx) => (
                      <tr key={idx}>
                        <td className="name-cell">{row.Name}</td>
                        <td className="cases-cell">
                          {row.Cases || "No cases found"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
              <li>Results are saved in the <strong>results</strong> folder with timestamp</li>
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