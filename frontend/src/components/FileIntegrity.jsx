import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function FileIntegrity({ onAnalysisComplete }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0] || null;

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const analyzeFileIntegrity = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/api/file-integrity/verify`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "File integrity analysis failed."
        );
      }

      setResult(data);

      if (onAnalysisComplete) {
        await onAnalysisComplete();
      }
    } catch (err) {
      setError(
        err.message || "File integrity analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const integrity =
    result?.file_integrity ||
    result?.report?.file_integrity ||
    result?.report ||
    result ||
    {};

  const filename =
    integrity.filename ||
    file?.name ||
    "Unknown file";

  const fileType =
    integrity.file_type ||
    file?.type ||
    "Unknown";

  const fileSize =
    integrity.file_size_bytes ??
    file?.size ??
    0;

  const algorithm =
    integrity.algorithm ||
    "SHA-256";

  const status =
    integrity.integrity_status ||
    integrity.status ||
    "HASH_GENERATED";

  const sha256 =
    integrity.sha256 ||
    integrity.hash ||
    "";

  const historyId =
    result?.history_id ??
    result?.history?.id ??
    integrity.history_id ??
    result?.id ??
    null;

  const formatBytes = (bytes) => {
    if (!bytes) {
      return "0 bytes";
    }

    if (bytes < 1024) {
      return `${bytes} bytes`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="file-integrity-page">
      <style>
        {`
          .file-integrity-page {
            width: 100%;
            color: #e8f1ff;
            background: #071525;
            border: 1px solid #173f66;
            border-radius: 16px;
            padding: 28px;
            box-sizing: border-box;
          }

          .file-integrity-page *,
          .file-integrity-page *::before,
          .file-integrity-page *::after {
            box-sizing: border-box;
          }

          .file-integrity-header {
            margin-bottom: 24px;
          }

          .file-integrity-eyebrow {
            margin: 0 0 8px;
            color: #5da9ff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
          }

          .file-integrity-title {
            margin: 0;
            color: #f4f8ff;
            font-size: 28px;
            font-weight: 800;
            line-height: 1.2;
          }

          .file-integrity-description {
            margin: 10px 0 0;
            color: #8ea9c5;
            font-size: 14px;
            line-height: 1.6;
          }

          .file-integrity-upload {
            border: 1px solid #194b7a;
            background: #0a1d31;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 18px;
          }

          .file-integrity-upload-title {
            margin: 0 0 14px;
            color: #dfeeff;
            font-size: 16px;
            font-weight: 700;
          }

          .file-integrity-input {
            width: 100%;
            color: #c9dcf2;
            background: #081827;
            border: 1px solid #27577f;
            border-radius: 10px;
            padding: 12px;
            cursor: pointer;
          }

          .file-integrity-input::file-selector-button {
            margin-right: 12px;
            padding: 9px 14px;
            color: #ffffff;
            background: #1877e8;
            border: 0;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
          }

          .file-integrity-selected {
            margin-top: 15px;
            padding: 13px 15px;
            border-radius: 10px;
            background: #0d2943;
            border: 1px solid #1d4f78;
          }

          .file-integrity-selected-label {
            color: #7ea2c4;
            font-size: 12px;
            margin-bottom: 5px;
          }

          .file-integrity-selected-name {
            color: #f3f8ff;
            font-size: 14px;
            font-weight: 700;
            word-break: break-word;
          }

          .file-integrity-selected-size {
            color: #89a6c3;
            font-size: 12px;
            margin-top: 4px;
          }

          .file-integrity-button {
            width: 100%;
            margin-top: 16px;
            border: 0;
            border-radius: 10px;
            padding: 13px 18px;
            color: #ffffff;
            background: linear-gradient(
              135deg,
              #1676ec,
              #2468d8
            );
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            transition:
              transform 0.15s ease,
              opacity 0.15s ease;
          }

          .file-integrity-button:hover {
            transform: translateY(-1px);
          }

          .file-integrity-button:disabled {
            opacity: 0.65;
            cursor: not-allowed;
            transform: none;
          }

          .file-integrity-error {
            margin-top: 14px;
            padding: 12px 14px;
            border-radius: 10px;
            color: #ffd8df;
            background: #34131b;
            border: 1px solid #71303c;
            font-size: 13px;
          }

          .file-integrity-result {
            margin-top: 22px;
            background: #081a2d;
            border: 1px solid #1a4d79;
            border-radius: 14px;
            overflow: hidden;
          }

          .file-integrity-result-header {
            padding: 18px 20px;
            border-bottom: 1px solid #173d62;
            background: #0b223a;
          }

          .file-integrity-result-heading {
            margin: 0;
            color: #f2f7ff;
            font-size: 20px;
            font-weight: 800;
          }

          .file-integrity-result-subtitle {
            margin: 5px 0 0;
            color: #86a4c2;
            font-size: 12px;
          }

          .file-integrity-result-body {
            padding: 20px;
          }

          .file-integrity-status {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 7px 11px;
            margin-bottom: 18px;
            border-radius: 999px;
            color: #7ff0c8;
            background: rgba(18, 185, 129, 0.12);
            border: 1px solid rgba(18, 185, 129, 0.32);
            font-size: 12px;
            font-weight: 800;
          }

          .file-integrity-status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #36d9a0;
          }

          .file-integrity-info-grid {
            display: grid;
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
            gap: 12px;
          }

          .file-integrity-info-card {
            min-width: 0;
            padding: 15px;
            background: #0b2137;
            border: 1px solid #17476f;
            border-radius: 11px;
          }

          .file-integrity-info-label {
            display: block;
            margin-bottom: 7px;
            color: #7698b9;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.7px;
          }

          .file-integrity-info-value {
            display: block;
            color: #edf5ff;
            font-size: 14px;
            font-weight: 750;
            word-break: break-word;
          }

          .file-integrity-hash-card {
            margin-top: 14px;
            padding: 16px;
            background: #061320;
            border: 1px solid #22557f;
            border-radius: 11px;
          }

          .file-integrity-hash-label {
            display: block;
            margin-bottom: 9px;
            color: #76a6d0;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.8px;
            text-transform: uppercase;
          }

          .file-integrity-hash {
            display: block;
            color: #7be6ff;
            font-family:
              "SFMono-Regular",
              Consolas,
              "Liberation Mono",
              monospace;
            font-size: 13px;
            line-height: 1.7;
            word-break: break-all;
            white-space: normal;
          }

          .file-integrity-note {
            margin: 16px 0 0;
            color: #88a5c1;
            font-size: 12px;
            line-height: 1.65;
          }

          .file-integrity-history {
            margin-top: 10px;
            color: #7193b3;
            font-size: 12px;
          }

          @media (max-width: 700px) {
            .file-integrity-page {
              padding: 18px;
            }

            .file-integrity-title {
              font-size: 23px;
            }

            .file-integrity-info-grid {
              grid-template-columns: 1fr;
            }
          }
        `}
      </style>

      <div className="file-integrity-header">
        <p className="file-integrity-eyebrow">
          FORENSIC TOOL
        </p>

        <h2 className="file-integrity-title">
          File Integrity
        </h2>

        <p className="file-integrity-description">
          Upload a file to calculate its SHA-256 hash
          and generate an integrity report.
        </p>
      </div>

      <div className="file-integrity-upload">
        <h3 className="file-integrity-upload-title">
          Select File
        </h3>

        <input
          className="file-integrity-input"
          type="file"
          onChange={handleFileChange}
        />

        {file && (
          <div className="file-integrity-selected">
            <div className="file-integrity-selected-label">
              Selected File
            </div>

            <div className="file-integrity-selected-name">
              {file.name}
            </div>

            <div className="file-integrity-selected-size">
              {formatBytes(file.size)}
              {file.type ? ` • ${file.type}` : ""}
            </div>
          </div>
        )}

        <button
          type="button"
          className="file-integrity-button"
          onClick={analyzeFileIntegrity}
          disabled={!file || loading}
        >
          {loading
            ? "Generating SHA-256..."
            : "Analyze File Integrity"}
        </button>

        {error && (
          <div className="file-integrity-error">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="file-integrity-result">
          <div className="file-integrity-result-header">
            <h3 className="file-integrity-result-heading">
              Integrity Analysis Result
            </h3>

            <p className="file-integrity-result-subtitle">
              Cryptographic file integrity report
            </p>
          </div>

          <div className="file-integrity-result-body">
            <div className="file-integrity-status">
              <span className="file-integrity-status-dot" />
              {status}
            </div>

            <div className="file-integrity-info-grid">
              <div className="file-integrity-info-card">
                <span className="file-integrity-info-label">
                  Filename
                </span>

                <span className="file-integrity-info-value">
                  {filename}
                </span>
              </div>

              <div className="file-integrity-info-card">
                <span className="file-integrity-info-label">
                  File Type
                </span>

                <span className="file-integrity-info-value">
                  {fileType}
                </span>
              </div>

              <div className="file-integrity-info-card">
                <span className="file-integrity-info-label">
                  File Size
                </span>

                <span className="file-integrity-info-value">
                  {formatBytes(fileSize)}
                </span>
              </div>

              <div className="file-integrity-info-card">
                <span className="file-integrity-info-label">
                  Algorithm
                </span>

                <span className="file-integrity-info-value">
                  {algorithm}
                </span>
              </div>
            </div>

            <div className="file-integrity-hash-card">
              <span className="file-integrity-hash-label">
                SHA-256 Hash
              </span>

              <code className="file-integrity-hash">
                {sha256 || "Hash unavailable"}
              </code>
            </div>

            <p className="file-integrity-note">
              SHA-256 identifies the current file contents.
              Without a reference hash, it does not by itself
              prove authenticity or that the file is unchanged
              from an earlier version.
            </p>

            {historyId && (
              <div className="file-integrity-history">
                History ID: <strong>{historyId}</strong>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileIntegrity;