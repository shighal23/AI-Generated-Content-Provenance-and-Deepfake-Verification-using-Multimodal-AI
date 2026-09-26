import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatBytes(value) {
  const size = Number(value || 0);

  if (!size) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(
    Math.floor(Math.log(size) / Math.log(1024)),
    units.length - 1
  );

  return `${(size / Math.pow(1024, index)).toFixed(index ? 2 : 0)} ${units[index]}`;
}

function formatDate(value) {
  if (!value) {
    return "N/A";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }

  return date.toLocaleString();
}

function extensionFromName(name) {
  if (!name) {
    return "N/A";
  }

  const parts = name.split(".");
  if (parts.length < 2) {
    return "N/A";
  }

  return `.${parts.pop().toLowerCase()}`;
}

async function sha256(file) {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);

  const hashArray = Array.from(new Uint8Array(hashBuffer));

  return hashArray
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function getImageDimensions(file) {
  return new Promise((resolve) => {
    if (!file || !file.type.startsWith("image/")) {
      resolve(null);
      return;
    }

    const objectUrl = URL.createObjectURL(file);

    const image = new Image();

    image.onload = () => {
      const result = {
        width: image.naturalWidth,
        height: image.naturalHeight,
      };

      URL.revokeObjectURL(objectUrl);
      resolve(result);
    };

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(null);
    };

    image.src = objectUrl;
  });
}

function MetricCard({ label, value }) {
  return (
    <div
      style={{
        border: "1px solid #dbe3ee",
        borderRadius: "10px",
        background: "#ffffff",
        padding: "12px",
        minWidth: 0,
      }}
    >
      <div
        style={{
          fontSize: "8px",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          fontWeight: 800,
          color: "#94a3b8",
        }}
      >
        {label}
      </div>

      <div
        style={{
          marginTop: "6px",
          fontSize: "12px",
          fontWeight: 850,
          color: "#0f172a",
          wordBreak: "break-word",
          lineHeight: 1.45,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function FileColumn({ title, file, info, previewUrl }) {
  return (
    <div
      style={{
        border: "1px solid #dbe3ee",
        borderRadius: "13px",
        background: "#ffffff",
        padding: "14px",
        minWidth: 0,
      }}
    >
      <div
        style={{
          fontSize: "10px",
          color: "#2563eb",
          fontWeight: 850,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: "7px",
          fontSize: "14px",
          fontWeight: 900,
          color: "#0f172a",
          wordBreak: "break-word",
        }}
      >
        {file?.name || "No file selected"}
      </div>

      {previewUrl && (
        <div
          style={{
            marginTop: "12px",
            background: "#0b1324",
            borderRadius: "10px",
            padding: "10px",
            textAlign: "center",
          }}
        >
          <img
            src={previewUrl}
            alt={`${title} preview`}
            style={{
              maxWidth: "100%",
              maxHeight: "280px",
              objectFit: "contain",
              borderRadius: "7px",
            }}
          />
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
          gap: "8px",
          marginTop: "12px",
        }}
      >
        <MetricCard
          label="Size"
          value={file ? formatBytes(file.size) : "N/A"}
        />

        <MetricCard
          label="Type"
          value={file?.type || "Unknown"}
        />

        <MetricCard
          label="Extension"
          value={file ? extensionFromName(file.name) : "N/A"}
        />

        <MetricCard
          label="Dimensions"
          value={
            info?.dimensions
              ? `${info.dimensions.width} × ${info.dimensions.height}`
              : "N/A"
          }
        />

        <MetricCard
          label="Modified"
          value={file ? formatDate(file.lastModified) : "N/A"}
        />

        <MetricCard
          label="SHA-256"
          value={info?.sha256 ? `${info.sha256.slice(0, 20)}…` : "N/A"}
        />
      </div>

      {info?.sha256 && (
        <div
          style={{
            marginTop: "10px",
            padding: "9px 10px",
            borderRadius: "8px",
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            fontSize: "9px",
            color: "#475569",
            lineHeight: 1.5,
            wordBreak: "break-all",
          }}
        >
          <strong>SHA-256:</strong> {info.sha256}
        </div>
      )}
    </div>
  );
}

function ComparisonRow({ label, left, right, difference }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1.1fr 1fr 1fr 1fr",
        borderTop: "1px solid #eef2f7",
        fontSize: "10px",
        color: "#475569",
      }}
    >
      <div
        style={{
          padding: "10px",
          fontWeight: 800,
          color: "#334155",
        }}
      >
        {label}
      </div>

      <div
        style={{
          padding: "10px",
          wordBreak: "break-word",
        }}
      >
        {left}
      </div>

      <div
        style={{
          padding: "10px",
          wordBreak: "break-word",
        }}
      >
        {right}
      </div>

      <div
        style={{
          padding: "10px",
          fontWeight: 800,
          wordBreak: "break-word",
        }}
      >
        {difference}
      </div>
    </div>
  );
}

function comparisonDifference(a, b, mode = "text") {
  if (a === undefined || a === null) {
    return "N/A";
  }

  if (b === undefined || b === null) {
    return "N/A";
  }

  if (mode === "number") {
    const x = Number(a);
    const y = Number(b);

    if (!Number.isFinite(x) || !Number.isFinite(y)) {
      return "N/A";
    }

    if (x === y) {
      return "No change";
    }

    const delta = y - x;
    const sign = delta > 0 ? "+" : "";

    return `${sign}${formatBytes(Math.abs(delta))}`;
  }

  return String(a) === String(b) ? "No change" : "Different";
}

function ComputerFiles() {
  const [fileOne, setFileOne] = useState(null);
  const [fileTwo, setFileTwo] = useState(null);

  const [previewOne, setPreviewOne] = useState("");
  const [previewTwo, setPreviewTwo] = useState("");

  const [infoOne, setInfoOne] = useState(null);
  const [infoTwo, setInfoTwo] = useState(null);

  const [comparison, setComparison] = useState(null);

  const [elaOne, setElaOne] = useState(null);
  const [elaTwo, setElaTwo] = useState(null);

  const [loading, setLoading] = useState(false);
  const [elaLoading, setElaLoading] = useState(false);
  const [error, setError] = useState("");

  const inputOneRef = useRef(null);
  const inputTwoRef = useRef(null);

  useEffect(() => {
    return () => {
      if (previewOne) {
        URL.revokeObjectURL(previewOne);
      }

      if (previewTwo) {
        URL.revokeObjectURL(previewTwo);
      }
    };
  }, [previewOne, previewTwo]);

  const processFile = async (file) => {
    if (!file) {
      return null;
    }

    const [hash, dimensions] = await Promise.all([
      sha256(file),
      getImageDimensions(file),
    ]);

    return {
      sha256: hash,
      dimensions,
    };
  };

  const handleFileOne = async (event) => {
    const selected = event.target.files?.[0] || null;

    setError("");
    setComparison(null);
    setElaOne(null);
    setElaTwo(null);

    if (previewOne) {
      URL.revokeObjectURL(previewOne);
    }

    setFileOne(selected);

    if (!selected) {
      setPreviewOne("");
      setInfoOne(null);
      return;
    }

    if (selected.type.startsWith("image/")) {
      setPreviewOne(URL.createObjectURL(selected));
    } else {
      setPreviewOne("");
    }

    try {
      setLoading(true);
      const info = await processFile(selected);
      setInfoOne(info);
    } catch (err) {
      setError(err.message || "Unable to process File 1.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileTwo = async (event) => {
    const selected = event.target.files?.[0] || null;

    setError("");
    setComparison(null);
    setElaOne(null);
    setElaTwo(null);

    if (previewTwo) {
      URL.revokeObjectURL(previewTwo);
    }

    setFileTwo(selected);

    if (!selected) {
      setPreviewTwo("");
      setInfoTwo(null);
      return;
    }

    if (selected.type.startsWith("image/")) {
      setPreviewTwo(URL.createObjectURL(selected));
    } else {
      setPreviewTwo("");
    }

    try {
      setLoading(true);
      const info = await processFile(selected);
      setInfoTwo(info);
    } catch (err) {
      setError(err.message || "Unable to process File 2.");
    } finally {
      setLoading(false);
    }
  };

  const compareFiles = () => {
    setError("");

    if (!fileOne || !fileTwo) {
      setError("Please select both File 1 and File 2.");
      return;
    }

    if (!infoOne || !infoTwo) {
      setError("File information is still being prepared. Please try again.");
      return;
    }

    const sameHash = infoOne.sha256 === infoTwo.sha256;

    const sameName = fileOne.name === fileTwo.name;
    const sameType = fileOne.type === fileTwo.type;

    const sameDimensions =
      !!infoOne.dimensions &&
      !!infoTwo.dimensions &&
      infoOne.dimensions.width === infoTwo.dimensions.width &&
      infoOne.dimensions.height === infoTwo.dimensions.height;

    const sizeDifference =
      Number(fileTwo.size || 0) - Number(fileOne.size || 0);

    const sizePercent =
      Number(fileOne.size || 0) > 0
        ? ((sizeDifference / Number(fileOne.size)) * 100).toFixed(2)
        : "N/A";

    const changes = [];

    if (!sameHash) {
      changes.push("Binary content differs.");
    }

    if (!sameName) {
      changes.push("Filenames are different.");
    }

    if (!sameType) {
      changes.push("MIME types are different.");
    }

    if (
      infoOne.dimensions &&
      infoTwo.dimensions &&
      !sameDimensions
    ) {
      changes.push("Image dimensions are different.");
    }

    if (sizeDifference !== 0) {
      changes.push(
        `File size changed by ${sizePercent}% compared with File 1.`
      );
    }

    if (!changes.length) {
      changes.push("No differences detected in the compared file properties.");
    }

    setComparison({
      sameHash,
      sameName,
      sameType,
      sameDimensions,
      sizeDifference,
      sizePercent,
      changes,
    });
  };

  const clearAll = () => {
    if (previewOne) {
      URL.revokeObjectURL(previewOne);
    }

    if (previewTwo) {
      URL.revokeObjectURL(previewTwo);
    }

    setFileOne(null);
    setFileTwo(null);
    setPreviewOne("");
    setPreviewTwo("");
    setInfoOne(null);
    setInfoTwo(null);
    setComparison(null);
    setElaOne(null);
    setElaTwo(null);
    setError("");

    if (inputOneRef.current) {
      inputOneRef.current.value = "";
    }

    if (inputTwoRef.current) {
      inputTwoRef.current.value = "";
    }
  };

  const runELACompare = async () => {
    setError("");

    if (!fileOne || !fileTwo) {
      setError("Please select both image files first.");
      return;
    }

    const supportedOne = /\.(jpg|jpeg|png|webp)$/i.test(fileOne.name);
    const supportedTwo = /\.(jpg|jpeg|png|webp)$/i.test(fileTwo.name);

    if (!supportedOne || !supportedTwo) {
      setError(
        "ELA comparison is available only when both selected files are JPG, JPEG, PNG or WEBP images."
      );
      return;
    }

    setElaLoading(true);
    setElaOne(null);
    setElaTwo(null);

    try {
      const uploadForELA = async (file) => {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_URL}/api/analyze/image`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || `ELA analysis failed for ${file.name}.`
          );
        }

        return data?.report || null;
      };

      const [reportOne, reportTwo] = await Promise.all([
        uploadForELA(fileOne),
        uploadForELA(fileTwo),
      ]);

      setElaOne(reportOne);
      setElaTwo(reportTwo);
    } catch (err) {
      setError(err.message || "ELA comparison failed.");
    } finally {
      setElaLoading(false);
    }
  };

  const elaMetrics = (report) => {
    const ela = report?.forensics?.ela || {};
    const noise = report?.forensics?.noise || {};

    return {
      meanDifference: ela?.mean_difference ?? "N/A",
      maxDifference: ela?.max_difference ?? "N/A",
      meanNoise:
        noise?.mean_noise !== undefined
          ? Number(noise.mean_noise).toFixed(4)
          : "N/A",
      noiseStd:
        noise?.noise_std !== undefined
          ? Number(noise.noise_std).toFixed(4)
          : "N/A",
      heatmapPath: ela?.heatmap_path || "",
    };
  };

  const getHeatmapUrl = (report) => {
    const path = report?.forensics?.ela?.heatmap_path || "";

    if (!path) {
      return "";
    }

    const filename = path.split(/[/\\]/).pop();

    if (!filename) {
      return "";
    }

    return `${API_URL}/reports/ela/${encodeURIComponent(filename)}`;
  };

  const elaMetricsOne = elaOne ? elaMetrics(elaOne) : null;
  const elaMetricsTwo = elaTwo ? elaMetrics(elaTwo) : null;

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
          gap: "16px",
          alignItems: "flex-start",
          flexWrap: "wrap",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "10px",
              color: "#2563eb",
              fontWeight: 850,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              marginBottom: "7px",
            }}
          >
            Forensic Workspace
          </div>

          <h1
            style={{
              margin: 0,
              fontSize: "24px",
              color: "#0f172a",
            }}
          >
            Computer Files
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
            Compare two files from your computer using file metadata and
            SHA-256 fingerprints. Image pairs can also be checked with ELA.
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
            fontWeight: 850,
          }}
        >
          FILE COMPARISON
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
          gap: "12px",
          marginTop: "18px",
        }}
      >
        <div
          style={{
            border: "1.5px dashed #cbd5e1",
            background: "#f8fbff",
            borderRadius: "13px",
            padding: "16px",
          }}
        >
          <div
            style={{
              fontSize: "11px",
              fontWeight: 850,
              color: "#334155",
              marginBottom: "8px",
            }}
          >
            File 1
          </div>

          <input
            ref={inputOneRef}
            type="file"
            onChange={handleFileOne}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px",
              background: "#ffffff",
              border: "1px solid #dbe3ee",
              borderRadius: "9px",
              fontSize: "10px",
            }}
          />

          {fileOne && (
            <div
              style={{
                marginTop: "8px",
                color: "#64748b",
                fontSize: "9px",
                wordBreak: "break-word",
              }}
            >
              Selected:{" "}
              <strong style={{ color: "#334155" }}>
                {fileOne.name}
              </strong>
            </div>
          )}
        </div>

        <div
          style={{
            border: "1.5px dashed #cbd5e1",
            background: "#f8fbff",
            borderRadius: "13px",
            padding: "16px",
          }}
        >
          <div
            style={{
              fontSize: "11px",
              fontWeight: 850,
              color: "#334155",
              marginBottom: "8px",
            }}
          >
            File 2
          </div>

          <input
            ref={inputTwoRef}
            type="file"
            onChange={handleFileTwo}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px",
              background: "#ffffff",
              border: "1px solid #dbe3ee",
              borderRadius: "9px",
              fontSize: "10px",
            }}
          />

          {fileTwo && (
            <div
              style={{
                marginTop: "8px",
                color: "#64748b",
                fontSize: "9px",
                wordBreak: "break-word",
              }}
            >
              Selected:{" "}
              <strong style={{ color: "#334155" }}>
                {fileTwo.name}
              </strong>
            </div>
          )}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          gap: "8px",
          flexWrap: "wrap",
          marginTop: "12px",
        }}
      >
        <button
          type="button"
          onClick={clearAll}
          disabled={loading || elaLoading}
          style={{
            border: "1px solid #dbe3ee",
            background: "#ffffff",
            color: "#334155",
            borderRadius: "9px",
            padding: "9px 13px",
            fontSize: "10px",
            fontWeight: 800,
            cursor: loading || elaLoading ? "not-allowed" : "pointer",
            opacity: loading || elaLoading ? 0.55 : 1,
          }}
        >
          Clear
        </button>

        <button
          type="button"
          onClick={compareFiles}
          disabled={loading || elaLoading}
          style={{
            border: "1px solid #2563eb",
            background: "#2563eb",
            color: "#ffffff",
            borderRadius: "9px",
            padding: "9px 14px",
            fontSize: "10px",
            fontWeight: 800,
            cursor: loading || elaLoading ? "not-allowed" : "pointer",
            opacity: loading || elaLoading ? 0.7 : 1,
          }}
        >
          {loading ? "Preparing..." : "Compare Files"}
        </button>

        <button
          type="button"
          onClick={runELACompare}
          disabled={loading || elaLoading}
          style={{
            border: "1px solid #0f766e",
            background: "#0f766e",
            color: "#ffffff",
            borderRadius: "9px",
            padding: "9px 14px",
            fontSize: "10px",
            fontWeight: 800,
            cursor: loading || elaLoading ? "not-allowed" : "pointer",
            opacity: loading || elaLoading ? 0.7 : 1,
          }}
        >
          {elaLoading ? "Running ELA..." : "Compare ELA"}
        </button>
      </div>

      {error && (
        <div
          style={{
            marginTop: "12px",
            padding: "10px 12px",
            borderRadius: "9px",
            background: "#fef2f2",
            border: "1px solid #fecaca",
            color: "#b91c1c",
            fontSize: "10px",
            lineHeight: 1.5,
          }}
        >
          {error}
        </div>
      )}

      {(fileOne || fileTwo) && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "12px",
            marginTop: "16px",
          }}
        >
          <FileColumn
            title="File 1"
            file={fileOne}
            info={infoOne}
            previewUrl={previewOne}
          />

          <FileColumn
            title="File 2"
            file={fileTwo}
            info={infoTwo}
            previewUrl={previewTwo}
          />
        </div>
      )}

      {comparison && (
        <div
          style={{
            marginTop: "16px",
            border: "1px solid #dbe3ee",
            borderRadius: "13px",
            overflow: "hidden",
            background: "#ffffff",
          }}
        >
          <div
            style={{
              padding: "14px",
              background: "#f8fbff",
              borderBottom: "1px solid #dbe3ee",
            }}
          >
            <div
              style={{
                fontSize: "11px",
                color: "#0f172a",
                fontWeight: 900,
              }}
            >
              Comparison Results
            </div>

            <div
              style={{
                marginTop: "4px",
                fontSize: "9px",
                color: "#64748b",
              }}
            >
              Exact file properties and SHA-256 comparison.
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.1fr 1fr 1fr 1fr",
              background: "#f8fafc",
              fontSize: "8px",
              fontWeight: 850,
              color: "#64748b",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            <div style={{ padding: "10px" }}>Attribute</div>
            <div style={{ padding: "10px" }}>File 1</div>
            <div style={{ padding: "10px" }}>File 2</div>
            <div style={{ padding: "10px" }}>Difference</div>
          </div>

          <ComparisonRow
            label="File Name"
            left={fileOne?.name || "N/A"}
            right={fileTwo?.name || "N/A"}
            difference={comparison.sameName ? "No change" : "Different"}
          />

          <ComparisonRow
            label="File Size"
            left={fileOne ? formatBytes(fileOne.size) : "N/A"}
            right={fileTwo ? formatBytes(fileTwo.size) : "N/A"}
            difference={
              comparison.sizeDifference === 0
                ? "No change"
                : `${comparison.sizeDifference > 0 ? "+" : ""}${comparison.sizePercent}%`
            }
          />

          <ComparisonRow
            label="MIME Type"
            left={fileOne?.type || "Unknown"}
            right={fileTwo?.type || "Unknown"}
            difference={comparison.sameType ? "No change" : "Different"}
          />

          <ComparisonRow
            label="Dimensions"
            left={
              infoOne?.dimensions
                ? `${infoOne.dimensions.width} × ${infoOne.dimensions.height}`
                : "N/A"
            }
            right={
              infoTwo?.dimensions
                ? `${infoTwo.dimensions.width} × ${infoTwo.dimensions.height}`
                : "N/A"
            }
            difference={
              comparison.sameDimensions
                ? "No change"
                : infoOne?.dimensions && infoTwo?.dimensions
                ? "Changed"
                : "N/A"
            }
          />

          <ComparisonRow
            label="SHA-256"
            left={infoOne?.sha256 || "N/A"}
            right={infoTwo?.sha256 || "N/A"}
            difference={
              comparison.sameHash
                ? "IDENTICAL"
                : "DIFFERENT CONTENT"
            }
          />
        </div>
      )}

      {comparison && (
        <div
          style={{
            marginTop: "12px",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "12px",
          }}
        >
          <div
            style={{
              border: "1px solid #dbe3ee",
              borderRadius: "12px",
              padding: "14px",
              background: comparison.sameHash ? "#f0fdf4" : "#fff7ed",
            }}
          >
            <div
              style={{
                fontSize: "9px",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "#64748b",
                fontWeight: 850,
              }}
            >
              Binary Integrity Comparison
            </div>

            <div
              style={{
                marginTop: "6px",
                fontSize: "18px",
                fontWeight: 950,
                color: comparison.sameHash ? "#166534" : "#c2410c",
              }}
            >
              {comparison.sameHash ? "IDENTICAL" : "DIFFERENT"}
            </div>

            <div
              style={{
                marginTop: "5px",
                fontSize: "9px",
                color: "#64748b",
                lineHeight: 1.5,
              }}
            >
              {comparison.sameHash
                ? "Both files have the same SHA-256 fingerprint."
                : "The files have different SHA-256 fingerprints."}
            </div>
          </div>

          <div
            style={{
              border: "1px solid #dbe3ee",
              borderRadius: "12px",
              padding: "14px",
              background: "#ffffff",
            }}
          >
            <div
              style={{
                fontSize: "9px",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "#64748b",
                fontWeight: 850,
              }}
            >
              Changes Detected
            </div>

            <div
              style={{
                marginTop: "8px",
                display: "grid",
                gap: "7px",
              }}
            >
              {comparison.changes.map((change, index) => (
                <div
                  key={index}
                  style={{
                    fontSize: "9px",
                    color: "#475569",
                    lineHeight: 1.5,
                    paddingBottom:
                      index === comparison.changes.length - 1
                        ? 0
                        : "7px",
                    borderBottom:
                      index === comparison.changes.length - 1
                        ? 0
                        : "1px solid #eef2f7",
                  }}
                >
                  • {change}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {(elaOne || elaTwo) && (
        <div
          style={{
            marginTop: "16px",
            border: "1px solid #dbe3ee",
            borderRadius: "13px",
            padding: "14px",
            background: "#ffffff",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "11px",
                fontWeight: 900,
                color: "#0f172a",
              }}
            >
              ELA Comparison
            </div>

            <div
              style={{
                marginTop: "4px",
                fontSize: "9px",
                color: "#64748b",
              }}
            >
              ELA values are forensic indicators and should be interpreted
              together with other evidence.
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "12px",
              marginTop: "12px",
            }}
          >
            <div
              style={{
                border: "1px solid #dbe3ee",
                borderRadius: "11px",
                padding: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  fontWeight: 850,
                  color: "#334155",
                  marginBottom: "9px",
                }}
              >
                File 1 — ELA
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: "8px",
                }}
              >
                <MetricCard
                  label="Mean Difference"
                  value={elaMetricsOne?.meanDifference ?? "N/A"}
                />

                <MetricCard
                  label="Max Difference"
                  value={elaMetricsOne?.maxDifference ?? "N/A"}
                />

                <MetricCard
                  label="Mean Noise"
                  value={elaMetricsOne?.meanNoise ?? "N/A"}
                />

                <MetricCard
                  label="Noise Std"
                  value={elaMetricsOne?.noiseStd ?? "N/A"}
                />
              </div>

              {getHeatmapUrl(elaOne) && (
                <div
                  style={{
                    marginTop: "10px",
                    background: "#0b1324",
                    borderRadius: "9px",
                    padding: "9px",
                  }}
                >
                  <img
                    src={getHeatmapUrl(elaOne)}
                    alt="File 1 ELA heatmap"
                    style={{
                      width: "100%",
                      maxHeight: "330px",
                      objectFit: "contain",
                      borderRadius: "7px",
                    }}
                  />
                </div>
              )}
            </div>

            <div
              style={{
                border: "1px solid #dbe3ee",
                borderRadius: "11px",
                padding: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  fontWeight: 850,
                  color: "#334155",
                  marginBottom: "9px",
                }}
              >
                File 2 — ELA
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: "8px",
                }}
              >
                <MetricCard
                  label="Mean Difference"
                  value={elaMetricsTwo?.meanDifference ?? "N/A"}
                />

                <MetricCard
                  label="Max Difference"
                  value={elaMetricsTwo?.maxDifference ?? "N/A"}
                />

                <MetricCard
                  label="Mean Noise"
                  value={elaMetricsTwo?.meanNoise ?? "N/A"}
                />

                <MetricCard
                  label="Noise Std"
                  value={elaMetricsTwo?.noiseStd ?? "N/A"}
                />
              </div>

              {getHeatmapUrl(elaTwo) && (
                <div
                  style={{
                    marginTop: "10px",
                    background: "#0b1324",
                    borderRadius: "9px",
                    padding: "9px",
                  }}
                >
                  <img
                    src={getHeatmapUrl(elaTwo)}
                    alt="File 2 ELA heatmap"
                    style={{
                      width: "100%",
                      maxHeight: "330px",
                      objectFit: "contain",
                      borderRadius: "7px",
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div
        style={{
          marginTop: "15px",
          paddingTop: "11px",
          borderTop: "1px solid #eef2f7",
          fontSize: "9px",
          color: "#94a3b8",
          lineHeight: 1.5,
        }}
      >
        SHA-256 equality means the files are byte-for-byte identical. Different
        hashes mean the file contents differ, but do not by themselves prove
        malicious manipulation.
      </div>

      <style>{`
        @media (max-width: 900px) {
          .computer-files-responsive {
            grid-template-columns: 1fr !important;
          }
        }

        @media (max-width: 680px) {
          .computer-files-responsive-small {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

export default ComputerFiles;