import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function URLVerification() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const verifyURL = async () => {
    if (!url.trim()) {
      setError("Please enter a URL first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/analyze/url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "URL verification failed."
        );
      }

      setResult(data.report);
    } catch (err) {
      setError(err.message || "URL verification failed.");
    } finally {
      setLoading(false);
    }
  };

  const urlAnalysis = result?.url_analysis;
  const summary = result?.summary;

  const riskScore = Math.min(
    Math.max(Number(urlAnalysis?.risk_score ?? 0), 0),
    100
  );

  const verdict = urlAnalysis?.verdict || "UNKNOWN";

  return (
    <section className="url-verification">

      {/* ================= HEADER ================= */}

      <div className="results-heading">
        <div>
          <h2>URL Verification</h2>

          <p>
            Analyze URLs for suspicious structural
            and security indicators.
          </p>
        </div>
      </div>

      {/* ================= URL INPUT ================= */}

      <div className="url-input-section">

        <input
          type="url"
          value={url}
          onChange={(event) => {
            setUrl(event.target.value);
            setError("");
            setResult(null);
          }}
          placeholder="https://example.com"
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              verifyURL();
            }
          }}
        />

        <button
          onClick={verifyURL}
          disabled={loading}
        >
          {loading ? "Verifying..." : "Verify URL"}
        </button>

      </div>

      {/* ================= ERROR ================= */}

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* ================= RESULT ================= */}

      {result && (
        <div className="url-result">

          {/* RESULT HEADER */}

          <div className="results-heading">

            <div>
              <h2>URL Verification Result</h2>

              <p>
                {summary?.url || url}
              </p>
            </div>

            <div
              className={`verdict ${verdict.toLowerCase()}`}
            >
              {verdict.replace(/_/g, " ")}
            </div>

          </div>

          {/* ================= SCORE ================= */}

          <div className="score-card">

            <span>URL Risk Score</span>

            <strong>{riskScore}</strong>

            <small>out of 100</small>

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

            <div className="card">
              <span>Domain</span>

              <strong>
                {urlAnalysis?.domain || "N/A"}
              </strong>
            </div>

            <div className="card">
              <span>Scheme</span>

              <strong>
                {urlAnalysis?.scheme
                  ? urlAnalysis.scheme.toUpperCase()
                  : "N/A"}
              </strong>
            </div>

            <div className="card">
              <span>HTTPS</span>

              <strong>
                {urlAnalysis?.is_https
                  ? "Yes"
                  : "No"}
              </strong>
            </div>

            <div className="card">
              <span>IP Address</span>

              <strong>
                {urlAnalysis?.is_ip_address
                  ? "Yes"
                  : "No"}
              </strong>
            </div>

            <div className="card">
              <span>Shortened URL</span>

              <strong>
                {urlAnalysis?.is_shortened_url
                  ? "Yes"
                  : "No"}
              </strong>
            </div>

            <div className="card">
              <span>Port</span>

              <strong>
                {urlAnalysis?.port ?? "Default"}
              </strong>
            </div>

          </div>

          {/* ================= URL STRUCTURE ================= */}

          <div className="analysis-grid">

            <div className="panel">

              <h3>URL Structure</h3>

              <div className="info-row">
                <span>Domain</span>

                <strong>
                  {urlAnalysis?.domain || "N/A"}
                </strong>
              </div>

              <div className="info-row">
                <span>Path</span>

                <strong>
                  {urlAnalysis?.path || "/"}
                </strong>
              </div>

              <div className="info-row">
                <span>Query</span>

                <strong>
                  {urlAnalysis?.query || "None"}
                </strong>
              </div>

              <div className="info-row">
                <span>Subdomains</span>

                <strong>
                  {urlAnalysis?.subdomain_count ?? 0}
                </strong>
              </div>

              <div className="info-row">
                <span>Excessive Subdomains</span>

                <strong>
                  {urlAnalysis?.excessive_subdomains
                    ? "Yes"
                    : "No"}
                </strong>
              </div>

              <div className="info-row">
                <span>Unusual Port</span>

                <strong>
                  {urlAnalysis?.unusual_port
                    ? "Yes"
                    : "No"}
                </strong>
              </div>

            </div>

            {/* ================= SECURITY ================= */}

            <div className="panel">

              <h3>Security Indicators</h3>

              <div className="info-row">
                <span>HTTPS</span>

                <strong>
                  {urlAnalysis?.is_https
                    ? "Secure"
                    : "Not Secure"}
                </strong>
              </div>

              <div className="info-row">
                <span>IP Address URL</span>

                <strong>
                  {urlAnalysis?.is_ip_address
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

              <div className="info-row">
                <span>Shortened URL</span>

                <strong>
                  {urlAnalysis?.is_shortened_url
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

              <div className="info-row">
                <span>Unusual Port</span>

                <strong>
                  {urlAnalysis?.unusual_port
                    ? "Detected"
                    : "Not Detected"}
                </strong>
              </div>

            </div>

          </div>

          {/* ================= KEYWORDS ================= */}

          <div className="analysis-grid">

            {/* KEYWORD MATCHES */}

            <div className="panel">

              <h3>Keyword Matches</h3>

              {urlAnalysis?.keyword_matches?.length > 0 ? (

                urlAnalysis.keyword_matches.map(
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
                  <span>✓</span>

                  No suspicious keywords detected.
                </div>

              )}

            </div>

            {/* PATH KEYWORDS */}

            <div className="panel">

              <h3>Suspicious Path Keywords</h3>

              {urlAnalysis?.suspicious_path_keywords?.length > 0 ? (

                urlAnalysis.suspicious_path_keywords.map(
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
                  <span>✓</span>

                  No suspicious path keywords detected.
                </div>

              )}

            </div>

          </div>

          {/* ================= QUERY ================= */}

          <div className="analysis-grid">

            <div className="panel">

              <h3>Suspicious Query Keywords</h3>

              {urlAnalysis?.suspicious_query_keywords?.length > 0 ? (

                urlAnalysis.suspicious_query_keywords.map(
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
                  <span>✓</span>

                  No suspicious query keywords detected.
                </div>

              )}

            </div>

            {/* QUERY PARAMETERS */}

            <div className="panel">

              <h3>Query Parameters</h3>

              {urlAnalysis?.query_parameters &&
              Object.keys(
                urlAnalysis.query_parameters
              ).length > 0 ? (

                Object.entries(
                  urlAnalysis.query_parameters
                ).map(([key, value]) => (
                  <div
                    className="info-row"
                    key={key}
                  >
                    <span>{key}</span>

                    <strong>
                      {String(value)}
                    </strong>
                  </div>
                ))

              ) : (

                <div className="reason success">
                  <span>✓</span>

                  No query parameters detected.
                </div>

              )}

            </div>

          </div>

          {/* ================= RISK ASSESSMENT ================= */}

          <div className="reasons">

            <h3>URL Risk Assessment</h3>

            {urlAnalysis?.reasons?.length > 0 ? (

              urlAnalysis.reasons.map(
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

                No significant suspicious URL
                indicators detected.
              </div>

            )}

            <p className="risk-disclaimer">
              Method:{" "}
              {urlAnalysis?.method ||
                "URL Forensic Analysis"}
            </p>

            <p className="risk-disclaimer">
              Analysis Status:{" "}
              {urlAnalysis?.analysis_status ||
                "COMPLETED"}
            </p>

            <p className="risk-disclaimer">
              Note: URL forensic indicators are
              structural and heuristic signals. They
              should not be treated as conclusive proof
              that a website is malicious or safe.
            </p>

          </div>

        </div>
      )}

    </section>
  );
}

export default URLVerification;