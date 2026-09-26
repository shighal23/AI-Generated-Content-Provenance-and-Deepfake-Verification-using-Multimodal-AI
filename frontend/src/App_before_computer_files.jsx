import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

import FileIntegrity from "./components/FileIntegrity";
import SecurityScanner from "./components/SecurityScanner";
import ELAAnalysis from "./components/ELAAnalysis";

const API_URL = "http://127.0.0.1:8000";

function Icon({ name, size = 18 }) {
  const p = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.9,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
  };

  if (name === "grid") return <svg {...p}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>;
  if (name === "shield") return <svg {...p}><path d="M12 3 20 6v6c0 5-3.3 8-8 9-4.7-1-8-4-8-9V6l8-3Z"/><path d="m9 12 2 2 4-4"/></svg>;
  if (name === "image") return <svg {...p}><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m5 17 4.5-4 3 2.5 2-2 4.5 4"/></svg>;
  if (name === "video") return <svg {...p}><rect x="3" y="5" width="13" height="14" rx="2"/><path d="m16 9 5-3v12l-5-3z"/></svg>;
  if (name === "audio") return <svg {...p}><path d="M5 10v4M9 7v10M13 4v16M17 8v8M21 10v4"/></svg>;
  if (name === "message") return <svg {...p}><path d="M4 5h16v11H8l-4 4V5Z"/><path d="M8 9h8M8 12h5"/></svg>;
  if (name === "document") return <svg {...p}><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v5h5M10 12h5M10 16h5"/></svg>;
  if (name === "link") return <svg {...p}><path d="M10 13a5 5 0 0 0 7.5.5l1.5-1.5a5 5 0 0 0-7.1-7.1L11 5.8"/><path d="M14 11a5 5 0 0 0-7.5-.5L5 12a5 5 0 0 0 7.1 7.1l.9-.9"/></svg>;
  if (name === "qr") return <svg {...p}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><path d="M14 14h3v3h-3zM18 18h3M18 14v2M14 19v2M21 14v3"/></svg>;
  if (name === "scan") return <svg {...p}><path d="M5 4H4a1 1 0 0 0-1 1v3M19 4h1a1 1 0 0 1 1 1v3M5 20H4a1 1 0 0 1-1-1v-3M19 20h1a1 1 0 0 0 1-1v-3"/><path d="M7 12h10"/></svg>;
  if (name === "layers") return <svg {...p}><path d="m12 3 8 4-8 4-8-4 8-4Z"/><path d="m4 12 8 4 8-4M4 17l8 4 8-4"/></svg>;
  if (name === "hash") return <svg {...p}><path d="M10 3 8 21M16 3l-2 18M4 9h17M3 15h17"/></svg>;
  if (name === "folder") return <svg {...p}><path d="M3 7h6l2 2h10v10H3z"/><path d="M3 7V5h6l2 2"/></svg>;
  if (name === "history") return <svg {...p}><path d="M4 12a8 8 0 1 0 2.3-5.7L4 9"/><path d="M4 4v5h5"/><path d="M12 7v5l3 2"/></svg>;
  if (name === "report") return <svg {...p}><path d="M6 3h12v18H6z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg>;
  if (name === "settings") return <svg {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.6 1.6-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V20h-2.4v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.6-1.6.1-.1A1.7 1.7 0 0 0 8.6 15a1.7 1.7 0 0 0-1.6-1H6.8v-2.4H7a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.6-1.6.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V4h2.4v.2a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.6 1.6-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2V14h-.2a1.7 1.7 0 0 0-1.6 1Z"/></svg>;
  if (name === "bell") return <svg {...p}><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></svg>;
  if (name === "search") return <svg {...p}><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg>;
  if (name === "download") return <svg {...p}><path d="M12 3v11M7 10l5 5 5-5M4 20h16"/></svg>;
  if (name === "trash") return <svg {...p}><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></svg>;
  if (name === "refresh") return <svg {...p}><path d="M20 11a8 8 0 0 0-14.6-4L4 9"/><path d="M4 4v5h5M4 13a8 8 0 0 0 14.6 4L20 15"/><path d="M20 20v-5h-5"/></svg>;
  if (name === "close") return <svg {...p}><path d="m6 6 12 12M18 6 6 18"/></svg>;
  if (name === "check") return <svg {...p}><path d="m5 12 4 4L19 6"/></svg>;
  if (name === "alert") return <svg {...p}><path d="M12 3 22 20H2L12 3Z"/><path d="M12 9v5M12 17h.01"/></svg>;
  return <svg {...p}><circle cx="12" cy="12" r="8"/></svg>;
}

const navGroups = [
  {
    title: "Workspace",
    items: [
      ["dashboard", "Dashboard", "grid"],
      ["verify", "Verify", "shield"],
    ],
  },
  {
    title: "Verification",
    items: [
      ["image", "Image", "image"],
      ["video", "Video", "video"],
      ["audio", "Audio", "audio"],
      ["message", "Message", "message"],
      ["document", "Document", "document"],
      ["url", "URL", "link"],
      ["qr", "QR Code", "qr"],
    ],
  },
  {
    title: "Forensics",
    items: [
      ["scanner", "Security Scanner", "scan"],
      ["ela", "ELA Analysis", "layers"],
      ["file-integrity", "File Integrity", "hash"],
      ["computer-files", "Computer Files", "folder"],
    ],
  },
];

function verdictText(value) {
  return String(value || "UNKNOWN").replace(/_/g, " ");
}

function riskLevel(score) {
  const n = Number(score || 0);
  if (n >= 70) return "high";
  if (n >= 35) return "medium";
  return "low";
}

function bytes(value) {
  const n = Number(value || 0);
  if (!n) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(n) / Math.log(1024)), units.length - 1);
  return `${(n / Math.pow(1024, i)).toFixed(i ? 2 : 0)} ${units[i]}`;
}

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

  const [activeNav, setActiveNav] = useState("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [darkThemeEnabled, setDarkThemeEnabled] = useState(true);
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);

  const dashboardRef = useRef(null);
  const verificationRef = useRef(null);
  const historyRef = useRef(null);
  const reportRef = useRef(null);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/history`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to load history.");
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

  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") {
        setShowProfileMenu(false);
        setShowNotificationPanel(false);
        setShowSettingsModal(false);
      }
    };
    window.document.addEventListener("keydown", onKey);
    return () => window.document.removeEventListener("keydown", onKey);
  }, []);

  const totalAnalyses = history.length;
  const lowRiskCount = history.filter((x) => x.verdict?.toUpperCase() === "LOW_RISK").length;
  const mediumRiskCount = history.filter((x) => x.verdict?.toUpperCase() === "MEDIUM_RISK").length;
  const highRiskCount = history.filter((x) => x.verdict?.toUpperCase() === "HIGH_RISK").length;
  const averageRisk = history.length
    ? Math.round(history.reduce((s, x) => s + Number(x.risk_score || 0), 0) / history.length)
    : 0;

  const filteredHistory = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return history;
    return history.filter((x) =>
      [x.filename, x.file_type, x.verdict, x.timestamp].filter(Boolean).join(" ").toLowerCase().includes(q)
    );
  }, [history, searchQuery]);

  const scrollToSection = (ref) => {
    if (!ref?.current) return;
    ref.current.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleAnalysisTypeChange = (type) => {
    setAnalysisType(type);
    setFile(null);
    setResult(null);
    setSelectedHistory(null);
    setError("");
  };

  const handleNav = (item) => {
    setActiveNav(item);
    setShowProfileMenu(false);
    setShowNotificationPanel(false);

    if (item === "dashboard") {
      setError("");
      scrollToSection(dashboardRef);
      return;
    }

    if (item === "history" || item === "reports") {
      setError("");
      loadHistory();
      scrollToSection(historyRef);
      return;
    }

    if (item === "verify") {
      setError("");
      scrollToSection(verificationRef);
      return;
    }

    if (item === "scanner") {
      setError("");
      setResult(null);
      setSelectedHistory(null);
      return;
    }

    if (["image", "video", "audio", "message", "document", "url", "qr"].includes(item)) {
      handleAnalysisTypeChange(item);
      setError("");
      scrollToSection(verificationRef);
      return;
    }

    if (item === "ela") {
      setError("");
      setResult(null);
      setSelectedHistory(null);
      setFile(null);
      return;  
    }

    if (item === "file-integrity") {
      handleAnalysisTypeChange("file-integrity");
      setError("");
      scrollToSection(verificationRef);
      return;
    }

    if (item === "computer-files") {
      setError("Computer Files module is reserved for the forensic workspace.");
      return;
    }

    if (item === "settings") {
      setError("");
      setShowSettingsModal(true);
      return;
    }
  };

  const openScanner = () => {
    setActiveNav("scanner");
    setResult(null);
    setSelectedHistory(null);
    setError("");
    setShowProfileMenu(false);
    setShowNotificationPanel(false);
  };

  const clearCurrent = () => {
    setFile(null);
    setResult(null);
    setSelectedHistory(null);
    setError("");
  };

  const handleFileChange = (event) => {
    setFile(event.target.files?.[0] || null);
    setResult(null);
    setSelectedHistory(null);
    setError("");
  };

  const analyzeFile = async (endpoint, errorMessage, inputName = "file") => {
    if (!file || typeof file === "string") {
      setError(errorMessage);
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);
    const formData = new FormData();
    formData.append(inputName, file);

    try {
      const response = await fetch(`${API_URL}${endpoint}`, { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || errorMessage);
      setResult(data);
      await loadHistory();
      if (autoScrollEnabled) setTimeout(() => scrollToSection(reportRef), 180);
    } catch (err) {
      setError(err.message || errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const analyzeImage = () => analyzeFile("/api/analyze/image", "Image analysis failed.");
  const analyzeVideo = () => analyzeFile("/api/analyze/video", "Video analysis failed.");
  const analyzeAudio = () => analyzeFile("/api/analyze/audio", "Audio analysis failed.");
  const analyzeDocument = () => analyzeFile("/api/analyze/document", "Document analysis failed.");
  const analyzeQR = () => analyzeFile("/api/analyze/qr", "QR analysis failed.");

  const analyzeMessage = async () => {
    if (typeof file !== "string" || !file.trim()) {
      setError("Please enter a message first.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);
    try {
      const response = await fetch(`${API_URL}/api/analyze/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: file.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Message analysis failed.");
      setResult(data);
      await loadHistory();
      if (autoScrollEnabled) setTimeout(() => scrollToSection(reportRef), 180);
    } catch (err) {
      setError(err.message || "Message analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const analyzeURL = async () => {
    if (typeof file !== "string" || !file.trim()) {
      setError("Please enter a URL first.");
      return;
    }
    const url = file.trim();
    try { new URL(url); } catch {
      setError("Please enter a valid URL.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    setSelectedHistory(null);
    try {
      const response = await fetch(`${API_URL}/api/analyze/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "URL analysis failed.");
      setResult(data);
      await loadHistory();
      if (autoScrollEnabled) setTimeout(() => scrollToSection(reportRef), 180);
    } catch (err) {
      setError(err.message || "URL analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const openHistory = async (id) => {
    try {
      setError("");
      const response = await fetch(`${API_URL}/api/history/${id}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to load history record.");
      setSelectedHistory(data.history);
      setResult(null);
      setActiveNav("history");
      if (autoScrollEnabled) setTimeout(() => scrollToSection(reportRef), 120);
    } catch (err) {
      setError(err.message || "Unable to load history record.");
    }
  };

  const deleteHistory = async (id) => {
    const item = history.find((x) => x.id === id);
    if (!window.confirm(`Delete "${item?.filename || "this record"}" from history?`)) return;
    setDeleteLoading(id);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/history/${id}`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to delete history record.");
      if (selectedHistory?.id === id) {
        setSelectedHistory(null);
        setResult(null);
      }
      await loadHistory();
    } catch (err) {
      setError(err.message || "Unable to delete history record.");
    } finally {
      setDeleteLoading(null);
    }
  };

  const clearHistory = async () => {
    if (!history.length) return;
    if (!window.confirm("Are you sure you want to delete ALL analysis history?")) return;
    setClearLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/history`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to clear history.");
      setHistory([]);
      setSelectedHistory(null);
      setResult(null);
    } catch (err) {
      setError(err.message || "Unable to clear history.");
    } finally {
      setClearLoading(false);
    }
  };

  const report = result?.report;
  const selectedReport = selectedHistory?.report;
  const activeReport = report || selectedReport;

  const scanner = activeReport?.scanner_analysis;
  const qr = activeReport?.qr_analysis;
  const url = activeReport?.url_analysis;
  const video = activeReport?.video_analysis;
  const audio = activeReport?.audio_analysis;
  const message = activeReport?.message_analysis;
  const doc = activeReport?.document_analysis;
  const risk = activeReport?.risk_assessment;
  const ml = activeReport?.ml_analysis;
  const forensics = activeReport?.forensics;

  const isScannerReport = activeReport?.verification?.file_type === "scanner" || !!scanner;
  const isQRReport = activeReport?.verification?.file_type === "qr" || !!qr;
  const isURLReport = activeReport?.verification?.file_type === "url" || !!url;
  const isVideoReport = activeReport?.verification?.file_type === "video" || !!video;
  const isAudioReport = activeReport?.verification?.file_type === "audio" || !!audio;
  const isMessageReport = activeReport?.verification?.file_type === "message" || !!message;
  const isDocumentReport = activeReport?.verification?.file_type === "document" || !!doc;

  const riskScore = Math.min(Math.max(Number(
    risk?.risk_score ?? message?.risk_score ?? scanner?.risk_score ?? qr?.risk_score ?? url?.risk_score ?? 0
  ), 0), 100);

  const verdict = risk?.verdict || message?.verdict || scanner?.verdict || qr?.verdict || url?.verdict ||
    (isVideoReport ? "VIDEO_ANALYSIS_COMPLETED" :
      isAudioReport ? "AUDIO_ANALYSIS_COMPLETED" :
        isDocumentReport ? "DOCUMENT_ANALYSIS_COMPLETED" : "UNKNOWN");

  const heatmapPath = forensics?.ela?.heatmap_path || "";
  const heatmapName = heatmapPath ? heatmapPath.split(/[/\\]/).pop() : "";
  const heatmapUrl = heatmapName ? `${API_URL}/reports/ela/${encodeURIComponent(heatmapName)}` : "";
  const integrity = forensics?.integrity;

  const latest = history.length ? history[history.length - 1] : null;

  return (
    <div className={`dv-root ${darkThemeEnabled ? "dv-dark" : ""}`}>
      <style>{`
        .dv-root{min-height:100vh;background:#eef3f8;color:#0f172a;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}.dv-shell{display:flex;min-height:100vh}.dv-side{position:fixed;inset:0 auto 0 0;width:248px;background:#0b1324;color:#cbd5e1;padding:20px 14px;overflow:auto}.dv-brand{display:flex;gap:10px;align-items:center;padding:4px 8px 18px}.dv-brand-mark{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#0ea5e9);color:#fff}.dv-brand-title{font-size:17px;font-weight:800;color:#fff}.dv-brand-sub{font-size:10px;color:#7f91aa;margin-top:2px;line-height:1.3}.dv-nav-group{margin-top:12px}.dv-nav-title{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#667993;padding:0 9px 7px}.dv-nav-btn{width:100%;border:0;background:transparent;color:#aebdce;display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:10px;margin:2px 0;cursor:pointer;font-size:12px;text-align:left}.dv-nav-btn:hover{background:rgba(255,255,255,.06);color:#fff}.dv-nav-btn.active{background:rgba(37,99,235,.2);color:#fff;box-shadow:inset 3px 0 #60a5fa}.dv-main{margin-left:248px;width:calc(100% - 248px)}.dv-top{height:72px;position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);border-bottom:1px solid #dbe3ee;display:flex;align-items:center;gap:16px;padding:0 24px;backdrop-filter:blur(10px)}.dv-title{font-size:18px;font-weight:800}.dv-bread{font-size:10px;color:#94a3b8;margin-top:3px}.dv-top-right{display:flex;gap:10px;align-items:center;margin-left:auto}.dv-search{width:min(360px,36vw);display:flex;align-items:center;gap:8px;background:#f8fafc;border:1px solid #dbe3ee;border-radius:10px;padding:9px 11px}.dv-search input{width:100%;border:0;outline:0;background:transparent;font-size:12px}.dv-icon-btn{width:37px;height:37px;border:1px solid #dbe3ee;border-radius:10px;background:#fff;display:grid;place-items:center;cursor:pointer;color:#475569;position:relative}.dv-dot{position:absolute;right:7px;top:7px;width:6px;height:6px;border-radius:50%;background:#ef4444}.dv-profile{display:flex;gap:8px;align-items:center;border:0;background:transparent;cursor:pointer}.dv-avatar{width:37px;height:37px;border-radius:50%;display:grid;place-items:center;background:#dbeafe;color:#1d4ed8;font-weight:800;font-size:12px}.dv-pname{font-size:11px;font-weight:800}.dv-prole{font-size:10px;color:#94a3b8;margin-top:2px}.dv-drop{position:absolute;right:24px;top:58px;width:215px;background:#fff;border:1px solid #dbe3ee;border-radius:13px;box-shadow:0 18px 48px rgba(15,23,42,.14);padding:7px;z-index:40}.dv-drop button{width:100%;border:0;background:transparent;padding:9px 10px;border-radius:8px;text-align:left;display:flex;gap:8px;align-items:center;font-size:11px;color:#334155;cursor:pointer}.dv-drop button:hover{background:#f1f5f9}.dv-notif{width:285px;padding:12px}.dv-content{padding:24px}.dv-section{scroll-margin-top:90px;margin-bottom:18px}.dv-hero{border:1px solid #dbe3ee;border-radius:17px;background:linear-gradient(135deg,#fff,#f4f8ff);padding:24px;display:flex;justify-content:space-between;gap:18px;align-items:center}.dv-hero h1{margin:0;font-size:26px}.dv-hero p{margin:7px 0 0;color:#64748b;font-size:12px;line-height:1.6;max-width:760px}.dv-badge-top{background:#e0ecff;color:#1d4ed8;border-radius:10px;padding:9px 12px;font-size:10px;font-weight:800}.dv-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.dv-stat,.dv-card,.dv-panel,.dv-verification,.dv-result{background:#fff;border:1px solid #dbe3ee;border-radius:14px}.dv-stat{padding:15px}.dv-stat-top{display:flex;justify-content:space-between;align-items:center;color:#64748b;font-size:11px}.dv-stat-icon{width:29px;height:29px;border-radius:8px;display:grid;place-items:center;background:#eff6ff;color:#2563eb}.dv-stat-value{font-size:25px;font-weight:850;margin-top:10px}.dv-stat-meta{font-size:10px;color:#94a3b8;margin-top:6px}.dv-progress{height:6px;border-radius:99px;background:#edf2f7;overflow:hidden;margin-top:10px}.dv-progress span{display:block;height:100%;border-radius:inherit}.low span{background:#22c55e}.medium span{background:#f59e0b}.high span{background:#ef4444}.dv-two{display:grid;grid-template-columns:1.1fr .9fr;gap:12px}.dv-panel{padding:16px}.dv-panel h3,.dv-result h2{margin:0;font-size:14px}.dv-sub{color:#94a3b8;font-size:10px;margin-top:4px}.dv-risk{display:grid;grid-template-columns:140px 1fr;gap:18px;align-items:center;margin-top:16px}.dv-gauge{width:125px;height:125px;border-radius:50%;background:conic-gradient(#2563eb ${averageRisk}%,#e8eef6 0);display:grid;place-items:center}.dv-gauge-inner{width:98px;height:98px;border-radius:50%;background:#fff;display:grid;place-items:center;align-content:center}.dv-gauge-score{font-size:28px;font-weight:900}.dv-gauge-label{font-size:9px;color:#94a3b8}.dv-bars{display:grid;gap:10px}.dv-bar{display:grid;grid-template-columns:82px 1fr 35px;gap:8px;align-items:center;font-size:10px;color:#64748b}.dv-bar-track{height:8px;background:#edf2f7;border-radius:99px;overflow:hidden}.dv-bar-fill{height:100%;border-radius:inherit}.dv-bar-fill.low{background:#22c55e}.dv-bar-fill.medium{background:#f59e0b}.dv-bar-fill.high{background:#ef4444}.dv-activity{margin-top:12px}.dv-activity-item{display:flex;align-items:center;gap:10px;border-top:1px solid #eef2f7;padding:9px 0}.dv-activity-icon{width:31px;height:31px;border-radius:8px;background:#f1f5f9;color:#475569;display:grid;place-items:center}.dv-activity-file{font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dv-activity-time{font-size:9px;color:#94a3b8;margin-top:2px}.dv-section-head{display:flex;justify-content:space-between;gap:12px;align-items:end;margin-bottom:10px}.dv-section-head h2{margin:0;font-size:16px}.dv-section-head p{margin:4px 0 0;color:#64748b;font-size:10px}.dv-feature-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.dv-card{padding:14px}.dv-card-icon{width:35px;height:35px;border-radius:9px;background:#eff6ff;color:#2563eb;display:grid;place-items:center}.dv-card h3{margin:10px 0 4px;font-size:12px}.dv-card p{margin:0 0 11px;color:#64748b;font-size:10px;line-height:1.45;min-height:29px}.dv-btn{border:1px solid #dbe3ee;background:#fff;color:#334155;border-radius:9px;padding:8px 11px;font-size:10px;font-weight:800;cursor:pointer}.dv-btn.primary{background:#2563eb;border-color:#2563eb;color:#fff}.dv-btn.danger{background:#fff7f7;color:#b91c1c;border-color:#fecaca}.dv-btn:disabled{opacity:.55;cursor:not-allowed}.dv-verification{padding:17px}.dv-tabs{display:flex;gap:7px;flex-wrap:wrap}.dv-tab{border:1px solid #dbe3ee;background:#f8fafc;color:#475569;border-radius:9px;padding:8px 10px;font-size:10px;font-weight:800;display:inline-flex;align-items:center;gap:6px;cursor:pointer}.dv-tab.active{background:#eff6ff;color:#1d4ed8;border-color:#93c5fd}.dv-upload{border:1.5px dashed #cbd5e1;background:#fbfdff;border-radius:12px;margin-top:14px;padding:15px}.dv-input,.dv-textarea{width:100%;border:1px solid #dbe3ee;border-radius:9px;padding:10px;font:inherit;font-size:11px;outline:0}.dv-textarea{min-height:125px;resize:vertical}.dv-help{font-size:9px;color:#94a3b8;margin-top:5px}.dv-upload-actions{display:flex;justify-content:flex-end;gap:7px;margin-top:11px}.dv-error{margin-top:10px;padding:9px 11px;border:1px solid #fecaca;background:#fef2f2;color:#b91c1c;border-radius:9px;font-size:10px}.dv-table{overflow:auto;border:1px solid #dbe3ee;border-radius:12px;background:#fff}.dv-row,.dv-head{min-width:860px;display:grid;grid-template-columns:2fr 1fr .7fr 1fr 1.2fr 1.4fr;align-items:center;gap:8px;padding:10px 12px;font-size:10px}.dv-head{background:#f8fafc;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;font-size:9px;font-weight:800}.dv-row{border-top:1px solid #eef2f7}.dv-file{font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dv-actions{display:flex;gap:5px;flex-wrap:wrap}.dv-badge{display:inline-flex;border-radius:999px;padding:4px 7px;font-size:8px;font-weight:800}.dv-badge.low{background:#dcfce7;color:#15803d}.dv-badge.medium{background:#fef3c7;color:#b45309}.dv-badge.high{background:#fee2e2;color:#b91c1c}.dv-badge.neutral{background:#e2e8f0;color:#475569}.dv-result{padding:17px}.dv-result-head{display:flex;justify-content:space-between;gap:12px;align-items:start}.dv-result-file{color:#64748b;font-size:10px;margin-top:4px;word-break:break-word}.dv-score{margin-top:13px;padding:15px;border:1px solid #e5edf6;border-radius:12px;background:#f7faff}.dv-score-label{font-size:10px;color:#64748b}.dv-score-num{font-size:36px;font-weight:900;margin-top:2px}.dv-score-track{height:7px;border-radius:99px;background:#e7edf5;margin-top:9px;overflow:hidden}.dv-score-track span{display:block;height:100%;background:#2563eb;border-radius:inherit}.dv-info-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:12px}.dv-info{border:1px solid #dbe3ee;border-radius:10px;padding:10px}.dv-info small{display:block;color:#94a3b8;font-size:8px}.dv-info strong{display:block;font-size:11px;margin-top:5px;word-break:break-word}.dv-analysis{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:10px}.dv-box{border:1px solid #dbe3ee;border-radius:10px;padding:11px}.dv-box h3{font-size:11px;margin:0 0 8px}.dv-kv{display:flex;justify-content:space-between;gap:10px;border-top:1px solid #eef2f7;padding:7px 0;font-size:9px}.dv-kv:first-of-type{border-top:0;padding-top:0}.dv-kv span{color:#64748b}.dv-kv strong{max-width:65%;text-align:right;overflow-wrap:anywhere}.dv-reasons{margin-top:10px;border:1px solid #dbe3ee;border-radius:10px;padding:11px}.dv-reason{display:flex;gap:7px;border-top:1px solid #eef2f7;padding:7px 0;font-size:9px;color:#475569}.dv-reason:first-of-type{border-top:0}.dv-reason-icon{width:17px;height:17px;display:grid;place-items:center;border-radius:6px;background:#fff7ed;color:#ea580c;flex:0 0 auto}.dv-integrity{margin-top:10px;padding:11px;border:1px solid #bfdbfe;background:#eff6ff;border-radius:10px}.dv-hash{font:9px ui-monospace,monospace;word-break:break-all;color:#1e3a8a;background:#fff;border:1px solid #dbeafe;border-radius:8px;padding:9px;margin-top:7px;display:block}.dv-modal-bg{position:fixed;inset:0;background:rgba(2,6,23,.5);display:grid;place-items:center;padding:18px;z-index:100}.dv-modal{width:min(520px,100%);background:#fff;border-radius:15px;padding:15px;border:1px solid #dbe3ee}.dv-modal-head{display:flex;justify-content:space-between;align-items:center}.dv-modal h2{margin:0;font-size:14px}.dv-close{border:1px solid #dbe3ee;background:#fff;border-radius:8px;width:32px;height:32px;display:grid;place-items:center;cursor:pointer}.dv-setting{display:flex;justify-content:space-between;gap:12px;align-items:center;border-top:1px solid #eef2f7;padding:12px 0}.dv-setting:first-of-type{margin-top:8px}.dv-setting strong{display:block;font-size:11px}.dv-setting span{display:block;font-size:9px;color:#94a3b8;margin-top:3px}.dv-toggle{width:44px;height:24px;border:0;background:#cbd5e1;border-radius:99px;position:relative;cursor:pointer}.dv-toggle.on{background:#2563eb}.dv-toggle i{position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:#fff;transition:.15s}.dv-toggle.on i{transform:translateX(20px)}.scanner-shell{margin-top:0}.dv-empty{padding:25px;text-align:center;color:#94a3b8;font-size:10px}
        @media(max-width:1050px){.dv-stats{grid-template-columns:repeat(2,1fr)}.dv-feature-grid{grid-template-columns:repeat(2,1fr)}.dv-info-grid{grid-template-columns:repeat(2,1fr)}}
        @media(max-width:760px){.dv-side{position:static;width:100%;height:auto}.dv-main{margin-left:0;width:100%}.dv-shell{display:block}.dv-top{height:auto;padding:12px;align-items:flex-start}.dv-top-right{width:100%;flex-wrap:wrap}.dv-search{width:100%;order:3}.dv-two,.dv-feature-grid,.dv-analysis,.dv-info-grid,.dv-stats{grid-template-columns:1fr}.dv-content{padding:12px}.dv-hero{display:block}.dv-badge-top{display:inline-block;margin-top:12px}.dv-risk{grid-template-columns:1fr}}
      `}</style>

      <div className="dv-shell">
        <aside className="dv-side">
          <div className="dv-brand">
            <div className="dv-brand-mark"><Icon name="shield" size={20} /></div>
            <div>
              <div className="dv-brand-title">DeepVerify-X</div>
              <div className="dv-brand-sub">AI Content Provenance & Risk Analysis</div>
            </div>
          </div>

          {navGroups.map((group) => (
            <div className="dv-nav-group" key={group.title}>
              <div className="dv-nav-title">{group.title}</div>
              {group.items.map(([id, label, icon]) => (
                <button
                  key={id}
                  className={`dv-nav-btn ${activeNav === id ? "active" : ""}`}
                  onClick={() => handleNav(id)}
                >
                  <Icon name={icon} size={16} />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          ))}

          <div className="dv-nav-group">
            <div className="dv-nav-title">System</div>
            <button className={`dv-nav-btn ${activeNav === "history" ? "active" : ""}`} onClick={() => handleNav("history")}><Icon name="history" size={16}/><span>History</span></button>
            <button className={`dv-nav-btn ${activeNav === "reports" ? "active" : ""}`} onClick={() => handleNav("reports")}><Icon name="report" size={16}/><span>Reports</span></button>
            <button className="dv-nav-btn" onClick={() => handleNav("settings")}><Icon name="settings" size={16}/><span>Settings</span></button>
          </div>
        </aside>

        <div className="dv-main">
          <header className="dv-top">
            <div>
              <div className="dv-title">
                {activeNav === "scanner" ? "Security Scanner" : activeNav === "file-integrity" ? "File Integrity" : "DeepVerify-X"}
              </div>
              <div className="dv-bread">AI-powered verification workspace</div>
            </div>

            <div className="dv-top-right">
              <div className="dv-search">
                <Icon name="search" size={15}/>
                <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search files, reports, or history..." />
              </div>

              <div style={{ position: "relative" }}>
                <button className="dv-icon-btn" onClick={() => { setShowNotificationPanel((v) => !v); setShowProfileMenu(false); }}>
                  <Icon name="bell" size={16}/>
                  {history.length > 0 && <span className="dv-dot" />}
                </button>
                {showNotificationPanel && (
                  <div className="dv-drop dv-notif">
                    <strong style={{fontSize:11}}>Notifications</strong>
                    <div className="dv-reason" style={{marginTop:8}}><div className="dv-reason-icon"><Icon name="check" size={10}/></div><div>API connected and ready.</div></div>
                    <div className="dv-reason"><div className="dv-reason-icon"><Icon name="history" size={10}/></div><div>{history.length} analysis record(s) available.</div></div>
                  </div>
                )}
              </div>

              <div style={{ position: "relative" }}>
                <button className="dv-profile" onClick={() => { setShowProfileMenu((v) => !v); setShowNotificationPanel(false); }}>
                  <div className="dv-avatar">AS</div>
                  <div><div className="dv-pname">Anshika Singh</div><div className="dv-prole">Student</div></div>
                </button>
                {showProfileMenu && (
                  <div className="dv-drop">
                    <button onClick={() => {setShowSettingsModal(true); setShowProfileMenu(false);}}><Icon name="settings" size={14}/>Settings</button>
                    <button onClick={() => {setShowProfileMenu(false); handleNav("dashboard");}}><Icon name="grid" size={14}/>Dashboard</button>
                    <button onClick={() => {setShowProfileMenu(false); openScanner();}}><Icon name="scan" size={14}/>Security Scanner</button>
                  </div>
                )}
              </div>
            </div>
          </header>

          <main className="dv-content">
            {/* EXACT SCANNER RENDER BLOCK */}
            {activeNav === "scanner" && (
              <section className="dv-section scanner-shell">
                <SecurityScanner />
              </section>
            )}

            {activeNav === "ela" && (
              <section className="dv-section scanner-shell">
                <ELAAnalysis onCompleted={loadHistory} />
              </section>  
            )}

            {activeNav !== "scanner" && activeNav !== "ela" && (
              <>
                <section ref={dashboardRef} className="dv-section">
                  <div className="dv-hero">
                    <div>
                      <h1>Welcome to DeepVerify-X</h1>
                      <p>Verify. Analyze. Stay Informed. AI-powered multi-modal verification platform to inspect manipulated, synthetic and suspicious content.</p>
                    </div>
                    <span className="dv-badge-top">AI • FORENSICS • RISK</span>
                  </div>
                </section>

                <section className="dv-section">
                  <div className="dv-stats">
                    <div className="dv-stat"><div className="dv-stat-top"><span>Total Analyses</span><span className="dv-stat-icon"><Icon name="grid" size={14}/></span></div><div className="dv-stat-value">{totalAnalyses}</div><div className="dv-stat-meta">All verification modules</div></div>
                    <div className="dv-stat"><div className="dv-stat-top"><span>Low Risk</span><span className="dv-stat-icon"><Icon name="check" size={14}/></span></div><div className="dv-stat-value">{lowRiskCount}</div><div className="dv-progress low"><span style={{width:`${totalAnalyses ? Math.round(lowRiskCount/totalAnalyses*100) : 0}%`}}/></div><div className="dv-stat-meta">{totalAnalyses ? Math.round(lowRiskCount/totalAnalyses*100) : 0}% of total</div></div>
                    <div className="dv-stat"><div className="dv-stat-top"><span>Medium Risk</span><span className="dv-stat-icon"><Icon name="alert" size={14}/></span></div><div className="dv-stat-value">{mediumRiskCount}</div><div className="dv-progress medium"><span style={{width:`${totalAnalyses ? Math.round(mediumRiskCount/totalAnalyses*100) : 0}%`}}/></div><div className="dv-stat-meta">{totalAnalyses ? Math.round(mediumRiskCount/totalAnalyses*100) : 0}% of total</div></div>
                    <div className="dv-stat"><div className="dv-stat-top"><span>High Risk</span><span className="dv-stat-icon"><Icon name="alert" size={14}/></span></div><div className="dv-stat-value">{highRiskCount}</div><div className="dv-progress high"><span style={{width:`${totalAnalyses ? Math.round(highRiskCount/totalAnalyses*100) : 0}%`}}/></div><div className="dv-stat-meta">{totalAnalyses ? Math.round(highRiskCount/totalAnalyses*100) : 0}% of total</div></div>
                  </div>
                </section>

                <section className="dv-section">
                  <div className="dv-two">
                    <div className="dv-panel">
                      <h3>Overall Risk</h3>
                      <div className="dv-sub">Average risk score across stored analyses</div>
                      <div className="dv-risk">
                        <div className="dv-gauge"><div className="dv-gauge-inner"><div className="dv-gauge-score">{averageRisk}</div><div className="dv-gauge-label">AVG RISK</div></div></div>
                        <div className="dv-bars">
                          <div className="dv-bar"><span>Low</span><div className="dv-bar-track"><div className="dv-bar-fill low" style={{width:`${totalAnalyses ? lowRiskCount/totalAnalyses*100 : 0}%`}}/></div><strong>{totalAnalyses ? Math.round(lowRiskCount/totalAnalyses*100) : 0}%</strong></div>
                          <div className="dv-bar"><span>Medium</span><div className="dv-bar-track"><div className="dv-bar-fill medium" style={{width:`${totalAnalyses ? mediumRiskCount/totalAnalyses*100 : 0}%`}}/></div><strong>{totalAnalyses ? Math.round(mediumRiskCount/totalAnalyses*100) : 0}%</strong></div>
                          <div className="dv-bar"><span>High</span><div className="dv-bar-track"><div className="dv-bar-fill high" style={{width:`${totalAnalyses ? highRiskCount/totalAnalyses*100 : 0}%`}}/></div><strong>{totalAnalyses ? Math.round(highRiskCount/totalAnalyses*100) : 0}%</strong></div>
                        </div>
                      </div>
                    </div>
                    <div className="dv-panel">
                      <h3>Recent Activity</h3>
                      <div className="dv-sub">Latest forensic checks</div>
                      <div className="dv-activity">
                        {history.length === 0 ? <div className="dv-empty">No activity yet.</div> : history.slice(-4).reverse().map((item) => (
                          <div className="dv-activity-item" key={item.id}>
                            <div className="dv-activity-icon"><Icon name={item.file_type === "url" ? "link" : item.file_type === "scanner" ? "scan" : item.file_type === "qr" ? "qr" : item.file_type === "video" ? "video" : item.file_type === "audio" ? "audio" : item.file_type === "message" ? "message" : item.file_type === "document" ? "document" : "image"} size={14}/></div>
                            <div style={{minWidth:0,flex:1}}><div className="dv-activity-file">{item.filename || "Analysis"}</div><div className="dv-activity-time">{item.timestamp ? new Date(item.timestamp).toLocaleString() : "N/A"}</div></div>
                            <span className={`dv-badge ${riskLevel(item.risk_score)}`}>{verdictText(item.verdict)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>

                <section ref={verificationRef} className="dv-section">
                  <div className="dv-section-head">
                    <div><h2>{analysisType === "file-integrity" ? "File Integrity" : "Content Verification"}</h2><p>Select a verification module and run the appropriate forensic analysis.</p></div>
                    {analysisType !== "file-integrity" && <button className="dv-btn" onClick={openScanner}><Icon name="scan" size={13}/> Security Scanner</button>}
                  </div>

                  {analysisType === "file-integrity" ? (
                    <FileIntegrity />
                  ) : (
                    <div className="dv-verification">
                      <div className="dv-tabs">
                        {[["image","Image","image"],["video","Video","video"],["audio","Audio","audio"],["message","Message","message"],["document","Document","document"],["url","URL","link"],["qr","QR Code","qr"]].map(([id,label,icon]) => (
                          <button key={id} className={`dv-tab ${analysisType === id ? "active" : ""}`} onClick={() => handleAnalysisTypeChange(id)}><Icon name={icon} size={13}/>{label}</button>
                        ))}
                      </div>

                      <div className="dv-upload">
                        {analysisType === "message" ? (
                          <>
                            <textarea className="dv-textarea" value={typeof file === "string" ? file : ""} onChange={(e)=>{setFile(e.target.value);setResult(null);setSelectedHistory(null);setError("");}} placeholder="Enter the message you want to analyze..." />
                            <div className="dv-help">{typeof file === "string" ? file.length : 0} characters</div>
                          </>
                        ) : analysisType === "url" ? (
                          <>
                            <input className="dv-input" type="url" value={typeof file === "string" ? file : ""} onChange={(e)=>{setFile(e.target.value);setResult(null);setSelectedHistory(null);setError("");}} onKeyDown={(e)=>{if(e.key === "Enter" && !loading) analyzeURL();}} placeholder="https://example.com" />
                            <div className="dv-help">Include http:// or https://</div>
                          </>
                        ) : (
                          <>
                            <input className="dv-input" type="file" accept={analysisType === "image" ? ".jpg,.jpeg,.png,.webp" : analysisType === "video" ? ".mp4,.avi,.mov,.mkv,.webm" : analysisType === "audio" ? ".wav,.mp3,.m4a,.aac,.flac,.ogg,.webm" : analysisType === "document" ? ".pdf,.docx" : ".jpg,.jpeg,.png,.webp"} onChange={handleFileChange}/>
                            {file && typeof file !== "string" && <div className="dv-help">Selected: <strong>{file.name}</strong> • {bytes(file.size)}</div>}
                          </>
                        )}
                        <div className="dv-upload-actions">
                          <button className="dv-btn" onClick={clearCurrent}>Clear</button>
                          <button className="dv-btn primary" disabled={loading} onClick={analysisType === "image" ? analyzeImage : analysisType === "video" ? analyzeVideo : analysisType === "audio" ? analyzeAudio : analysisType === "message" ? analyzeMessage : analysisType === "document" ? analyzeDocument : analysisType === "qr" ? analyzeQR : analyzeURL}>{loading ? "Analyzing..." : analysisType === "image" ? "Analyze Image" : analysisType === "video" ? "Analyze Video" : analysisType === "audio" ? "Analyze Audio" : analysisType === "message" ? "Analyze Message" : analysisType === "document" ? "Analyze Document" : analysisType === "qr" ? "Scan QR Code" : "Verify URL"}</button>
                        </div>
                      </div>
                      {error && <div className="dv-error">{error}</div>}
                    </div>
                  )}
                </section>

                <section ref={historyRef} className="dv-section">
                  <div className="dv-section-head"><div><h2>Analysis History</h2><p>Previous verification and forensic reports.</p></div><div style={{display:"flex",gap:7}}><button className="dv-btn" disabled={historyLoading} onClick={loadHistory}><Icon name="refresh" size={12}/>{historyLoading ? "Refreshing..." : "Refresh"}</button><button className="dv-btn danger" disabled={!history.length || clearLoading} onClick={clearHistory}><Icon name="trash" size={12}/>{clearLoading ? "Clearing..." : "Clear All"}</button></div></div>
                  <div className="dv-table">
                    <div className="dv-head"><span>File</span><span>Type</span><span>Risk</span><span>Verdict</span><span>Date</span><span>Action</span></div>
                    {filteredHistory.length === 0 ? <div className="dv-empty">No analysis history available.</div> : filteredHistory.slice().reverse().map((item)=> (
                      <div className="dv-row" key={item.id}>
                        <span className="dv-file">{item.filename || "N/A"}</span><span>{item.file_type || "N/A"}</span><span>{item.risk_score ?? "N/A"}</span><span><span className={`dv-badge ${riskLevel(item.risk_score)}`}>{verdictText(item.verdict)}</span></span><span>{item.timestamp ? new Date(item.timestamp).toLocaleString() : "N/A"}</span>
                        <span className="dv-actions"><button className="dv-btn" onClick={()=>openHistory(item.id)} disabled={deleteLoading===item.id}>View</button><button className="dv-btn" onClick={()=>window.open(`${API_URL}/api/reports/${item.id}`,"_blank")} disabled={deleteLoading===item.id}><Icon name="download" size={11}/> PDF</button><button className="dv-btn danger" onClick={()=>deleteHistory(item.id)} disabled={deleteLoading===item.id}>{deleteLoading===item.id ? "Deleting..." : "Delete"}</button></span>
                      </div>
                    ))}
                  </div>
                </section>

                {activeReport && (
                  <section ref={reportRef} className="dv-section">
                    <div className="dv-result">
                      <div className="dv-result-head"><div><h2>{isScannerReport ? "Security Scanner Result" : isQRReport ? "QR Verification Result" : isURLReport ? "URL Verification Result" : isVideoReport ? "Video Verification Result" : isAudioReport ? "Audio Verification Result" : isMessageReport ? "Message Analysis Result" : isDocumentReport ? "Document Verification Result" : "Verification Result"}</h2><div className="dv-result-file">{activeReport?.verification?.filename || "Analysis result"}</div></div><span className={`dv-badge ${riskLevel(riskScore)}`}>{verdictText(verdict)}</span></div>

                      {(isScannerReport || isQRReport || isURLReport || isMessageReport || !isVideoReport && !isAudioReport && !isDocumentReport) && (
                        <div className="dv-score"><div className="dv-score-label">Risk Score</div><div className="dv-score-num">{riskScore}<span style={{fontSize:10,color:"#94a3b8",fontWeight:600}}> / 100</span></div><div className="dv-score-track"><span style={{width:`${riskScore}%`}}/></div></div>
                      )}

                      {isScannerReport && (
                        <>
                          <div className="dv-info-grid"><div className="dv-info"><small>Domain</small><strong>{scanner?.domain || "N/A"}</strong></div><div className="dv-info"><small>HTTPS</small><strong>{scanner?.https ? "Yes" : "No"}</strong></div><div className="dv-info"><small>IP Address URL</small><strong>{scanner?.ip_address_url ? "Detected" : "No"}</strong></div><div className="dv-info"><small>Shortened URL</small><strong>{scanner?.shortened_url ? "Detected" : "No"}</strong></div></div>
                          <div className="dv-analysis"><div className="dv-box"><h3>Security Indicators</h3><div className="dv-kv"><span>Excessive Subdomains</span><strong>{scanner?.excessive_subdomains ? "Detected" : "No"}</strong></div><div className="dv-kv"><span>Unusual Port</span><strong>{scanner?.unusual_port ? "Detected" : "No"}</strong></div><div className="dv-kv"><span>Scheme</span><strong>{scanner?.scheme?.toUpperCase() || "N/A"}</strong></div></div><div className="dv-box"><h3>Scanner Findings</h3>{(scanner?.findings || []).length ? scanner.findings.map((x,i)=><div className="dv-reason" key={i}><div className="dv-reason-icon"><Icon name="alert" size={10}/></div><div>{x}</div></div>) : <div className="dv-reason"><div className="dv-reason-icon"><Icon name="check" size={10}/></div><div>No suspicious scanner findings detected.</div></div>}</div></div>
                        </>
                      )}

                      {isQRReport && <div className="dv-info-grid"><div className="dv-info"><small>QR Detected</small><strong>{qr?.qr_detected ? "Yes" : "No"}</strong></div><div className="dv-info"><small>Content Type</small><strong>{qr?.content_type || "N/A"}</strong></div><div className="dv-info"><small>Decoded Content</small><strong>{qr?.decoded_content || "N/A"}</strong></div><div className="dv-info"><small>Image Size</small><strong>{qr?.image_width ?? "-"} × {qr?.image_height ?? "-"}</strong></div></div>}

                      {isURLReport && <div className="dv-analysis"><div className="dv-box"><h3>URL Structure</h3><div className="dv-kv"><span>Domain</span><strong>{url?.domain || "N/A"}</strong></div><div className="dv-kv"><span>Path</span><strong>{url?.path || "/"}</strong></div><div className="dv-kv"><span>HTTPS</span><strong>{url?.is_https ? "Yes" : "No"}</strong></div><div className="dv-kv"><span>Shortened</span><strong>{url?.is_shortened_url ? "Yes" : "No"}</strong></div></div><div className="dv-box"><h3>Suspicious Indicators</h3>{[...(url?.keyword_matches || []),...(url?.suspicious_path_keywords || []),...(url?.suspicious_query_keywords || [])].length ? [...(url?.keyword_matches || []),...(url?.suspicious_path_keywords || []),...(url?.suspicious_query_keywords || [])].map((x,i)=><div className="dv-reason" key={i}><div className="dv-reason-icon"><Icon name="alert" size={10}/></div><div>{x}</div></div>) : <div className="dv-reason"><div className="dv-reason-icon"><Icon name="check" size={10}/></div><div>No suspicious URL indicators detected.</div></div>}</div></div>}

                      {isVideoReport && <div className="dv-info-grid"><div className="dv-info"><small>Duration</small><strong>{video?.duration_seconds !== undefined ? `${video.duration_seconds} sec` : "N/A"}</strong></div><div className="dv-info"><small>Frame Count</small><strong>{video?.frame_count ?? "N/A"}</strong></div><div className="dv-info"><small>FPS</small><strong>{video?.fps ?? "N/A"}</strong></div><div className="dv-info"><small>Resolution</small><strong>{video?.resolution || "N/A"}</strong></div></div>}

                      {isAudioReport && <div className="dv-info-grid"><div className="dv-info"><small>Duration</small><strong>{audio?.duration_seconds !== undefined ? `${audio.duration_seconds} sec` : "N/A"}</strong></div><div className="dv-info"><small>Sample Rate</small><strong>{audio?.sample_rate !== undefined ? `${audio.sample_rate} Hz` : "N/A"}</strong></div><div className="dv-info"><small>Channels</small><strong>{audio?.channels ?? "N/A"}</strong></div><div className="dv-info"><small>Bitrate</small><strong>{audio?.bitrate_kbps !== undefined ? `${audio.bitrate_kbps} kbps` : "N/A"}</strong></div></div>}

                      {isMessageReport && <div className="dv-info-grid"><div className="dv-info"><small>Word Count</small><strong>{message?.word_count ?? 0}</strong></div><div className="dv-info"><small>Characters</small><strong>{message?.character_count ?? 0}</strong></div><div className="dv-info"><small>URLs Detected</small><strong>{message?.url_count ?? 0}</strong></div><div className="dv-info"><small>Emails Detected</small><strong>{message?.email_count ?? 0}</strong></div></div>}

                      {isDocumentReport && <div className="dv-info-grid"><div className="dv-info"><small>File Type</small><strong>{doc?.file_type || doc?.format || "N/A"}</strong></div><div className="dv-info"><small>File Size</small><strong>{doc?.file_size_bytes !== undefined ? bytes(doc.file_size_bytes) : "N/A"}</strong></div><div className="dv-info"><small>Metadata</small><strong>{doc?.has_metadata ? "Available" : "Not Available"}</strong></div><div className="dv-info"><small>Structure</small><strong>{doc?.structural_status || "N/A"}</strong></div></div>}

                      {!isScannerReport && !isQRReport && !isURLReport && !isVideoReport && !isAudioReport && !isMessageReport && !isDocumentReport && <div className="dv-analysis"><div className="dv-box"><h3>Metadata</h3><div className="dv-kv"><span>Format</span><strong>{forensics?.metadata?.format || "N/A"}</strong></div><div className="dv-kv"><span>EXIF</span><strong>{forensics?.metadata?.has_exif ? "Yes" : "No"}</strong></div><div className="dv-kv"><span>Width</span><strong>{forensics?.metadata?.width || "N/A"}</strong></div><div className="dv-kv"><span>Height</span><strong>{forensics?.metadata?.height || "N/A"}</strong></div></div><div className="dv-box"><h3>ELA & Noise</h3><div className="dv-kv"><span>JPEG Quality</span><strong>{forensics?.ela?.jpeg_quality ?? "N/A"}</strong></div><div className="dv-kv"><span>Mean Difference</span><strong>{forensics?.ela?.mean_difference ?? "N/A"}</strong></div><div className="dv-kv"><span>Mean Noise</span><strong>{forensics?.noise?.mean_noise ?? "N/A"}</strong></div><div className="dv-kv"><span>Noise Std</span><strong>{forensics?.noise?.noise_std ?? "N/A"}</strong></div></div></div>}

                      {heatmapUrl && <div className="dv-box" style={{marginTop:10}}><h3>ELA Heatmap</h3><img src={heatmapUrl} alt="ELA heatmap" style={{width:"100%",maxHeight:430,objectFit:"contain",borderRadius:8,background:"#09111d"}}/></div>}

                      {integrity && <div className="dv-integrity"><strong>SHA-256 File Integrity</strong><code className="dv-hash">{integrity.sha256 || "Hash unavailable"}</code></div>}

                      <div className="dv-reasons"><h3 style={{margin:0,fontSize:11}}>Risk Assessment</h3>{(risk?.reasons || message?.reasons || url?.reasons || qr?.reasons || scanner?.findings || []).length ? (risk?.reasons || message?.reasons || url?.reasons || qr?.reasons || scanner?.findings || []).map((x,i)=><div className="dv-reason" key={i}><div className="dv-reason-icon"><Icon name="alert" size={10}/></div><div>{x}</div></div>) : <div className="dv-reason"><div className="dv-reason-icon"><Icon name="check" size={10}/></div><div>No significant risk indicators detected.</div></div>}</div>
                    </div>
                  </section>
                )}
              </>
            )}

            <div style={{textAlign:"center",fontSize:9,color:"#94a3b8",padding:"8px 0 18px"}}>DeepVerify-X • AI content provenance & forensic analysis</div>
          </main>
        </div>
      </div>

      {showSettingsModal && (
        <div className="dv-modal-bg" onClick={() => setShowSettingsModal(false)}>
          <div className="dv-modal" onClick={(e) => e.stopPropagation()}>
            <div className="dv-modal-head"><h2>Settings</h2><button className="dv-close" onClick={()=>setShowSettingsModal(false)}><Icon name="close" size={14}/></button></div>
            <div className="dv-setting"><div><strong>Dark Forensic Theme</strong><span>Keep the dashboard in dark-inspired forensic styling.</span></div><button className={`dv-toggle ${darkThemeEnabled ? "on" : ""}`} onClick={()=>setDarkThemeEnabled(v=>!v)}><i/></button></div>
            <div className="dv-setting"><div><strong>Auto Scroll</strong><span>Scroll to fresh analysis results automatically.</span></div><button className={`dv-toggle ${autoScrollEnabled ? "on" : ""}`} onClick={()=>setAutoScrollEnabled(v=>!v)}><i/></button></div>
            <div className="dv-setting"><div><strong>API Endpoint</strong><span>{API_URL}</span></div><span className="dv-badge low">CONNECTED</span></div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
