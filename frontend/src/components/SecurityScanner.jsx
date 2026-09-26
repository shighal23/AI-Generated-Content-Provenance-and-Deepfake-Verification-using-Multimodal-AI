import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function SecurityScanner() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const scanUrl = async () => {
    if (!url.trim()) {
      setError("Please enter a URL first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/api/scanner/scan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: url.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Security scan failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message || "Security scan failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const scanner =
    result?.report?.scanner_analysis || {};

  const summary =
    result?.report?.summary || {};

  const findings =
    scanner.findings ||
    summary.findings ||
    [];

  const riskScore =
    Number(scanner.risk_score ?? 0);

  const verdict =
    scanner.verdict || "UNKNOWN";

  return (
    <section className="scanner-page">
      <div className="scanner-header">
        <div>
          <p className="scanner-eyebrow">
            SECURITY FORENSICS
          </p>

          <h2>Security Scanner</h2>

          <p className="scanner-subtitle">
            Scan URLs for structural security indicators,
            suspicious keywords and risky patterns.
          </p>
        </div>

        <div className="scanner-status">
          <span />
          Scanner Ready
        </div>
      </div>

      <div className="scanner-input-panel">
        <label htmlFor="scanner-url">
          URL Security Scan
        </label>

        <div className="scanner-input-row">
          <input
            id="scanner-url"
            type="url"
            value={url}
            onChange={(event) => {
              setUrl(event.target.value);
              setError("");
              setResult(null);
            }}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !loading
              ) {
                scanUrl();
              }
            }}
            placeholder="https://example.com/login"
          />

          <button
            type="button"
            onClick={scanUrl}
            disabled={loading}
          >
            {loading
              ? "Scanning..."
              : "Run Security Scan"}
          </button>
        </div>

        <p className="scanner-input-help">
          Enter a complete URL including
          http:// or https://
        </p>

        {error && (
          <div className="scanner-error">
            {error}
          </div>
        )}
      </div>

      {!result && !loading && (
        <div className="scanner-empty">
          <div className="scanner-empty-icon">
            ⌁
          </div>

          <h3>Ready to scan</h3>

          <p>
            Enter a URL above to start the DeepVerify-X
            security scanner.
          </p>
        </div>
      )}

      {result && (
        <div className="scanner-results">

          <div className="scanner-result-top">

            <div>
              <p className="scanner-eyebrow">
                SCAN RESULT
              </p>

              <h3>Security Scan Completed</h3>

              <p className="scanner-url-display">
                {scanner.url || url}
              </p>
            </div>

            <div
              className={`scanner-verdict ${
                verdict.toLowerCase()
              }`}
            >
              {verdict.replace(/_/g, " ")}
            </div>

          </div>

          <div className="scanner-metrics">

            <div className="scanner-metric">
              <span>Risk Score</span>

              <strong>
                {riskScore}
              </strong>

              <small>
                out of 100
              </small>
            </div>

            <div className="scanner-metric">
              <span>Domain</span>

              <strong>
                {scanner.domain || "N/A"}
              </strong>
            </div>

            <div className="scanner-metric">
              <span>HTTPS</span>

              <strong>
                {scanner.https
                  ? "Secure"
                  : "Not Secure"}
              </strong>
            </div>

            <div className="scanner-metric">
              <span>Findings</span>

              <strong>
                {findings.length}
              </strong>
            </div>

          </div>

          <div className="scanner-analysis-grid">

            <div className="scanner-panel">
              <h4>Security Indicators</h4>

              <div className="scanner-row">
                <span>IP Address URL</span>
                <strong>
                  {scanner.ip_address_url
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Shortened URL</span>
                <strong>
                  {scanner.shortened_url
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Excessive Subdomains</span>
                <strong>
                  {scanner.excessive_subdomains
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Unusual Port</span>
                <strong>
                  {scanner.unusual_port
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>
            </div>

            <div className="scanner-panel">
              <h4>Scanner Information</h4>

              <div className="scanner-row">
                <span>Scan Type</span>

                <strong>
                  {scanner.scan_type ||
                    "URL Security Scan"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Scheme</span>

                <strong>
                  {scanner.scheme || "N/A"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Analysis Status</span>

                <strong>
                  {scanner.analysis_status ||
                    "COMPLETED"}
                </strong>
              </div>

              <div className="scanner-row">
                <span>Method</span>

                <strong>
                  {scanner.method ||
                    "DeepVerify-X Security Scanner"}
                </strong>
              </div>
            </div>

          </div>

          <div className="scanner-findings-panel">
            <h4>Scanner Findings</h4>

            {findings.length > 0 ? (
              findings.map(
                (finding, index) => (
                  <div
                    className="scanner-finding"
                    key={index}
                  >
                    <span>!</span>

                    <div>
                      <strong>
                        Finding {index + 1}
                      </strong>

                      <p>
                        {finding}
                      </p>
                    </div>
                  </div>
                )
              )
            ) : (
              <div className="scanner-finding success">
                <span>✓</span>

                <div>
                  <strong>
                    No major findings
                  </strong>

                  <p>
                    No major structural security
                    indicators were detected.
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="scanner-note">
            Scanner results are based on structural
            and heuristic security indicators and
            should not be treated as conclusive proof
            that a website is malicious or safe.
          </div>

        </div>
      )}
    </section>
  );
}

export default SecurityScanner;