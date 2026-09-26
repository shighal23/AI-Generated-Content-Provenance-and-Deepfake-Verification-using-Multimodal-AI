import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatNumber(value, digits = 4) {
  if (value === undefined || value === null || value === "") {
    return "N/A";
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return String(value);
  }

  return number.toFixed(digits);
}

function getHeatmapUrl(report) {
  const heatmapPath = report?.forensics?.ela?.heatmap_path || "";

  if (!heatmapPath) {
    return "";
  }

  const fileName = heatmapPath.split(/[/\\]/).pop();

  if (!fileName) {
    return "";
  }

  return `${API_URL}/reports/ela/${encodeURIComponent(fileName)}`;
}

function ELAAnalysis({ onCompleted }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    setResult(null);
    setError("");

    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
    } else {
      setPreviewUrl("");
    }
  };

  const clearAnalysis = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(null);
    setPreviewUrl("");
    setResult(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const runELA = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/api/analyze/image`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "ELA Analysis failed."
        );
      }

      setResult(data);

      if (typeof onCompleted === "function") {
        await onCompleted();
      }
    } catch (err) {
      setError(
        err.message || "Unable to complete ELA Analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  const report = result?.report || null;
  const forensics = report?.forensics || {};
  const ela = forensics?.ela || {};
  const noise = forensics?.noise || {};
  const metadata = forensics?.metadata || {};
  const risk = report?.risk_assessment || {};

  const heatmapUrl = getHeatmapUrl(report);

  const findings = Array.isArray(risk?.reasons)
    ? risk.reasons
    : [];

  return (
    <section
      style={{
        background: "#ffffff",
        border: "1px solid #dbe3ee",
        borderRadius: "16px",
        padding: "22px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "10px",
              fontWeight: 800,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "#2563eb",
              marginBottom: "7px",
            }}
          >
            Forensic Analysis
          </div>

          <h1
            style={{
              margin: 0,
              fontSize: "24px",
              color: "#0f172a",
            }}
          >
            ELA Analysis
          </h1>

          <p
            style={{
              margin: "7px 0 0",
              color: "#64748b",
              fontSize: "12px",
              lineHeight: 1.6,
              maxWidth: "760px",
            }}
          >
            Error Level Analysis checks JPEG recompression
            differences and highlights regions that show
            different error-level behaviour.
          </p>
        </div>

        <div
          style={{
            padding: "8px 11px",
            borderRadius: "999px",
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            color: "#1d4ed8",
            fontSize: "9px",
            fontWeight: 800,
          }}
        >
          STANDALONE FORENSICS
        </div>
      </div>

      <div
        style={{
          marginTop: "18px",
          border: "1.5px dashed #cbd5e1",
          background: "#f8fbff",
          borderRadius: "13px",
          padding: "18px",
        }}
      >
        <div
          style={{
            fontSize: "12px",
            fontWeight: 800,
            color: "#334155",
            marginBottom: "8px",
          }}
        >
          Upload Image
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          onChange={handleFileChange}
          style={{
            width: "100%",
            padding: "10px",
            border: "1px solid #dbe3ee",
            borderRadius: "9px",
            background: "#ffffff",
            boxSizing: "border-box",
            fontSize: "11px",
          }}
        />

        {selectedFile && (
          <div
            style={{
              marginTop: "8px",
              fontSize: "10px",
              color: "#64748b",
            }}
          >
            Selected:{" "}
            <strong style={{ color: "#334155" }}>
              {selectedFile.name}
            </strong>
          </div>
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: "8px",
            marginTop: "12px",
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            onClick={clearAnalysis}
            disabled={loading}
            style={{
              border: "1px solid #dbe3ee",
              background: "#ffffff",
              color: "#334155",
              borderRadius: "9px",
              padding: "9px 13px",
              fontSize: "10px",
              fontWeight: 800,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.55 : 1,
            }}
          >
            Clear
          </button>

          <button
            type="button"
            onClick={runELA}
            disabled={loading}
            style={{
              border: "1px solid #2563eb",
              background: "#2563eb",
              color: "#ffffff",
              borderRadius: "9px",
              padding: "9px 14px",
              fontSize: "10px",
              fontWeight: 800,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "Running ELA..." : "Run ELA Analysis"}
          </button>
        </div>

        {error && (
          <div
            style={{
              marginTop: "11px",
              padding: "10px 12px",
              borderRadius: "9px",
              background: "#fef2f2",
              border: "1px solid #fecaca",
              color: "#b91c1c",
              fontSize: "10px",
            }}
          >
            {error}
          </div>
        )}
      </div>

      {previewUrl && (
        <div
          style={{
            marginTop: "16px",
            border: "1px solid #dbe3ee",
            borderRadius: "13px",
            padding: "14px",
            background: "#ffffff",
          }}
        >
          <h3
            style={{
              margin: "0 0 10px",
              fontSize: "12px",
              color: "#334155",
            }}
          >
            Original Image
          </h3>

          <div
            style={{
              background: "#0b1324",
              borderRadius: "10px",
              padding: "12px",
              textAlign: "center",
            }}
          >
            <img
              src={previewUrl}
              alt="Original uploaded image"
              style={{
                maxWidth: "100%",
                maxHeight: "420px",
                objectFit: "contain",
                borderRadius: "8px",
              }}
            />
          </div>
        </div>
      )}

      {result && (
        <>
          <div
            style={{
              marginTop: "16px",
              padding: "14px",
              borderRadius: "12px",
              background: "#f7faff",
              border: "1px solid #dbeafe",
            }}
          >
            <div
              style={{
                fontSize: "9px",
                color: "#64748b",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              Analysis Completed
            </div>

            <div
              style={{
                marginTop: "5px",
                color: "#0f172a",
                fontSize: "12px",
                fontWeight: 800,
                wordBreak: "break-word",
              }}
            >
              {report?.verification?.filename ||
                selectedFile?.name ||
                "Image"}
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(4, minmax(0, 1fr))",
              gap: "10px",
              marginTop: "14px",
            }}
          >
            {[
              ["Format", metadata?.format || "N/A"],
              ["Width", metadata?.width ?? "N/A"],
              ["Height", metadata?.height ?? "N/A"],
              ["EXIF", metadata?.has_exif ? "Yes" : "No"],
            ].map(([label, value]) => (
              <div
                key={label}
                style={{
                  border: "1px solid #dbe3ee",
                  borderRadius: "10px",
                  padding: "11px",
                  background: "#ffffff",
                }}
              >
                <div
                  style={{
                    fontSize: "8px",
                    color: "#94a3b8",
                    fontWeight: 700,
                    textTransform: "uppercase",
                  }}
                >
                  {label}
                </div>

                <div
                  style={{
                    marginTop: "5px",
                    color: "#0f172a",
                    fontSize: "11px",
                    fontWeight: 800,
                    wordBreak: "break-word",
                  }}
                >
                  {String(value)}
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(5, minmax(0, 1fr))",
              gap: "10px",
              marginTop: "14px",
            }}
          >
            {[
              ["JPEG Quality", ela?.jpeg_quality ?? "N/A"],
              [
                "Mean Difference",
                ela?.mean_difference ?? "N/A",
              ],
              [
                "Maximum Difference",
                ela?.max_difference ?? "N/A",
              ],
              [
                "Mean Noise",
                formatNumber(noise?.mean_noise),
              ],
              [
                "Noise Std",
                formatNumber(noise?.noise_std),
              ],
            ].map(([label, value]) => (
              <div
                key={label}
                style={{
                  border: "1px solid #dbe3ee",
                  borderRadius: "10px",
                  padding: "11px",
                  background: "#ffffff",
                }}
              >
                <div
                  style={{
                    fontSize: "8px",
                    color: "#94a3b8",
                    fontWeight: 700,
                    textTransform: "uppercase",
                  }}
                >
                  {label}
                </div>

                <div
                  style={{
                    marginTop: "6px",
                    color: "#0f172a",
                    fontSize: "14px",
                    fontWeight: 900,
                  }}
                >
                  {String(value)}
                </div>
              </div>
            ))}
          </div>

          {heatmapUrl && (
            <div
              style={{
                marginTop: "16px",
                border: "1px solid #dbe3ee",
                borderRadius: "13px",
                padding: "14px",
                background: "#ffffff",
              }}
            >
              <h3
                style={{
                  margin: 0,
                  fontSize: "12px",
                  color: "#334155",
                }}
              >
                ELA Heatmap
              </h3>

              <p
                style={{
                  margin: "6px 0 12px",
                  fontSize: "10px",
                  color: "#64748b",
                  lineHeight: 1.5,
                }}
              >
                Highlighted regions show areas with different
                error-level response after JPEG recompression.
              </p>

              <div
                style={{
                  background: "#0b1324",
                  borderRadius: "10px",
                  padding: "12px",
                  textAlign: "center",
                }}
              >
                <img
                  src={heatmapUrl}
                  alt="ELA Heatmap"
                  style={{
                    width: "100%",
                    maxHeight: "500px",
                    objectFit: "contain",
                    borderRadius: "8px",
                  }}
                  onError={(event) => {
                    event.currentTarget.style.display = "none";
                  }}
                />
              </div>
            </div>
          )}

          <div
            style={{
              marginTop: "16px",
              border: "1px solid #dbe3ee",
              borderRadius: "13px",
              padding: "14px",
              background: "#ffffff",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: "12px",
                color: "#334155",
              }}
            >
              ELA Interpretation
            </h3>

            {findings.length ? (
              findings.map((finding, index) => (
                <div
                  key={index}
                  style={{
                    display: "flex",
                    gap: "8px",
                    alignItems: "flex-start",
                    borderTop:
                      index === 0
                        ? "0"
                        : "1px solid #eef2f7",
                    padding:
                      index === 0 ? "9px 0 0" : "9px 0",
                    fontSize: "10px",
                    color: "#475569",
                    lineHeight: 1.5,
                  }}
                >
                  <span
                    style={{
                      width: "17px",
                      height: "17px",
                      display: "grid",
                      placeItems: "center",
                      borderRadius: "6px",
                      background: "#fff7ed",
                      color: "#ea580c",
                      flex: "0 0 auto",
                      fontWeight: 900,
                    }}
                  >
                    !
                  </span>

                  <span>{finding}</span>
                </div>
              ))
            ) : (
              <div
                style={{
                  marginTop: "9px",
                  padding: "9px",
                  borderRadius: "8px",
                  background: "#f0fdf4",
                  border: "1px solid #bbf7d0",
                  color: "#166534",
                  fontSize: "10px",
                }}
              >
                No specific ELA risk finding was returned.
              </div>
            )}

            <div
              style={{
                marginTop: "12px",
                paddingTop: "10px",
                borderTop: "1px solid #eef2f7",
                fontSize: "9px",
                color: "#94a3b8",
                lineHeight: 1.5,
              }}
            >
              ELA is a forensic indicator. It should not be
              treated as conclusive proof that an image is
              manipulated or AI-generated.
            </div>
          </div>
        </>
      )}

      <style>{`
        @media (max-width: 1050px) {
          .ela-analysis-info-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
          }
        }

        @media (max-width: 760px) {
          .ela-analysis-info-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

export default ELAAnalysis;