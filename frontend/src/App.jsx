import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedHistory, setSelectedHistory] = useState(null);

  const reportRef = useRef(null);

  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/history`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load history.");
      }

      setHistory(Array.isArray(data.history) ? data.history : []);
    } catch (err) {
      setError(err.message || "Unable to load history.");
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const totalAnalyses = history.length;

  const lowRiskCount = history.filter(
    (item) => item.verdict === "LOW_RISK"
  ).length;

  const mediumRiskCount = history.filter(
    (item) => item.verdict === "MEDIUM_RISK"
  ).length;

  const highRiskCount = history.filter(
    (item) => item.verdict === "HIGH_RISK"
  ).length;

  const analyzeImage = async () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/analyze/image`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Image analysis failed.");
      }

      setResult(data);
      await loadHistory();
    } catch (err) {
      setError(err.message || "Image analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const openHistory = async (id) => {
    try {
      setError("");

      const response = await fetch(
        `${API_URL}/api/history/${id}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load history record."
        );
      }

      setSelectedHistory(data.history);
      setResult(null);
    } catch (err) {
      setError(
        err.message || "Unable to load history record."
      );
    }
  };

  useEffect(() => {
    if (selectedHistory && reportRef.current) {
      setTimeout(() => {
        reportRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    }
  }, [selectedHistory]);

  const report = result?.report;
  const selectedReport = selectedHistory?.report;
  const activeReport = report || selectedReport;

  const risk = activeReport?.risk_assessment;
  const ml = activeReport?.ml_analysis;
  const forensics = activeReport?.forensics;

  const verdictClass = risk?.verdict
    ? risk.verdict.toLowerCase()
    : "";

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>DeepVerify-X</h1>
          <p>
            AI-Generated Content Provenance & Deepfake Verification
          </p>
        </div>

        <span className="status">
          ● API Connected
        </span>
      </header>

      <main className="container">

        <section className="dashboard">
          <div className="dashboard-card">
            <span>Total Analyses</span>
            <strong>{totalAnalyses}</strong>
            <small>Images verified</small>
          </div>

          <div className="dashboard-card low-card">
            <span>Low Risk</span>
            <strong>{lowRiskCount}</strong>
            <small>Low risk results</small>
          </div>

          <div className="dashboard-card medium-card">
            <span>Medium Risk</span>
            <strong>{mediumRiskCount}</strong>
            <small>Medium risk results</small>
          </div>

          <div className="dashboard-card high-card">
            <span>High Risk</span>
            <strong>{highRiskCount}</strong>
            <small>High risk results</small>
          </div>
        </section>

        <section className="upload-section">
          <h2>Verify Your Image</h2>

          <p>
            Upload an image to analyze AI-generation signals,
            metadata and manipulation traces.
          </p>

          <div className="upload-box">
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.webp"
              onChange={(e) => {
                const selectedFile = e.target.files?.[0] || null;

                setFile(selectedFile);
                setResult(null);
                setSelectedHistory(null);
                setError("");
              }}
            />

            {file && (
              <div className="file-name">
                Selected: <strong>{file.name}</strong>
              </div>
            )}

            <button
              onClick={analyzeImage}
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Analyze Image"}
            </button>
          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </section>

        <section className="history-section">
          <div className="section-heading">
            <div>
              <h2>Analysis History</h2>
              <p>
                Previous image verification reports
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadHistory}
              disabled={historyLoading}
            >
              {historyLoading
                ? "Loading..."
                : "Refresh"}
            </button>
          </div>

          {history.length === 0 ? (
            <div className="empty-history">
              No analysis history available.
            </div>
          ) : (
            <div className="history-table">

              <div className="history-header">
                <span>Image</span>
                <span>Risk Score</span>
                <span>Verdict</span>
                <span>Date</span>
                <span>Action</span>
              </div>

              {history.map((item) => (
                <div
                  className="history-row"
                  key={item.id}
                >
                  <strong>
                    {item.filename}
                  </strong>

                  <span>
                    {item.risk_score}
                  </span>

                  <span
                    className={`history-verdict ${
                      item.verdict?.toLowerCase() || ""
                    }`}
                  >
                    {item.verdict
                      ?.replace("_", " ")
                      || "UNKNOWN"}
                  </span>

                  <span>
                    {item.timestamp
                      ? new Date(
                          item.timestamp
                        ).toLocaleString()
                      : "N/A"}
                  </span>

                  <button
                    className="view-button"
                    onClick={() =>
                      openHistory(item.id)
                    }
                  >
                    View
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {activeReport && (
          <section
            className="results"
            ref={reportRef}
          >
            <div className="results-heading">
              <div>
                <h2>
                  Verification Result
                </h2>

                <p>
                  {activeReport?.verification?.filename ||
                    "Unknown file"}
                </p>
              </div>

              <div
                className={`verdict ${verdictClass}`}
              >
                {risk?.verdict
                  ?.replace("_", " ")
                  || "UNKNOWN"}
              </div>
            </div>

            <div className="score-card">
              <span>
                Overall Risk Score
              </span>

              <strong>
                {risk?.risk_score ?? 0}
              </strong>

              <small>
                out of 100
              </small>

              <div className="score-bar">
                <div
                  style={{
                    width: `${Math.min(
                      Number(risk?.risk_score || 0),
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="grid">

              <div className="card">
                <span>ML Model</span>
                <strong>
                  {ml?.model || "N/A"}
                </strong>
              </div>

              <div className="card">
                <span>Confidence</span>

                <strong>
                  {ml?.confidence !== undefined
                    ? `${(
                        ml.confidence * 100
                      ).toFixed(2)}%`
                    : "N/A"}
                </strong>
              </div>

              <div className="card">
                <span>Image Format</span>

                <strong>
                  {forensics?.metadata?.format ||
                    "N/A"}
                </strong>
              </div>

              <div className="card">
                <span>Dimensions</span>

                <strong>
                  {forensics?.metadata?.width ||
                    "-"}{" "}
                  ×{" "}
                  {forensics?.metadata?.height ||
                    "-"}
                </strong>
              </div>
            </div>

            <div className="analysis-grid">

              <div className="panel">
                <h3>Metadata</h3>

                <div className="info-row">
                  <span>Format</span>
                  <strong>
                    {forensics?.metadata?.format ||
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>EXIF Available</span>
                  <strong>
                    {forensics?.metadata?.has_exif
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Mode</span>
                  <strong>
                    {forensics?.metadata?.mode ||
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Width</span>
                  <strong>
                    {forensics?.metadata?.width ||
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Height</span>
                  <strong>
                    {forensics?.metadata?.height ||
                      "N/A"}
                  </strong>
                </div>
              </div>

              <div className="panel">
                <h3>ELA Analysis</h3>

                <div className="info-row">
                  <span>JPEG Quality</span>
                  <strong>
                    {forensics?.ela?.jpeg_quality ??
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Mean Difference</span>
                  <strong>
                    {forensics?.ela?.mean_difference ??
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Maximum Difference</span>
                  <strong>
                    {forensics?.ela?.max_difference ??
                      "N/A"}
                  </strong>
                </div>
              </div>

              <div className="panel">
                <h3>Noise Analysis</h3>

                <div className="info-row">
                  <span>Mean Noise</span>
                  <strong>
                    {forensics?.noise?.mean_noise ??
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Noise Std</span>
                  <strong>
                    {forensics?.noise?.noise_std ??
                      "N/A"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Maximum Noise</span>
                  <strong>
                    {forensics?.noise?.max_noise ??
                      "N/A"}
                  </strong>
                </div>
              </div>
            </div>

            <div className="reasons">
              <h3>
                Risk Assessment
              </h3>

              {risk?.reasons?.length ? (
                risk.reasons.map(
                  (reason, index) => (
                    <div
                      className="reason"
                      key={index}
                    >
                      <span>!</span>
                      {reason}
                    </div>
                  )
                )
              ) : (
                <div className="reason success">
                  <span>✓</span>
                  No significant risk
                  indicators detected.
                </div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;