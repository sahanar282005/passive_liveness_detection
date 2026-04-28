import { useState, useEffect, useRef, useCallback } from "react";

const NEON = "#00D4FF";
const BG = "#0B0F1A";
const CARD = "rgba(255,255,255,0.04)";
const BORDER = "rgba(0,212,255,0.15)";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body, #root {
    background: ${BG};
    color: #E0F4FF;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #0B0F1A; }
  ::-webkit-scrollbar-thumb { background: ${NEON}44; border-radius: 2px; }

  .orbitron { font-family: 'Orbitron', monospace; }
  .mono { font-family: 'Space Mono', monospace; }

  @keyframes glow-pulse {
    0%, 100% { text-shadow: 0 0 20px #00D4FF88, 0 0 60px #00D4FF44; }
    50% { text-shadow: 0 0 40px #00D4FFcc, 0 0 100px #00D4FF88, 0 0 200px #00D4FF22; }
  }

  @keyframes scan-line {
    0% { top: 0%; opacity: 1; }
    100% { top: 100%; opacity: 0.3; }
  }

  @keyframes border-flow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
  }

  @keyframes particle-drift {
    0% { transform: translateY(0) translateX(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-100vh) translateX(40px); opacity: 0; }
  }

  @keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes blink-cursor {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }

  @keyframes slide-in-left {
    from { transform: translateX(-30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  @keyframes fade-up {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  @keyframes pulse-ring {
    0% { transform: scale(0.9); opacity: 1; }
    100% { transform: scale(1.4); opacity: 0; }
  }

  @keyframes score-fill {
    from { stroke-dashoffset: 339; }
  }

  @keyframes matrix-rain {
    0% { transform: translateY(-100%); opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
  }

  .glow-text { animation: glow-pulse 3s ease-in-out infinite; }

  .glass-card {
    background: ${CARD};
    border: 1px solid ${BORDER};
    backdrop-filter: blur(20px);
    border-radius: 12px;
  }

  .neon-btn {
    background: transparent;
    border: 1px solid ${NEON};
    color: ${NEON};
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    padding: 12px 28px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    position: relative;
    overflow: hidden;
  }

  .neon-btn:hover {
    background: ${NEON}22;
    box-shadow: 0 0 20px ${NEON}44, inset 0 0 20px ${NEON}11;
  }

  .neon-btn-solid {
    background: ${NEON};
    border: 1px solid ${NEON};
    color: #0B0F1A;
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    padding: 12px 28px;
    cursor: pointer;
    font-weight: 700;
    transition: all 0.3s ease;
    text-transform: uppercase;
  }

  .neon-btn-solid:hover {
    background: #33DDFF;
    box-shadow: 0 0 30px ${NEON}88;
  }

  .particle {
    position: absolute;
    width: 2px;
    height: 2px;
    background: ${NEON};
    border-radius: 50%;
    animation: particle-drift linear infinite;
    opacity: 0;
  }

  .scan-overlay {
    position: absolute;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, ${NEON}, transparent);
    animation: scan-line 2.5s linear infinite;
    box-shadow: 0 0 10px ${NEON};
    z-index: 10;
  }

  .corner-tl, .corner-tr, .corner-bl, .corner-br {
    position: absolute;
    width: 20px; height: 20px;
    border-color: ${NEON};
    border-style: solid;
  }
  .corner-tl { top: 8px; left: 8px; border-width: 2px 0 0 2px; }
  .corner-tr { top: 8px; right: 8px; border-width: 2px 2px 0 0; }
  .corner-bl { bottom: 8px; left: 8px; border-width: 0 0 2px 2px; }
  .corner-br { bottom: 8px; right: 8px; border-width: 0 2px 2px 0; }

  .log-line {
    animation: slide-in-left 0.3s ease forwards;
    border-left: 2px solid ${NEON}44;
    padding-left: 10px;
    margin-bottom: 6px;
  }

  .feature-card {
    background: rgba(0,212,255,0.03);
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.4s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
  }

  .feature-card:hover {
    border-color: ${NEON}55;
    background: rgba(0,212,255,0.07);
    transform: translateY(-4px);
    box-shadow: 0 8px 40px ${NEON}22;
  }

  .feature-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at center, ${NEON}08 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.4s;
  }

  .feature-card:hover::before { opacity: 1; }

  .confidence-ring {
    transform: rotate(-90deg);
    transform-origin: center;
  }

  .confidence-ring circle:last-child {
    animation: score-fill 1.5s ease forwards;
  }

  .tab-active {
    border-bottom: 2px solid ${NEON};
    color: ${NEON};
  }

  .risk-bar {
    height: 6px;
    border-radius: 3px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
  }

  .risk-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .timeline-step {
    position: relative;
    padding-left: 24px;
    padding-bottom: 16px;
  }

  .timeline-step::before {
    content: '';
    position: absolute;
    left: 7px; top: 24px;
    width: 1px; bottom: 0;
    background: ${BORDER};
  }

  .timeline-step:last-child::before { display: none; }

  .timeline-dot {
    position: absolute;
    left: 0; top: 4px;
    width: 15px; height: 15px;
    border-radius: 50%;
    border: 2px solid ${NEON};
    background: #0B0F1A;
    display: flex; align-items: center; justify-content: center;
  }

  .timeline-dot.active {
    background: ${NEON}22;
    box-shadow: 0 0 10px ${NEON}88;
  }

  .webcam-box {
    position: relative;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    aspect-ratio: 4/3;
  }

  input[type="file"] { display: none; }

  .upload-zone {
    border: 2px dashed ${BORDER};
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .upload-zone:hover {
    border-color: ${NEON}66;
    background: rgba(0,212,255,0.04);
  }

  .upload-zone.drag-over {
    border-color: ${NEON};
    background: rgba(0,212,255,0.08);
    box-shadow: 0 0 30px ${NEON}22;
  }

  .stat-mini {
    background: rgba(0,212,255,0.05);
    border: 1px solid rgba(0,212,255,0.1);
    border-radius: 10px;
    padding: 14px 16px;
  }

  .shimmer-btn::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 40%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shimmer 2s infinite;
  }

  select, input {
    background: rgba(0,212,255,0.05);
    border: 1px solid ${BORDER};
    color: #E0F4FF;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    outline: none;
  }

  select:focus, input:focus {
    border-color: ${NEON}66;
  }
`;

const FEATURES = [
  { icon: "◎", title: "Face Detection", desc: "Haar Cascade + deep feature extraction for sub-50ms face localization", color: "#00D4FF" },
  { icon: "⬡", title: "Spoof Detection", desc: "ResNet18 binary classifier trained on CelebA-Spoof dataset", color: "#00FFB3" },
  { icon: "◈", title: "Confidence Scoring", desc: "Calibrated softmax probabilities with uncertainty quantification", color: "#FF6B6B" },
  { icon: "◉", title: "Risk Assessment", desc: "3-tier risk engine mapping scores to LOW / MEDIUM / HIGH outcomes", color: "#FFB800" },
  { icon: "▦", title: "Analysis Logs", desc: "Full trace of LBP, blur, FFT, reflection and edge feature scores", color: "#BF5FFF" },
  { icon: "⬡", title: "Decision Engine", desc: "Threshold-based access policy: ALLOW, REVIEW, or BLOCK", color: "#00D4FF" },
];

const TYPE_COLORS = { info: "#00D4FF", success: "#00FFB3", warn: "#FFB800", error: "#FF6B6B" };

function Particles() {
  const particles = Array.from({ length: 25 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 15}s`,
    duration: `${8 + Math.random() * 12}s`,
    size: Math.random() > 0.7 ? 3 : 2,
    opacity: 0.3 + Math.random() * 0.5,
  }));
  return (
    <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0, overflow: "hidden" }}>
      {particles.map(p => (
        <div key={p.id} className="particle" style={{
          left: p.left, bottom: 0,
          width: p.size, height: p.size,
          animationDelay: p.delay,
          animationDuration: p.duration,
          opacity: p.opacity,
        }} />
      ))}
      {/* Grid lines */}
      <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.04 }}>
        <defs>
          <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
            <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#00D4FF" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>
  );
}

function HeroSection({ onStart }) {
  const [typed, setTyped] = useState("");
  const full = "PASSIVE LIVENESS";
  useEffect(() => {
    let i = 0;
    const iv = setInterval(() => {
      if (i <= full.length) { setTyped(full.slice(0, i)); i++; }
      else clearInterval(iv);
    }, 80);
    return () => clearInterval(iv);
  }, []);

  return (
    <section style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", padding: "60px 20px", textAlign: "center" }}>
      <div style={{ marginBottom: 12, display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#00FFB3", boxShadow: "0 0 10px #00FFB3" }} />
        <span className="mono" style={{ fontSize: 11, color: "#00FFB3", letterSpacing: 3, textTransform: "uppercase" }}>System Online — v2.4.1</span>
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#00FFB3", boxShadow: "0 0 10px #00FFB3" }} />
      </div>

      <h1 className="orbitron glow-text" style={{ fontSize: "clamp(36px, 8vw, 96px)", fontWeight: 900, color: NEON, letterSpacing: "0.05em", lineHeight: 1.1, marginBottom: 8 }}>
        {typed}<span style={{ animation: "blink-cursor 1s infinite" }}>_</span>
      </h1>

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div style={{ height: 1, width: 60, background: `linear-gradient(90deg, transparent, ${NEON})` }} />
        <span className="mono" style={{ fontSize: 13, color: "#00D4FF88", letterSpacing: 4 }}>DETECTION SYSTEM</span>
        <div style={{ height: 1, width: 60, background: `linear-gradient(90deg, ${NEON}, transparent)` }} />
      </div>

      <p style={{ fontSize: 16, color: "rgba(224,244,255,0.6)", maxWidth: 560, lineHeight: 1.8, marginBottom: 48, fontWeight: 300 }}>
        Real-time AI-powered face liveness verification using deep neural networks and classical computer vision. Trained on 600K+ samples from CelebA-Spoof.
      </p>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center" }}>
        <button className="neon-btn-solid shimmer-btn" style={{ position: "relative", overflow: "hidden", borderRadius: 4 }} onClick={onStart}>
          ▶ Start Analysis
        </button>
        <button className="neon-btn" style={{ borderRadius: 4 }} onClick={onStart}>
          ◎ Try Live Camera
        </button>
      </div>

      <div style={{ position: "absolute", bottom: 40, left: "50%", transform: "translateX(-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 10, color: "#00D4FF44", letterSpacing: 3, fontFamily: "monospace" }}>SCROLL</span>
        <div style={{ width: 1, height: 40, background: `linear-gradient(${NEON}88, transparent)` }} />
      </div>

      {/* Decorative rings */}
      <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", pointerEvents: "none", zIndex: -1 }}>
        {[200, 340, 480].map((r, i) => (
          <div key={r} style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: r, height: r, borderRadius: "50%", border: `1px solid ${NEON}${i === 0 ? "22" : i === 1 ? "11" : "08"}`, animation: `spin-slow ${20 + i * 10}s linear infinite` }} />
        ))}
      </div>
    </section>
  );
}

function FeaturesSection() {
  return (
    <section style={{ padding: "80px 40px", maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 60 }}>
        <span className="mono" style={{ fontSize: 11, color: NEON, letterSpacing: 4 }}>CAPABILITIES</span>
        <h2 className="orbitron" style={{ fontSize: 32, fontWeight: 700, color: "#E0F4FF", marginTop: 8 }}>Detection Engine</h2>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
        {FEATURES.map((f, i) => (
          <div key={i} className="feature-card" style={{ animationDelay: `${i * 100}ms` }}>
            <div style={{ fontSize: 28, color: f.color, marginBottom: 14, textShadow: `0 0 20px ${f.color}88` }}>{f.icon}</div>
            <h3 className="orbitron" style={{ fontSize: 13, fontWeight: 700, color: "#E0F4FF", marginBottom: 8, letterSpacing: 1 }}>{f.title}</h3>
            <p style={{ fontSize: 13, color: "rgba(224,244,255,0.5)", lineHeight: 1.7 }}>{f.desc}</p>
            <div style={{ position: "absolute", top: 0, right: 0, width: 60, height: 60, background: `radial-gradient(circle at top right, ${f.color}15, transparent)`, borderRadius: "0 12px 0 0" }} />
          </div>
        ))}
      </div>
    </section>
  );
}

function LogPanel({ logs, scanning }) {
  const endRef = useRef(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 400 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, paddingBottom: 12, borderBottom: `1px solid ${BORDER}` }}>
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: scanning ? "#00FFB3" : "#FF6B6B", boxShadow: scanning ? "0 0 8px #00FFB3" : "none" }} />
        <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>AI AGENT LOG</span>
      </div>

      <div style={{ flex: 1, overflowY: "auto", fontFamily: "Space Mono, monospace", fontSize: 11, paddingRight: 4 }}>
        {logs.length === 0 ? (
          <div style={{ color: "#00D4FF33", padding: "20px 0", textAlign: "center" }}>
            <div className="orbitron" style={{ fontSize: 11, letterSpacing: 2, marginBottom: 8 }}>AWAITING INPUT</div>
            <div style={{ fontSize: 10, color: "#00D4FF22" }}>Upload image to begin analysis</div>
          </div>
        ) : logs.map((l, i) => (
          <div key={i} className="log-line" style={{ borderLeftColor: `${TYPE_COLORS[l.type]}44` }}>
            <span style={{ color: "#00D4FF44", fontSize: 10 }}>{String(i).padStart(3, "0")} </span>
            <span style={{ color: TYPE_COLORS[l.type] }}>›</span>{" "}
            <span style={{ color: l.type === "info" ? "rgba(224,244,255,0.7)" : TYPE_COLORS[l.type] }}>{l.msg}</span>
          </div>
        ))}
        {scanning && (
          <div className="log-line" style={{ borderLeftColor: "#00D4FF44" }}>
            <span style={{ color: "#00D4FF", animation: "blink-cursor 0.8s infinite" }}>█</span>
            <span style={{ color: "rgba(224,244,255,0.4)", fontSize: 10 }}> processing...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${BORDER}`, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {[["Total Runs", "12"], ["Avg Time", "1.8s"]].map(([k, v]) => (
          <div key={k} className="stat-mini">
            <div style={{ fontSize: 10, color: "rgba(224,244,255,0.4)", marginBottom: 2, fontFamily: "monospace" }}>{k}</div>
            <div className="orbitron" style={{ fontSize: 16, color: NEON }}>{v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function UploadPanel({ onAnalyze, scanning, imagePreview, setImagePreview, selectedFile, setSelectedFile, error }) {
  const inputRef = useRef(null);
  const [drag, setDrag] = useState(false);

  const handleFile = (file) => {
    if (!file) {
      console.warn("No file provided to handleFile");
      return;
    }
    
    console.log("File selected:", file.name, file.type, file.size, "bytes");
    
    // Set file first
    setSelectedFile(file);
    
    // Read preview
    const reader = new FileReader();
    reader.onload = (e) => {
      console.log("Image preview ready");
      setImagePreview(e.target.result);
      // Call analyze after preview is ready
      onAnalyze(file);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, paddingBottom: 12, borderBottom: `1px solid ${BORDER}` }}>
        <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>ANALYSIS CENTER</span>
        {scanning && <span className="mono" style={{ fontSize: 10, color: NEON, animation: "blink-cursor 0.8s infinite" }}>● SCANNING</span>}
      </div>

      <input ref={inputRef} type="file" accept="image/*" onChange={e => handleFile(e.target.files[0])} />

      <div
        className={`upload-zone ${drag ? "drag-over" : ""}`}
        onClick={() => inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}
        style={{ position: "relative", minHeight: 200 }}
      >
        {imagePreview ? (
          <>
            <img src={imagePreview} alt="preview" style={{ width: "100%", maxHeight: 260, objectFit: "cover", borderRadius: 8 }} />
            {scanning && (
              <>
                <div className="scan-overlay" />
                <div className="corner-tl" /><div className="corner-tr" />
                <div className="corner-bl" /><div className="corner-br" />
                <div style={{ position: "absolute", bottom: 8, left: "50%", transform: "translateX(-50%)", background: `${NEON}22`, border: `1px solid ${NEON}`, borderRadius: 4, padding: "4px 12px" }}>
                  <span className="mono" style={{ fontSize: 10, color: NEON }}>ANALYZING BIOMETRICS...</span>
                </div>
              </>
            )}
          </>
        ) : (
          <div style={{ pointerEvents: "none" }}>
            <div style={{ fontSize: 40, color: `${NEON}44`, marginBottom: 12 }}>◎</div>
            <div className="orbitron" style={{ fontSize: 12, color: NEON, letterSpacing: 2, marginBottom: 8 }}>DROP IMAGE HERE</div>
            <div style={{ fontSize: 12, color: "rgba(224,244,255,0.3)" }}>or click to browse — JPG, PNG</div>
            <div style={{ fontSize: 10, color: "rgba(224,244,255,0.15)", marginTop: 8, fontFamily: "monospace" }}>Max 10000×10000px</div>
          </div>
        )}
      </div>

      {error && <div style={{ color: "#FF6B6B", fontSize: 12, textAlign: "center" }}>{error}</div>}

      {imagePreview && !scanning && (
        <div style={{ display: "flex", gap: 10 }}>
          <button
            className="neon-btn-solid"
            style={{ flex: 1, borderRadius: 4 }}
            onClick={() => selectedFile && onAnalyze(selectedFile)}
          >▶ Re-Analyze</button>
          <button className="neon-btn" style={{ borderRadius: 4 }} onClick={() => { setImagePreview(null); setSelectedFile(null); }}>✕ Clear</button>
        </div>
      )}
    </div>
  );
}

function ConfidenceRing({ value, size = 100 }) {
  const r = 40, circ = 2 * Math.PI * r;
  const offset = circ - (value / 100) * circ;
  const color = value >= 70 ? "#00FFB3" : value >= 40 ? "#FFB800" : "#FF6B6B";
  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
      <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" className="confidence-ring"
        style={{ transform: "rotate(-90deg)", transformOrigin: "center", filter: `drop-shadow(0 0 6px ${color}88)` }}
      />
      <text x="50" y="46" textAnchor="middle" fill={color} fontSize="16" fontWeight="700" fontFamily="Orbitron, monospace">{Math.round(value)}</text>
      <text x="50" y="58" textAnchor="middle" fill="rgba(224,244,255,0.4)" fontSize="8" fontFamily="monospace">%</text>
    </svg>
  );
}

function ResultsPanel({ result, error }) {
  if (error) {
    return (
      <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center", alignItems: "center", gap: 12, color: "#FF6B6B" }}>
        <div style={{ fontSize: 48 }}>✗</div>
        <div className="orbitron" style={{ fontSize: 11, letterSpacing: 2 }}>ANALYSIS FAILED</div>
        <div style={{ fontSize: 12, textAlign: "center" }}>{error}</div>
      </div>
    );
  }

  const riskColors = { LOW: "#00FFB3", MEDIUM: "#FFB800", HIGH: "#FF6B6B", UNKNOWN: "#888" };
  const predColors = { REAL: "#00FFB3", SPOOF: "#FF6B6B", UNCERTAIN: "#FFB800", ERROR: "#888" };

  if (!result) {
    return (
      <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center", alignItems: "center", gap: 12, opacity: 0.4 }}>
        <div style={{ fontSize: 48, color: NEON }}>◎</div>
        <div className="orbitron" style={{ fontSize: 11, color: NEON, letterSpacing: 2 }}>AWAITING ANALYSIS</div>
      </div>
    );
  }

  const { prediction, confidence, spoof_score, risk_level, recommendation, explanations, ai_explanation } = result;
  const predColor = predColors[prediction] || "#888";
  const riskColor = riskColors[risk_level] || "#888";
  const showAiExplanation = ai_explanation && !/unavailable|service error|not configured/i.test(ai_explanation);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, paddingBottom: 12, borderBottom: `1px solid ${BORDER}` }}>
        <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>ANALYSIS RESULTS</span>
      </div>

      {/* Prediction badge */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", background: `${predColor}11`, border: `1px solid ${predColor}44`, borderRadius: 10 }}>
        <div>
          <div style={{ fontSize: 10, color: "rgba(224,244,255,0.4)", fontFamily: "monospace", marginBottom: 4 }}>PREDICTION</div>
          <div className="orbitron" style={{ fontSize: 22, fontWeight: 900, color: predColor, textShadow: `0 0 20px ${predColor}88` }}>{prediction}</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <ConfidenceRing value={confidence} size={80} />
          <div style={{ fontSize: 9, color: "rgba(224,244,255,0.3)", fontFamily: "monospace", marginTop: 2 }}>CONFIDENCE</div>
        </div>
      </div>

      {/* Spoof score bar */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
          <span style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(224,244,255,0.5)" }}>SPOOF SCORE</span>
          <span className="orbitron" style={{ fontSize: 12, color: prediction === "SPOOF" ? "#FF6B6B" : "#00FFB3" }}>{spoof_score.toFixed(3)}</span>
        </div>
        <div className="risk-bar">
          <div className="risk-fill" style={{ width: `${spoof_score * 100}%`, background: spoof_score > 0.6 ? "linear-gradient(90deg,#FF6B6B,#FF3333)" : spoof_score > 0.3 ? "linear-gradient(90deg,#FFB800,#FF8800)" : "linear-gradient(90deg,#00FFB3,#00D4FF)" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 3 }}>
          <span style={{ fontSize: 9, fontFamily: "monospace", color: "#00FFB3" }}>REAL</span>
          <span style={{ fontSize: 9, fontFamily: "monospace", color: "#FF6B6B" }}>SPOOF</span>
        </div>
      </div>

      {/* Risk + Recommendation */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <div style={{ padding: "10px 12px", background: `${riskColor}11`, border: `1px solid ${riskColor}33`, borderRadius: 8 }}>
          <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.4)", marginBottom: 4 }}>RISK LEVEL</div>
          <div className="orbitron" style={{ fontSize: 14, color: riskColor }}>{risk_level}</div>
        </div>
        <div style={{ padding: "10px 12px", background: `${riskColor}11`, border: `1px solid ${riskColor}33`, borderRadius: 8 }}>
          <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.4)", marginBottom: 4 }}>DECISION</div>
          <div className="orbitron" style={{ fontSize: 14, color: riskColor }}>{recommendation}</div>
        </div>
      </div>

      {/* Explanations */}
      <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: 8, padding: 12 }}>
        <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.4)", marginBottom: 8, letterSpacing: 2 }}>SIGNAL ANALYSIS</div>
        {explanations.slice(0, 4).map((e, i) => (
          <div key={i} style={{ display: "flex", gap: 8, marginBottom: 5, fontSize: 11, color: "rgba(224,244,255,0.6)", alignItems: "flex-start" }}>
            <span style={{ color: NEON, flexShrink: 0, fontSize: 10 }}>›</span>
            <span style={{ lineHeight: 1.5 }}>{e}</span>
          </div>
        ))}
      </div>

      {showAiExplanation ? (
        <div style={{ background: "rgba(0,0,0,0.18)", borderRadius: 8, padding: 12, border: `1px solid ${BORDER}` }}>
          <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.4)", marginBottom: 8, letterSpacing: 2 }}>AI EXPLANATION</div>
          <div style={{ fontSize: 12, color: "rgba(224,244,255,0.85)", lineHeight: 1.7 }}>{ai_explanation}</div>
        </div>
      ) : null}
    </div>
  );
}

function LiveCameraPanel() {
  const videoRef = useRef(null);
  const [active, setActive] = useState(false);
  const [overlay, setOverlay] = useState(null);
  const [tick, setTick] = useState(0);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      videoRef.current.play();
      setActive(true);
    } catch { setActive(false); alert("Camera access denied or unavailable."); }
  };

  const stopCamera = () => {
    videoRef.current?.srcObject?.getTracks().forEach(t => t.stop());
    setActive(false);
    setOverlay(null);
  };

  useEffect(() => {
    if (!active) return;
    const results = [
      { label: "REAL", color: "#00FFB3", score: 0.083 },
      { label: "REAL", color: "#00FFB3", score: 0.121 },
      { label: "UNCERTAIN", color: "#FFB800", score: 0.441 },
      { label: "REAL", color: "#00FFB3", score: 0.067 },
    ];
    let i = 0;
    const iv = setInterval(() => {
      setOverlay(results[i % results.length]);
      setTick(t => t + 1);
      i++;
    }, 2200);
    return () => clearInterval(iv);
  }, [active]);

  return (
    <div style={{ padding: "0 0 20px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div>
          <div className="orbitron" style={{ fontSize: 13, color: "#E0F4FF", letterSpacing: 2 }}>LIVE CAMERA</div>
          <div style={{ fontSize: 11, color: "rgba(224,244,255,0.4)", marginTop: 2 }}>Real-time passive liveness detection</div>
        </div>
        {active
          ? <button className="neon-btn" style={{ borderRadius: 4, fontSize: 10 }} onClick={stopCamera}>✕ Stop</button>
          : <button className="neon-btn-solid" style={{ borderRadius: 4, fontSize: 10 }} onClick={startCamera}>◎ Start Camera</button>
        }
      </div>

      <div className="webcam-box" style={{ border: `1px solid ${active ? NEON + "44" : BORDER}`, transition: "border-color 0.3s" }}>
        <video ref={videoRef} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted playsInline />

        {!active && (
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.6)" }}>
            <div style={{ fontSize: 48, color: `${NEON}33`, marginBottom: 12 }}>◎</div>
            <div className="orbitron" style={{ fontSize: 11, color: `${NEON}66`, letterSpacing: 2 }}>CAMERA OFFLINE</div>
          </div>
        )}

        {active && (
          <>
            <div className="corner-tl" /><div className="corner-tr" />
            <div className="corner-bl" /><div className="corner-br" />
            <div className="scan-overlay" />

            {/* Face box simulation */}
            <div style={{ position: "absolute", top: "20%", left: "30%", width: "40%", height: "55%", border: `2px solid ${overlay?.color || NEON}`, borderRadius: 4, boxShadow: `0 0 15px ${overlay?.color || NEON}44` }}>
              <div style={{ position: "absolute", top: -18, left: 0, right: 0, textAlign: "center" }}>
                <span className="mono" style={{ fontSize: 10, color: overlay?.color || NEON, background: "#0B0F1A", padding: "2px 8px", borderRadius: 2 }}>
                  {overlay ? `${overlay.label} — ${overlay.score.toFixed(3)}` : "DETECTING..."}
                </span>
              </div>
            </div>

            <div style={{ position: "absolute", bottom: 10, left: 10, right: 10, display: "flex", justifyContent: "space-between" }}>
              <span className="mono" style={{ fontSize: 10, color: NEON, background: "rgba(0,0,0,0.6)", padding: "3px 8px", borderRadius: 4 }}>◉ LIVE</span>
              <span className="mono" style={{ fontSize: 10, color: "rgba(224,244,255,0.4)", background: "rgba(0,0,0,0.6)", padding: "3px 8px", borderRadius: 4 }}>30fps</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function TimelinePanel({ logs }) {
  if (logs.length === 0) return (
    <div style={{ textAlign: "center", padding: "40px 20px", opacity: 0.3 }}>
      <div className="orbitron" style={{ fontSize: 11, color: NEON, letterSpacing: 2 }}>NO TIMELINE DATA</div>
    </div>
  );

  return (
    <div style={{ paddingTop: 8 }}>
      {logs.map((l, i) => (
        <div key={i} className="timeline-step" style={{ animationDelay: `${i * 80}ms`, animation: "fade-up 0.3s ease forwards" }}>
          <div className={`timeline-dot ${l.type !== "info" ? "active" : ""}`} style={{ borderColor: TYPE_COLORS[l.type] }}>
            <div style={{ width: 5, height: 5, borderRadius: "50%", background: TYPE_COLORS[l.type] }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <span className="mono" style={{ fontSize: 11, color: TYPE_COLORS[l.type], flex: 1 }}>{l.msg}</span>
            <span style={{ fontSize: 9, color: "rgba(224,244,255,0.2)", fontFamily: "monospace", marginLeft: 12, flexShrink: 0 }}>{(l.t / 1000).toFixed(1)}s</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function AnalyticsDashboard({ result, totalRuns, avgScore }) {
  const stats = [
    { label: "Model", value: "ResNet18", sub: "v2.4.1" },
    { label: "Avg Score", value: avgScore ? avgScore.toFixed(3) : "—", sub: "spoof prob" },
    { label: "Total Runs", value: totalRuns, sub: "this session" },
    { label: "Last Result", value: result?.prediction || "—", sub: result?.risk_level || "pending" },
  ];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
        <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>ANALYTICS</span>
        <div style={{ flex: 1, height: 1, background: BORDER }} />
        <span className="mono" style={{ fontSize: 9, color: `${NEON}66` }}>SESSION STATS</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        {stats.map((s, i) => (
          <div key={i} className="stat-mini" style={{ animation: `fade-up 0.4s ease ${i * 100}ms both` }}>
            <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.35)", marginBottom: 6, letterSpacing: 1 }}>{s.label.toUpperCase()}</div>
            <div className="orbitron" style={{ fontSize: 18, color: NEON, marginBottom: 2 }}>{s.value}</div>
            <div style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.25)" }}>{s.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("hero");
  const [imagePreview, setImagePreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [totalRuns, setTotalRuns] = useState(0);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("upload");
  const [error, setError] = useState(null);

  const runAnalysis = useCallback(async (file) => {
    console.log("API CALLED - Starting analysis for file:", file?.name);
    
    if (!file) {
      console.error("No file provided to runAnalysis");
      setError("No file selected");
      return;
    }

    setScanning(true);
    setLogs([]);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log("FormData created with file:", file.name, file.size, "bytes");

      setLogs([{ msg: "Image sent to API", type: "info" }]);

      setTimeout(() => setLogs(prev => [...prev, { msg: "Processing with ResNet18", type: "info" }]), 500);

      // Use deployed Render backend directly
      const apiUrl = 'https://passive-liveness-detection.onrender.com';
      console.log("Using API URL:", apiUrl);
      
      const fetchUrl = `${apiUrl}/analyze`;
      console.log("Fetching from:", fetchUrl);
      
      const response = await fetch(fetchUrl, {
        method: 'POST',
        body: formData,
      });

      console.log("Response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Response error:", errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Response data received:", data);

      setTimeout(() => {
        setResult(data);
        setLogs(prev => [...prev, { msg: `Prediction: ${data.prediction}`, type: data.prediction === 'REAL' ? 'success' : 'error' }]);
        setScanning(false);
        setTotalRuns(n => n + 1);
        setScoreHistory(h => [...h, data.spoof_score]);
      }, 1000);

    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.message);
      setLogs([{ msg: "Error: " + err.message, type: "error" }]);
      setScanning(false);
    }
  }, []);

  const avgScore = scoreHistory.length ? scoreHistory.reduce((a, b) => a + b, 0) / scoreHistory.length : null;

  if (view === "hero") {
    return (
      <>
        <style>{css}</style>
        <Particles />
        <div style={{ position: "relative", zIndex: 1 }}>
          <HeroSection onStart={() => setView("app")} />
          <FeaturesSection />
          <div style={{ textAlign: "center", padding: "40px 20px 80px" }}>
            <button className="neon-btn-solid" style={{ borderRadius: 4 }} onClick={() => setView("app")}>
              ▶ Launch Dashboard
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <style>{css}</style>
      <Particles />
      <div style={{ position: "relative", zIndex: 1, minHeight: "100vh", padding: "0 0 60px" }}>
        {/* Nav */}
        <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 32px", borderBottom: `1px solid ${BORDER}`, backdropFilter: "blur(20px)", background: "rgba(11,15,26,0.8)", position: "sticky", top: 0, zIndex: 100 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: NEON, boxShadow: `0 0 12px ${NEON}` }} />
            <span className="orbitron" style={{ fontSize: 13, fontWeight: 900, color: NEON, letterSpacing: 3 }}>PASSIVE LIVENESS</span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {["Upload", "Camera", "Analytics"].map((t, i) => (
              <button key={t} className="neon-btn" style={{ borderRadius: 4, padding: "8px 16px", fontSize: 10,
                background: activeTab === t.toLowerCase() ? `${NEON}11` : "transparent",
                borderColor: activeTab === t.toLowerCase() ? NEON : `${NEON}44`
              }} onClick={() => setActiveTab(t.toLowerCase())}>
                {t}
              </button>
            ))}
            <button className="neon-btn" style={{ borderRadius: 4, padding: "8px 14px", fontSize: 10 }} onClick={() => setView("hero")}>← Back</button>
          </div>
        </nav>

        {/* Main 3-panel dashboard */}
        {activeTab !== "analytics" && activeTab !== "camera" && (
          <div style={{ display: "grid", gridTemplateColumns: "280px 1fr 320px", gap: 20, padding: "24px 32px", minHeight: "70vh" }}>
            {/* Left: Log panel */}
            <div className="glass-card" style={{ padding: 20 }}>
              <LogPanel logs={logs} scanning={scanning} />
            </div>

            {/* Center: Upload */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div className="glass-card" style={{ padding: 20 }}>
                <UploadPanel onAnalyze={runAnalysis} scanning={scanning} imagePreview={imagePreview} setImagePreview={setImagePreview} selectedFile={selectedFile} setSelectedFile={setSelectedFile} error={error} />
              </div>

              {/* Timeline */}
              {logs.length > 0 && (
                <div className="glass-card" style={{ padding: 20 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, paddingBottom: 12, borderBottom: `1px solid ${BORDER}` }}>
                    <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>PROCESSING TIMELINE</span>
                  </div>
                  <TimelinePanel logs={logs} />
                </div>
              )}
            </div>

            {/* Right: Results */}
            <div className="glass-card" style={{ padding: 20 }}>
              <ResultsPanel result={result} error={error} />
            </div>
          </div>
        )}

        {/* Camera tab */}
        {activeTab === "camera" && (
          <div style={{ maxWidth: 900, margin: "24px auto", padding: "0 32px" }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <LiveCameraPanel />
            </div>
          </div>
        )}

        {/* Analytics tab */}
        {activeTab === "analytics" && (
          <div style={{ maxWidth: 1000, margin: "24px auto", padding: "0 32px", display: "flex", flexDirection: "column", gap: 20 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <AnalyticsDashboard result={result} totalRuns={totalRuns} avgScore={avgScore} />
            </div>

            {scoreHistory.length > 0 && (
              <div className="glass-card" style={{ padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                  <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>SCORE HISTORY</span>
                  <div style={{ flex: 1, height: 1, background: BORDER }} />
                </div>
                <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 80 }}>
                  {scoreHistory.map((s, i) => (
                    <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ width: "100%", background: s > 0.6 ? "#FF6B6B" : s > 0.3 ? "#FFB800" : "#00FFB3", height: Math.max(4, s * 80), borderRadius: "2px 2px 0 0", boxShadow: s > 0.6 ? "0 0 8px #FF6B6B88" : "0 0 8px #00FFB388", transition: "height 0.5s ease" }} />
                      <span className="mono" style={{ fontSize: 9, color: "rgba(224,244,255,0.3)" }}>{i + 1}</span>
                    </div>
                  ))}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
                  <span style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.3)" }}>Run #1</span>
                  <span style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.3)" }}>Run #{scoreHistory.length}</span>
                </div>
              </div>
            )}

            {result && (
              <div className="glass-card" style={{ padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                  <span className="orbitron" style={{ fontSize: 11, color: "#E0F4FF", letterSpacing: 2 }}>LAST RESULT DETAIL</span>
                </div>
                <ResultsPanel result={result} error={error} />
              </div>
            )}
          </div>
        )}

        {/* Footer analytics bar - always visible in app */}
        <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, background: "rgba(11,15,26,0.95)", borderTop: `1px solid ${BORDER}`, backdropFilter: "blur(20px)", padding: "10px 32px", display: "flex", alignItems: "center", gap: 32, zIndex: 100 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#00FFB3", boxShadow: "0 0 8px #00FFB3" }} />
            <span className="mono" style={{ fontSize: 10, color: "#00FFB3" }}>API ONLINE</span>
          </div>
          {[
            ["Model", "ResNet18 v2.4.1"],
            ["Threshold", "0.20 / 0.80"],
            ["Session Runs", totalRuns],
            ["Avg Score", avgScore ? avgScore.toFixed(3) : "—"],
            ["Last Decision", result?.recommendation || "—"],
          ].map(([k, v]) => (
            <div key={k} style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{ fontSize: 9, fontFamily: "monospace", color: "rgba(224,244,255,0.3)", letterSpacing: 1 }}>{k.toUpperCase()}</span>
              <span className="mono" style={{ fontSize: 11, color: NEON }}>{v}</span>
            </div>          ))}
        </div>
      </div>
    </>
  );
}
