import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [analysisType, setAnalysisType] = useState("image");

  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(null);
  const [clearLoading, setClearLoading] = useState(false);

  const [error, setError] = useState("");
  const [selectedHistory, setSelectedHistory] = useState(null);

  const reportRef = useRef(null);

  // =========================================================
  // LOAD HISTORY
  // =========================================================

  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/history`);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load history."
        );
      }

      setHistory(
        Array.isArray(data.history)
          ? data.history
          : []
      );
    } catch (err) {
      setError(
        err.message || "Unable to load history."
      );
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // =========================================================
  // DASHBOARD CALCULATIONS
  // =========================================================

  const totalAnalyses = history.length;

  const lowRiskCount = history.filter(
    (item) =>
      item.verdict?.toUpperCase() === "LOW_RISK"
  ).length;

  const mediumRiskCount = history.filter(
    (item) =>
      item.verdict?.toUpperCase() === "MEDIUM_RISK"
  ).length;

  const highRiskCount = history.filter(
    (item) =>
      item.verdict?.toUpperCase() === "HIGH_RISK"
  ).length;

  const averageRiskScore =
    history.length > 0
      ? Math.round(
          history.reduce(
            (sum, item) =>
              sum + Number(item.risk_score || 0),
            0
          ) / history.length
        )
      : 0;

  const lowPercentage =
    totalAnalyses > 0
      ? Math.round(
          (lowRiskCount / totalAnalyses) * 100
        )
      : 0;

  const mediumPercentage =
    totalAnalyses > 0
      ? Math.round(
          (mediumRiskCount / totalAnalyses) * 100
        )
      : 0;

  const highPercentage =
    totalAnalyses > 0
      ? Math.round(
          (highRiskCount / totalAnalyses) * 100
        )
      : 0;

  const latestAnalysis =
    history.length > 0
      ? history[history.length - 1]
      : null;

  // =========================================================
  // ANALYZE IMAGE
  // =========================================================

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
      const response = await fetch(
        `${API_URL}/api/analyze/image`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Image analysis failed."
        );
      }

      setResult(data);

      await loadHistory();
    } catch (err) {
      setError(
        err.message || "Image analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ANALYZE VIDEO
  // =========================================================

  const analyzeVideo = async () => {
    if (!file) {
      setError("Please select a video first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/api/analyze/video`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Video analysis failed."
        );
      }

      setResult(data);

      await loadHistory();
    } catch (err) {
      setError(
        err.message || "Video analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ANALYZE AUDIO
  // =========================================================

  const analyzeAudio = async () => {
    if (!file) {
      setError("Please select an audio file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/api/analyze/audio`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Audio analysis failed."
        );
      }

      setResult(data);

      await loadHistory();
    } catch (err) {
      setError(
        err.message || "Audio analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ANALYZE MESSAGE
  // =========================================================

  const analyzeMessage = async () => {
    if (
      typeof file !== "string" ||
      !file.trim()
    ) {
      setError("Please enter a message first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);

    try {
      const response = await fetch(
        `${API_URL}/api/analyze/message`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: file.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Message analysis failed."
        );
      }

      setResult(data);

      await loadHistory();
    } catch (err) {
      setError(
        err.message || "Message analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // HANDLE ANALYSIS TYPE
  // =========================================================

  const handleAnalysisTypeChange = (type) => {
    setAnalysisType(type);

    setFile(null);
    setResult(null);
    setSelectedHistory(null);
    setError("");
  };

  // =========================================================
  // HANDLE FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0] || null;

    setFile(selectedFile);
    setResult(null);
    setSelectedHistory(null);
    setError("");
  };

  // =========================================================
  // OPEN HISTORY
  // =========================================================

  const openHistory = async (id) => {
    try {
      setError("");

      const response = await fetch(
        `${API_URL}/api/history/${id}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to load history record."
        );
      }

      setSelectedHistory(data.history);
      setResult(null);
    } catch (err) {
      setError(
        err.message ||
          "Unable to load history record."
      );
    }
  };

  // =========================================================
  // DELETE SINGLE HISTORY
  // =========================================================

  const deleteHistory = async (id) => {
    const item = history.find(
      (entry) => entry.id === id
    );

    const confirmed = window.confirm(
      `Delete "${
        item?.filename || "this record"
      }" from history?`
    );

    if (!confirmed) {
      return;
    }

    setDeleteLoading(id);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/history/${id}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to delete history record."
        );
      }

      if (selectedHistory?.id === id) {
        setSelectedHistory(null);
        setResult(null);
      }

      await loadHistory();
    } catch (err) {
      setError(
        err.message ||
          "Unable to delete history record."
      );
    } finally {
      setDeleteLoading(null);
    }
  };

  // =========================================================
  // CLEAR ALL HISTORY
  // =========================================================

  const clearHistory = async () => {
    if (history.length === 0) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete ALL analysis history?"
    );

    if (!confirmed) {
      return;
    }

    setClearLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/history`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to clear history."
        );
      }

      setHistory([]);
      setSelectedHistory(null);
      setResult(null);
    } catch (err) {
      setError(
        err.message ||
          "Unable to clear history."
      );
    } finally {
      setClearLoading(false);
    }
  };

  // =========================================================
  // ACTIVE REPORT
  // =========================================================

  const report = result?.report;

  const selectedReport =
    selectedHistory?.report;

  const activeReport =
    report || selectedReport;

  const isVideoReport =
    activeReport?.verification?.file_type ===
      "video" ||
    activeReport?.video_analysis;

  const isAudioReport =
    activeReport?.verification?.file_type ===
      "audio" ||
    activeReport?.audio_analysis;

  const isMessageReport =
    activeReport?.verification?.file_type ===
      "message" ||
    activeReport?.message_analysis;

  // =========================================================
  // IMAGE REPORT DATA
  // =========================================================

  const risk =
    activeReport?.risk_assessment;

  const ml =
    activeReport?.ml_analysis;

  const forensics =
    activeReport?.forensics;

  // =========================================================
  // VIDEO REPORT DATA
  // =========================================================

  const video =
    activeReport?.video_analysis;

  // =========================================================
  // AUDIO REPORT DATA
  // =========================================================

  const audio =
    activeReport?.audio_analysis;

  // =========================================================
  // MESSAGE REPORT DATA
  // =========================================================

  const message =
    activeReport?.message_analysis;

  // =========================================================
  // VERDICT
  // =========================================================

  const verdict =
    risk?.verdict ||
    message?.verdict ||
    (isVideoReport
      ? "VIDEO_ANALYSIS_COMPLETED"
      : isAudioReport
      ? "AUDIO_ANALYSIS_COMPLETED"
      : isMessageReport
      ? "MESSAGE_ANALYSIS_COMPLETED"
      : "UNKNOWN");

  const verdictClass =
    verdict.toLowerCase();

  const riskScore = Math.min(
    Math.max(
      Number(
        risk?.risk_score ??
          message?.risk_score ??
          0
      ),
      0
    ),
    100
  );

  // =========================================================
  // ELA HEATMAP URL
  // =========================================================

  const heatmapPath =
    forensics?.ela?.heatmap_path || "";

  const heatmapFileName =
    heatmapPath
      ? heatmapPath
          .split(/[/\\]/)
          .pop()
      : "";

  const heatmapUrl =
    heatmapFileName
      ? `${API_URL}/reports/ela/${encodeURIComponent(
          heatmapFileName
        )}`
      : "";

  // =========================================================
  // SHA-256 INTEGRITY
  // =========================================================

  const integrity =
    forensics?.integrity;

  // =========================================================
  // AUTO SCROLL TO RESULT
  // =========================================================

  useEffect(() => {
    if (
      activeReport &&
      reportRef.current
    ) {
      setTimeout(() => {
        reportRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 150);
    }
  }, [activeReport]);

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">

        <div>
          <h1>
            DeepVerify-X
          </h1>

          <p>
            AI-Generated Content Provenance
            &amp; Deepfake Verification
          </p>
        </div>

        <span className="status">
          ● API Connected
        </span>

      </header>

      <main className="container">

        {/* ================= DASHBOARD ================= */}

        <section className="dashboard">

          {/* TOTAL */}

          <div className="dashboard-card total-card">

            <div className="card-top">

              <span>
                Total Analyses
              </span>

              <span className="dashboard-icon">
                ◉
              </span>

            </div>

            <strong>
              {totalAnalyses}
            </strong>

            <small>
              Images, videos, audio &amp; messages analyzed
            </small>

          </div>

          {/* LOW RISK */}

          <div className="dashboard-card low-card">

            <div className="card-top">

              <span>
                Low Risk
              </span>

              <span className="dashboard-icon">
                ✓
              </span>

            </div>

            <strong>
              {lowRiskCount}
            </strong>

            <div className="mini-progress">

              <div
                style={{
                  width: `${lowPercentage}%`,
                }}
              />

            </div>

            <small>
              {lowPercentage}% of total analyses
            </small>

          </div>

          {/* MEDIUM RISK */}

          <div className="dashboard-card medium-card">

            <div className="card-top">

              <span>
                Medium Risk
              </span>

              <span className="dashboard-icon">
                !
              </span>

            </div>

            <strong>
              {mediumRiskCount}
            </strong>

            <div className="mini-progress">

              <div
                style={{
                  width: `${mediumPercentage}%`,
                }}
              />

            </div>

            <small>
              {mediumPercentage}% of total analyses
            </small>

          </div>

          {/* HIGH RISK */}

          <div className="dashboard-card high-card">

            <div className="card-top">

              <span>
                High Risk
              </span>

              <span className="dashboard-icon">
                ⚠
              </span>

            </div>

            <strong>
              {highRiskCount}
            </strong>

            <div className="mini-progress">

              <div
                style={{
                  width: `${highPercentage}%`,
                }}
              />

            </div>

            <small>
              {highPercentage}% of total analyses
            </small>

          </div>

          {/* AVERAGE RISK */}

          <div className="dashboard-card average-card">

            <div className="card-top">

              <span>
                Average Risk Score
              </span>

              <span className="dashboard-icon">
                ◈
              </span>

            </div>

            <strong>
              {averageRiskScore}
            </strong>

            <div className="score-mini-bar">

              <div
                style={{
                  width: `${averageRiskScore}%`,
                }}
              />

            </div>

            <small>
              Risk-scored analyses
            </small>

          </div>

          {/* LATEST ANALYSIS */}

          <div className="dashboard-card latest-card">

            <div className="card-top">

              <span>
                Latest Analysis
              </span>

              <span className="dashboard-icon">
                ●
              </span>

            </div>

            {latestAnalysis ? (
              <>

                <strong>
                  {latestAnalysis.risk_score ?? 0}
                </strong>

                <small className="latest-file">
                  {latestAnalysis.filename}
                </small>

                <span
                  className={`latest-verdict ${
                    latestAnalysis.verdict?.toLowerCase() ||
                    ""
                  }`}
                >
                  {latestAnalysis.verdict?.replace(
                    /_/g,
                    " "
                  )}
                </span>

              </>
            ) : (
              <>

                <strong>
                  0
                </strong>

                <small>
                  No analysis available
                </small>

              </>
            )}

          </div>

        </section>

        {/* ================= ANALYSIS TYPE ================= */}

        <section className="upload-section">

          <h2>
            Content Verification
          </h2>

          <p>
            Select an analysis type and upload
            your content for forensic verification.
          </p>

          {/* ================= TYPE BUTTONS ================= */}

          <div
            style={{
              display: "flex",
              gap: "12px",
              marginBottom: "20px",
              flexWrap: "wrap",
            }}
          >

            {/* IMAGE */}

            <button
              type="button"
              onClick={() =>
                handleAnalysisTypeChange("image")
              }
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                border:
                  analysisType === "image"
                    ? "2px solid #2563eb"
                    : "1px solid #cbd5e1",
                background:
                  analysisType === "image"
                    ? "#eff6ff"
                    : "#ffffff",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              🖼️ Image Verification
            </button>

            {/* VIDEO */}

            <button
              type="button"
              onClick={() =>
                handleAnalysisTypeChange("video")
              }
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                border:
                  analysisType === "video"
                    ? "2px solid #2563eb"
                    : "1px solid #cbd5e1",
                background:
                  analysisType === "video"
                    ? "#eff6ff"
                    : "#ffffff",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              🎥 Video Verification
            </button>

            {/* AUDIO */}

            <button
              type="button"
              onClick={() =>
                handleAnalysisTypeChange("audio")
              }
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                border:
                  analysisType === "audio"
                    ? "2px solid #2563eb"
                    : "1px solid #cbd5e1",
                background:
                  analysisType === "audio"
                    ? "#eff6ff"
                    : "#ffffff",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              🎧 Audio Verification
            </button>

            {/* MESSAGE */}

            <button
              type="button"
              onClick={() =>
                handleAnalysisTypeChange("message")
              }
              style={{
                padding: "10px 20px",
                borderRadius: "8px",
                border:
                  analysisType === "message"
                    ? "2px solid #2563eb"
                    : "1px solid #cbd5e1",
                background:
                  analysisType === "message"
                    ? "#eff6ff"
                    : "#ffffff",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              📝 Message Analysis
            </button>

          </div>

          {/* ================= UPLOAD BOX ================= */}

          <div className="upload-box">

            {analysisType === "message" ? (

              <>

                <textarea
                  placeholder="Enter the message you want to analyze..."
                  value={
                    typeof file === "string"
                      ? file
                      : ""
                  }
                  onChange={(event) => {
                    setFile(event.target.value);
                    setResult(null);
                    setSelectedHistory(null);
                    setError("");
                  }}
                  rows={7}
                  style={{
                    width: "100%",
                    padding: "12px",
                    borderRadius: "8px",
                    border: "1px solid #cbd5e1",
                    resize: "vertical",
                    fontFamily: "inherit",
                    fontSize: "15px",
                    boxSizing: "border-box",
                    marginBottom: "12px",
                  }}
                />

                <div
                  style={{
                    textAlign: "right",
                    marginBottom: "12px",
                    color: "#64748b",
                    fontSize: "13px",
                  }}
                >
                  {(
                    typeof file === "string"
                      ? file
                      : ""
                  ).length}{" "}
                  characters
                </div>

              </>

            ) : (

              <>

                <input
                  type="file"
                  accept={
                    analysisType === "image"
                      ? ".jpg,.jpeg,.png,.webp"
                      : analysisType === "video"
                      ? ".mp4,.avi,.mov,.mkv,.webm"
                      : ".wav,.mp3,.m4a,.aac,.flac,.ogg,.webm"
                  }
                  onChange={handleFileChange}
                />

                {file && (

                  <div className="file-name">

                    Selected:{" "}

                    <strong>
                      {file.name}
                    </strong>

                  </div>

                )}

              </>

            )}

            <button
              onClick={
                analysisType === "image"
                  ? analyzeImage
                  : analysisType === "video"
                  ? analyzeVideo
                  : analysisType === "audio"
                  ? analyzeAudio
                  : analyzeMessage
              }
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : analysisType === "image"
                ? "Analyze Image"
                : analysisType === "video"
                ? "Analyze Video"
                : analysisType === "audio"
                ? "Analyze Audio"
                : "Analyze Message"}
            </button>

          </div>

          {error && (

            <div className="error">
              {error}
            </div>

          )}

        </section>

        {/* ================= HISTORY ================= */}

        <section className="history-section">

          <div className="section-heading">

            <div>

              <h2>
                Analysis History
              </h2>

              <p>
                Previous image, video, audio and message
                verification reports
              </p>

            </div>

            <div className="history-actions">

              <button
                className="refresh-button"
                onClick={loadHistory}
                disabled={
                  historyLoading ||
                  clearLoading
                }
              >
                {historyLoading
                  ? "Loading..."
                  : "Refresh"}
              </button>

              <button
                className="clear-button"
                onClick={clearHistory}
                disabled={
                  history.length === 0 ||
                  clearLoading ||
                  historyLoading
                }
              >
                {clearLoading
                  ? "Clearing..."
                  : "Clear All"}
              </button>

            </div>

          </div>

          {history.length === 0 ? (

            <div className="empty-history">
              No analysis history available.
            </div>

          ) : (

            <div className="history-table">

              <div className="history-header">

                <span>
                  File
                </span>

                <span>
                  Type
                </span>

                <span>
                  Risk Score
                </span>

                <span>
                  Verdict
                </span>

                <span>
                  Date
                </span>

                <span>
                  Action
                </span>

              </div>

              {history.map((item) => {

                const itemVerdict =
                  item.verdict ||
                  "UNKNOWN";

                const isDeleting =
                  deleteLoading === item.id;

                return (

                  <div
                    className="history-row"
                    key={item.id}
                  >

                    <strong>
                      {item.filename}
                    </strong>

                    <span>
                      {item.file_type === "video"
                        ? "🎥 Video"
                        : item.file_type === "audio"
                        ? "🎧 Audio"
                        : item.file_type === "message"
                        ? "📝 Message"
                        : "🖼️ Image"}
                    </span>

                    <span>
                      {item.risk_score ?? "N/A"}
                    </span>

                    <span
                      className={`history-verdict ${
                        itemVerdict.toLowerCase()
                      }`}
                    >
                      {itemVerdict.replace(
                        /_/g,
                        " "
                      )}
                    </span>

                    <span>
                      {item.timestamp
                        ? new Date(
                            item.timestamp
                          ).toLocaleString()
                        : "N/A"}
                    </span>

                    <div className="history-buttons">

                      <button
                        className="view-button"
                        onClick={() =>
                          openHistory(item.id)
                        }
                        disabled={isDeleting}
                      >
                        View
                      </button>

                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteHistory(item.id)
                        }
                        disabled={isDeleting}
                      >
                        {isDeleting
                          ? "Deleting..."
                          : "Delete"}
                      </button>

                    </div>

                  </div>

                );
              })}

            </div>

          )}

        </section>

        {/* ================= RESULTS ================= */}

        {activeReport && (

          <section
            className="results"
            ref={reportRef}
          >

            {/* =================================================
                MESSAGE RESULT
            ================================================= */}

            {isMessageReport ? (

              <>

                <div className="results-heading">

                  <div>

                    <h2>
                      Message Analysis Result
                    </h2>

                    <p>
                      Text Message
                    </p>

                  </div>

                  <div
                    className={`verdict ${
                      message?.verdict?.toLowerCase() ||
                      ""
                    }`}
                  >
                    {(message?.verdict || "UNKNOWN").replace(
                      /_/g,
                      " "
                    )}
                  </div>

                </div>

                {/* ================= MESSAGE SCORE ================= */}

                <div className="score-card">

                  <span>
                    Message Risk Score
                  </span>

                  <strong>
                    {message?.risk_score ?? 0}
                  </strong>

                  <small>
                    out of 100
                  </small>

                  <div className="score-bar">

                    <div
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              message?.risk_score || 0
                            ),
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>

                {/* ================= MESSAGE DETAILS ================= */}

                <div className="grid">

                  <div className="card">

                    <span>
                      Word Count
                    </span>

                    <strong>
                      {message?.word_count ?? 0}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      Character Count
                    </span>

                    <strong>
                      {message?.character_count ?? 0}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      URLs Detected
                    </span>

                    <strong>
                      {message?.url_count ?? 0}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      Emails Detected
                    </span>

                    <strong>
                      {message?.email_count ?? 0}
                    </strong>

                  </div>

                </div>

                {/* ================= MESSAGE FORENSICS ================= */}

                <div className="analysis-grid">

                  <div className="panel">

                    <h3>
                      Message Indicators
                    </h3>

                    <div className="info-row">

                      <span>
                        Analysis Status
                      </span>

                      <strong>
                        {message?.analysis_status ||
                          "COMPLETED"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Phone Numbers
                      </span>

                      <strong>
                        {message?.phone_count ??
                          message?.["phone_ count"] ??
                          0}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Exclamation Marks
                      </span>

                      <strong>
                        {message?.exclamation_count ??
                          0}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Question Marks
                      </span>

                      <strong>
                        {message?.question_count ??
                          0}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Uppercase Ratio
                      </span>

                      <strong>
                        {message?.uppercase_ratio !==
                        undefined
                          ? `${(
                              Number(
                                message.uppercase_ratio
                              ) * 100
                            ).toFixed(1)}%`
                          : "N/A"}
                      </strong>

                    </div>

                  </div>

                  <div className="panel">

                    <h3>
                      Suspicious Keywords
                    </h3>

                    {message?.suspicious_keywords
                      ?.length ? (

                      message.suspicious_keywords.map(
                        (keyword, index) => (

                          <div
                            className="info-row"
                            key={index}
                          >

                            <span>
                              Keyword {index + 1}
                            </span>

                            <strong>
                              {keyword}
                            </strong>

                          </div>

                        )
                      )

                    ) : (

                      <div className="reason success">

                        <span>
                          ✓
                        </span>

                        No suspicious keyword
                        patterns detected.

                      </div>

                    )}

                  </div>

                </div>

                {/* ================= RISK ASSESSMENT ================= */}

                <div className="reasons">

                  <h3>
                    Risk Assessment
                  </h3>

                  {message?.reasons?.length ? (

                    message.reasons.map(
                      (reason, index) => (

                        <div
                          className="reason"
                          key={index}
                        >

                          <span>
                            !
                          </span>

                          {reason}

                        </div>

                      )
                    )

                  ) : (

                    <div className="reason success">

                      <span>
                        ✓
                      </span>

                      No significant suspicious
                      indicators detected.

                    </div>

                  )}

                  <p className="risk-disclaimer">

                    Note: Message Analysis performs
                    structural and suspicious-pattern
                    analysis. It is not a trained
                    AI-generated text detector.

                  </p>

                </div>

              </>

            ) : isAudioReport ? (

              /* =================================================
                 AUDIO RESULT
              ================================================= */

              <>

                <div className="results-heading">

                  <div>

                    <h2>
                      Audio Verification Result
                    </h2>

                    <p>
                      {activeReport
                        ?.verification
                        ?.filename ||
                        audio?.filename ||
                        "Unknown audio"}
                    </p>

                  </div>

                  <div className="verdict">
                    AUDIO ANALYSIS COMPLETED
                  </div>

                </div>

                {/* ================= AUDIO SUMMARY ================= */}

                <div className="score-card">

                  <span>
                    Audio Analysis Status
                  </span>

                  <strong
                    style={{
                      fontSize: "28px",
                    }}
                  >
                    {audio?.analysis_status ||
                      "COMPLETED"}
                  </strong>

                  <small>
                    Format:{" "}
                    {audio?.format ||
                      "UNKNOWN"}
                  </small>

                </div>

                {/* ================= AUDIO DETAILS ================= */}

                <div className="grid">

                  <div className="card">

                    <span>
                      Duration
                    </span>

                    <strong>
                      {audio?.duration_seconds !==
                      undefined
                        ? `${audio.duration_seconds} sec`
                        : "N/A"}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      Sample Rate
                    </span>

                    <strong>
                      {audio?.sample_rate !==
                      undefined
                        ? `${audio.sample_rate} Hz`
                        : "N/A"}
                    </strong>

                    <small>
                      {audio?.sample_rate_category ||
                        ""}
                    </small>

                  </div>

                  <div className="card">

                    <span>
                      Channels
                    </span>

                    <strong>
                      {audio?.channels ?? "N/A"}
                    </strong>

                    <small>
                      {audio?.channel_type ||
                        ""}
                    </small>

                  </div>

                  <div className="card">

                    <span>
                      Bitrate
                    </span>

                    <strong>
                      {audio?.bitrate_kbps !==
                      undefined
                        ? `${audio.bitrate_kbps} kbps`
                        : "N/A"}
                    </strong>

                  </div>

                </div>

                {/* ================= AUDIO FORENSICS ================= */}

                <div className="analysis-grid">

                  <div className="panel">

                    <h3>
                      Audio Information
                    </h3>

                    <div className="info-row">

                      <span>
                        Method
                      </span>

                      <strong>
                        {audio?.method ||
                          "Audio Forensic Analysis"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Format
                      </span>

                      <strong>
                        {audio?.format ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Duration
                      </span>

                      <strong>
                        {audio?.duration_seconds !==
                        undefined
                          ? `${audio.duration_seconds} sec`
                          : "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        File Size
                      </span>

                      <strong>
                        {audio?.file_size_bytes !==
                        undefined
                          ? `${audio.file_size_bytes.toLocaleString()} bytes`
                          : "N/A"}
                      </strong>

                    </div>

                  </div>

                  <div className="panel">

                    <h3>
                      Technical Properties
                    </h3>

                    <div className="info-row">

                      <span>
                        Sample Rate
                      </span>

                      <strong>
                        {audio?.sample_rate !==
                        undefined
                          ? `${audio.sample_rate} Hz`
                          : "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Sample Rate Category
                      </span>

                      <strong>
                        {audio?.sample_rate_category ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Channels
                      </span>

                      <strong>
                        {audio?.channels ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Channel Type
                      </span>

                      <strong>
                        {audio?.channel_type ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Bitrate
                      </span>

                      <strong>
                        {audio?.bitrate_kbps !==
                        undefined
                          ? `${audio.bitrate_kbps} kbps`
                          : "N/A"}
                      </strong>

                    </div>

                  </div>

                </div>

                {/* ================= AUDIO NOTE ================= */}

                <div className="reasons">

                  <h3>
                    Audio Analysis
                  </h3>

                  <div className="reason success">

                    <span>
                      ✓
                    </span>

                    Audio file was successfully
                    processed and its technical
                    properties were extracted.

                  </div>

                  <p className="risk-disclaimer">

                    Note: Current Audio Verification
                    performs technical and forensic
                    metadata analysis. It does not yet
                    provide a trained synthetic-voice or
                    AI-generated audio probability.

                  </p>

                </div>

              </>

            ) : isVideoReport ? (

              /* =================================================
                 VIDEO RESULT
              ================================================= */

              <>

                <div className="results-heading">

                  <div>

                    <h2>
                      Video Verification Result
                    </h2>

                    <p>
                      {activeReport
                        ?.verification
                        ?.filename ||
                        video?.filename ||
                        "Unknown video"}
                    </p>

                  </div>

                  <div className="verdict">
                    VIDEO ANALYSIS COMPLETED
                  </div>

                </div>

                {/* ================= VIDEO SUMMARY ================= */}

                <div className="score-card">

                  <span>
                    Video Analysis Status
                  </span>

                  <strong
                    style={{
                      fontSize: "28px",
                    }}
                  >
                    {video?.analysis_status ||
                      "COMPLETED"}
                  </strong>

                  <small>
                    Frame Status:{" "}
                    {video?.frame_status ||
                      "UNKNOWN"}
                  </small>

                </div>

                {/* ================= VIDEO DETAILS ================= */}

                <div className="grid">

                  <div className="card">

                    <span>
                      Duration
                    </span>

                    <strong>
                      {video?.duration_seconds !==
                      undefined
                        ? `${video.duration_seconds} sec`
                        : "N/A"}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      Frame Count
                    </span>

                    <strong>
                      {video?.frame_count ??
                        "N/A"}
                    </strong>

                  </div>

                  <div className="card">

                    <span>
                      FPS
                    </span>

                    <strong>
                      {video?.fps ?? "N/A"}
                    </strong>

                    <small>
                      {video?.fps_category ||
                        ""}
                    </small>

                  </div>

                  <div className="card">

                    <span>
                      Resolution
                    </span>

                    <strong>
                      {video?.resolution ||
                        "N/A"}
                    </strong>

                    <small>
                      {video
                        ?.resolution_category ||
                        ""}
                    </small>

                  </div>

                </div>

                {/* ================= FRAME ANALYSIS ================= */}

                <div className="analysis-grid">

                  <div className="panel">

                    <h3>
                      Frame Sampling
                    </h3>

                    <div className="info-row">

                      <span>
                        Sampled Frames
                      </span>

                      <strong>
                        {video?.sampled_frames ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Readable Frames
                      </span>

                      <strong>
                        {video?.readable_frames ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Frame Status
                      </span>

                      <strong>
                        {video?.frame_status ||
                          "N/A"}
                      </strong>

                    </div>

                  </div>

                  <div className="panel">

                    <h3>
                      Video Information
                    </h3>

                    <div className="info-row">

                      <span>
                        Format
                      </span>

                      <strong>
                        {video?.format
                          ? video.format.toUpperCase()
                          : "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Width
                      </span>

                      <strong>
                        {video?.width ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Height
                      </span>

                      <strong>
                        {video?.height ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        File Size
                      </span>

                      <strong>
                        {video?.file_size_bytes !==
                        undefined
                          ? `${video.file_size_bytes.toLocaleString()} bytes`
                          : "N/A"}
                      </strong>

                    </div>

                  </div>

                </div>

                {/* ================= VIDEO NOTE ================= */}

                <div className="reasons">

                  <h3>
                    Video Analysis
                  </h3>

                  <div className="reason success">

                    <span>
                      ✓
                    </span>

                    Video file was successfully
                    opened and sampled frames were
                    readable.

                  </div>

                  <p className="risk-disclaimer">

                    Note: Current Video Verification
                    performs structural and frame-level
                    forensic checks. It does not yet
                    provide a trained deepfake probability.

                  </p>

                </div>

              </>

            ) : (

              /* =================================================
                 IMAGE RESULT
              ================================================= */

              <>

                {/* RESULTS HEADING */}

                <div className="results-heading">

                  <div>

                    <h2>
                      Verification Result
                    </h2>

                    <p>
                      {activeReport
                        ?.verification
                        ?.filename ||
                        "Unknown file"}
                    </p>

                  </div>

                  <div
                    className={`verdict ${verdictClass}`}
                  >
                    {verdict.replace(
                      /_/g,
                      " "
                    )}
                  </div>

                </div>

                {/* ================= SCORE ================= */}

                <div className="score-card">

                  <span>
                    Overall Risk Score
                  </span>

                  <strong>
                    {riskScore}
                  </strong>

                  <small>
                    out of 100
                  </small>

                  <div className="score-bar">

                    <div
                      style={{
                        width: `${riskScore}%`,
                      }}
                    />

                  </div>

                </div>

                {/* ================= BASIC INFORMATION ================= */}

                <div className="grid">

                  {/* ML MODEL */}

                  <div className="card">

                    <span>
                      ML Model
                    </span>

                    <strong>
                      {ml?.model || "N/A"}
                    </strong>

                  </div>

                  {/* MODEL CONFIDENCE */}

                  <div className="card">

                    <span>
                      Model Confidence
                    </span>

                    <small>
                      Baseline ImageNet
                      classification confidence
                    </small>

                    <strong>
                      {ml?.confidence !==
                      undefined
                        ? `${(
                            ml.confidence *
                            100
                          ).toFixed(2)}%`
                        : "N/A"}
                    </strong>

                  </div>

                  {/* IMAGE FORMAT */}

                  <div className="card">

                    <span>
                      Image Format
                    </span>

                    <strong>
                      {forensics
                        ?.metadata
                        ?.format ||
                        "N/A"}
                    </strong>

                  </div>

                  {/* DIMENSIONS */}

                  <div className="card">

                    <span>
                      Dimensions
                    </span>

                    <strong>
                      {forensics
                        ?.metadata
                        ?.width ||
                        "-"}{" "}
                      ×{" "}
                      {forensics
                        ?.metadata
                        ?.height ||
                        "-"}
                    </strong>

                  </div>

                </div>

                {/* ================= FORENSIC ANALYSIS ================= */}

                <div className="analysis-grid">

                  {/* ================= METADATA ================= */}

                  <div className="panel">

                    <h3>
                      Metadata
                    </h3>

                    <div className="info-row">

                      <span>
                        Format
                      </span>

                      <strong>
                        {forensics
                          ?.metadata
                          ?.format ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        EXIF Available
                      </span>

                      <strong>
                        {forensics
                          ?.metadata
                          ?.has_exif
                          ? "Yes"
                          : "No"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Mode
                      </span>

                      <strong>
                        {forensics
                          ?.metadata
                          ?.mode ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Width
                      </span>

                      <strong>
                        {forensics
                          ?.metadata
                          ?.width ||
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Height
                      </span>

                      <strong>
                        {forensics
                          ?.metadata
                          ?.height ||
                          "N/A"}
                      </strong>

                    </div>

                  </div>

                  {/* ================= ELA ================= */}

                  <div className="panel">

                    <h3>
                      ELA Analysis
                    </h3>

                    <div className="info-row">

                      <span>
                        JPEG Quality
                      </span>

                      <strong>
                        {forensics
                          ?.ela
                          ?.jpeg_quality ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Mean Difference
                      </span>

                      <strong>
                        {forensics
                          ?.ela
                          ?.mean_difference ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Maximum Difference
                      </span>

                      <strong>
                        {forensics
                          ?.ela
                          ?.max_difference ??
                          "N/A"}
                      </strong>

                    </div>

                  </div>

                  {/* ================= NOISE ================= */}

                  <div className="panel">

                    <h3>
                      Noise Analysis
                    </h3>

                    <div className="info-row">

                      <span>
                        Mean Noise
                      </span>

                      <strong>
                        {forensics
                          ?.noise
                          ?.mean_noise ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Noise Std
                      </span>

                      <strong>
                        {forensics
                          ?.noise
                          ?.noise_std ??
                          "N/A"}
                      </strong>

                    </div>

                    <div className="info-row">

                      <span>
                        Maximum Noise
                      </span>

                      <strong>
                        {forensics
                          ?.noise
                          ?.max_noise ??
                          "N/A"}
                      </strong>

                    </div>

                  </div>

                </div>

                {/* ================= ELA HEATMAP ================= */}

                {heatmapUrl && (

                  <div className="panel ela-heatmap-panel">

                    <h3>
                      ELA Heatmap
                    </h3>

                    <p>
                      Error Level Analysis visualization
                      showing JPEG compression differences
                      across the image.
                    </p>

                    <div className="ela-heatmap-container">

                      <img
                        src={heatmapUrl}
                        alt="ELA Heatmap"
                        className="ela-heatmap"
                        onError={(event) => {
                          event.currentTarget.style.display =
                            "none";
                        }}
                      />

                    </div>

                    <small className="ela-note">

                      Brighter or highlighted regions
                      indicate areas with higher
                      error-level differences.

                      This visualization is a forensic
                      indicator and is not conclusive
                      proof of manipulation or AI
                      generation.

                    </small>

                  </div>

                )}

                {/* ================= SHA-256 INTEGRITY ================= */}

                {integrity && (

                  <div className="panel integrity-panel">

                    <h3>
                      File Integrity Verification
                    </h3>

                    <p className="integrity-description">

                      SHA-256 cryptographic hash used
                      to verify the integrity of the
                      uploaded file.

                    </p>

                    <div className="integrity-grid">

                      <div className="info-row">

                        <span>
                          Algorithm
                        </span>

                        <strong>
                          {integrity.algorithm ||
                            "SHA-256"}
                        </strong>

                      </div>

                      <div className="info-row">

                        <span>
                          Filename
                        </span>

                        <strong>
                          {integrity.filename ||
                            activeReport
                              ?.verification
                              ?.filename ||
                            "N/A"}
                        </strong>

                      </div>

                      <div className="info-row">

                        <span>
                          File Size
                        </span>

                        <strong>
                          {integrity
                            .file_size_bytes !==
                          undefined
                            ? `${integrity.file_size_bytes.toLocaleString()} bytes`
                            : "N/A"}
                        </strong>

                      </div>

                    </div>

                    <div className="hash-container">

                      <span className="hash-label">
                        SHA-256 Hash
                      </span>

                      <code className="sha256-hash">

                        {integrity.sha256 ||
                          "Hash unavailable"}

                      </code>

                    </div>

                    <small className="integrity-note">

                      The SHA-256 hash uniquely
                      represents the current file
                      contents. If the file is modified,
                      its hash will change.

                    </small>

                  </div>

                )}

                {/* ================= RISK ASSESSMENT ================= */}

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

                          <span>
                            !
                          </span>

                          {reason}

                        </div>

                      )
                    )

                  ) : (

                    <div className="reason success">

                      <span>
                        ✓
                      </span>

                      No significant risk
                      indicators detected.

                    </div>

                  )}

                  <p className="risk-disclaimer">

                    Note: Forensic indicators are
                    not conclusive proof of AI
                    generation or image
                    manipulation.

                  </p>

                </div>

              </>

            )}

          </section>

        )}

      </main>

    </div>
  );
}

export default App;