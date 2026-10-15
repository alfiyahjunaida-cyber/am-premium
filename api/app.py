#!/usr/bin/env python3
# api/app.py — Email Proxy (Send + Verify) — Vercel serverless
from flask import Flask, request, jsonify, render_template_string
import requests
from urllib.parse import quote

app = Flask(__name__)

TIMEOUT = 15


HTML = r'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>📧 Email Tool</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  :root {
    --bg: #050309;
    --glass: rgba(22, 16, 34, 0.7);
    --border: rgba(168, 85, 247, 0.15);
    --border-2: rgba(168, 85, 247, 0.3);
    --text: #ece7f5;
    --text-dim: #9a90ad;
    --text-dim-2: #6b6178;
    --accent: #a855f7;
    --accent-2: #ec4899;
    --green: #10b981;
    --red: #ef4444;
    --blue: #3b82f6;
  }
  html, body {
    min-height: 100vh;
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 50% at 20% 0%, rgba(168,85,247,0.25), transparent 50%),
      radial-gradient(ellipse 60% 40% at 80% 10%, rgba(236,72,153,0.18), transparent 50%),
      radial-gradient(ellipse 70% 60% at 50% 100%, rgba(139,92,246,0.15), transparent 60%);
    z-index: -1;
  }
  body::after {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(168,85,247,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(168,85,247,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: -1;
    mask-image: radial-gradient(ellipse 70% 70% at 50% 0%, black, transparent 70%);
    -webkit-mask-image: radial-gradient(ellipse 70% 70% at 50% 0%, black, transparent 70%);
  }
  .container { max-width: 980px; margin: 0 auto; padding: 30px 20px 60px; }

  .header { text-align: center; padding: 20px 0 40px; }
  .logo-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px;
    background: var(--glass);
    border: 1px solid var(--border-2);
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(168,85,247,0.2);
  }
  .logo-badge .pulse {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent);
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
  }
  .title {
    font-size: clamp(32px, 6vw, 48px);
    font-weight: 900;
    letter-spacing: -1.5px;
    line-height: 1;
    background: linear-gradient(135deg, #fff 0%, var(--accent) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 30px rgba(168,85,247,0.4));
    margin-bottom: 12px;
  }
  .subtitle {
    color: var(--text-dim);
    font-size: 14px;
    font-weight: 500;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  @media (max-width: 720px) {
    .grid { grid-template-columns: 1fr; }
  }

  .card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 26px;
    backdrop-filter: blur(20px) saturate(1.2);
    -webkit-backdrop-filter: blur(20px) saturate(1.2);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
  }
  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent-2), transparent);
    opacity: 0.6;
  }

  .card-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 20px;
    letter-spacing: 0.3px;
  }
  .card-title .icon {
    width: 36px; height: 36px;
    border-radius: 11px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    box-shadow: 0 6px 20px rgba(168,85,247,0.4);
    flex-shrink: 0;
  }

  label {
    display: block;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-dim);
    margin-bottom: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  input {
    width: 100%;
    padding: 15px 16px;
    background: rgba(0,0,0,0.35);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    color: var(--text);
    font-size: 14px;
    font-family: 'JetBrains Mono', monospace;
    outline: none;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 14px;
  }
  input:focus {
    border-color: var(--accent);
    background: rgba(168,85,247,0.06);
    box-shadow: 0 0 0 4px rgba(168,85,247,0.12), 0 0 30px rgba(168,85,247,0.15);
  }
  input::placeholder { color: var(--text-dim-2); font-family: 'Inter', sans-serif; }

  button {
    width: 100%;
    padding: 15px 20px;
    border: none;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    font-family: inherit;
    letter-spacing: 0.5px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: white;
    box-shadow: 0 8px 30px rgba(168,85,247,0.4);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  button:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(168,85,247,0.55); }
  button:active { transform: translateY(0); }
  button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  .log {
    margin-top: 16px;
    background: #030207;
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 14px;
    height: 240px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.7;
    color: #d1fae5;
    white-space: pre-wrap;
    word-break: break-all;
  }
  .log::-webkit-scrollbar { width: 6px; }
  .log::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--accent), var(--accent-2));
    border-radius: 3px;
  }
  .log .line { display: block; padding: 2px 0; animation: lineIn 0.2s ease; }
  @keyframes lineIn { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; } }
  .log .line.ok { color: #6ee7b7; }
  .log .line.err { color: #fca5a5; }
  .log .line.info { color: #93c5fd; }
  .log .empty { color: var(--text-dim-2); font-style: italic; text-align: center; padding: 60px 20px; }

  .footer {
    text-align: center;
    color: var(--text-dim-2);
    font-size: 12px;
    padding: 40px 0 10px;
    letter-spacing: 0.3px;
  }
  .footer b {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
  }

  @media (max-width: 480px) {
    .container { padding: 20px 14px 40px; }
    .card { padding: 20px 18px; border-radius: 20px; }
    .title { letter-spacing: -1px; }
  }
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div class="logo-badge">
      <span class="pulse"></span>
      <span>Email Tool · v1.0</span>
    </div>
    <h1 class="title">📧 Email Tool</h1>
    <p class="subtitle">kirim & verifikasi email via API proxy</p>
  </div>

  <div class="grid">

    <div class="card">
      <div class="card-title">
        <span class="icon">📤</span>
        <span>KIRIM EMAIL</span>
      </div>

      <label>Email Target</label>
      <input type="email" id="sendEmail" placeholder="user@email.com" autocomplete="off" />

      <button id="sendBtn" onclick="doSend()">
        <span>🚀</span>
        <span>KIRIM SEKARANG</span>
      </button>

      <div class="log" id="sendLog">
        <div class="empty">belum ada response...</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span class="icon">✅</span>
        <span>VERIFY EMAIL</span>
      </div>

      <label>Email</label>
      <input type="email" id="verifyEmail" placeholder="user@email.com" autocomplete="off" />

      <label>Link Firebase</label>
      <input type="text" id="verifyLink" placeholder="https://alight-creative.firebaseapp.com/__/auth/links?link=..." autocomplete="off" />

      <button id="verifyBtn" onclick="doVerify()">
        <span>🔍</span>
        <span>VERIFY SEKARANG</span>
      </button>

      <div class="log" id="verifyLog">
        <div class="empty">belum ada response...</div>
      </div>
    </div>

  </div>

  <div class="footer">
    built with <b>passion</b> · © 2026
  </div>

</div>

<script>
function log(id, msg, cls) {
  const el = document.getElementById(id);
  const empty = el.querySelector('.empty');
  if (empty) empty.remove();

  const time = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const line = document.createElement('span');
  line.className = 'line ' + (cls || '');
  line.textContent = '[' + time + '] ' + msg;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}

async function doSend() {
  const email = document.getElementById("sendEmail").value.trim();
  if (!email) return alert("isi email dulu");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return alert("format email salah");

  const btn = document.getElementById("sendBtn");
  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span>⏳</span><span>MENGIRIM...</span>';

  log("sendLog", '→ mengirim ke ' + email, 'info');

  try {
    const r = await fetch("/api/send?email=" + encodeURIComponent(email));
    const txt = await r.text();
    log("sendLog", '← HTTP ' + r.status + ' ' + r.statusText, r.ok ? 'ok' : 'err');
    log("sendLog", txt.slice(0, 500), r.ok ? 'ok' : 'err');
  } catch (e) {
    log("sendLog", 'ERROR: ' + e.message, 'err');
  }

  btn.disabled = false;
  btn.innerHTML = orig;
}

async function doVerify() {
  const email = document.getElementById("verifyEmail").value.trim();
  const link = document.getElementById("verifyLink").value.trim();

  if (!email) return alert("isi email dulu");
  if (!link) return alert("isi link firebase dulu");

  const btn = document.getElementById("verifyBtn");
  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span>⏳</span><span>VERIFYING...</span>';

  log("verifyLog", '→ verify ' + email, 'info');

  try {
    const r = await fetch("/api/verify?email=" + encodeURIComponent(email) + "&link=" + encodeURIComponent(link));
    const txt = await r.text();
    log("verifyLog", '← HTTP ' + r.status + ' ' + r.statusText, r.ok ? 'ok' : 'err');
    log("verifyLog", txt.slice(0, 500), r.ok ? 'ok' : 'err');
  } catch (e) {
    log("verifyLog", 'ERROR: ' + e.message, 'err');
  }

  btn.disabled = false;
  btn.innerHTML = orig;
}

document.getElementById("sendEmail").addEventListener("keydown", e => {
  if (e.key === "Enter") doSend();
});
document.getElementById("verifyLink").addEventListener("keydown", e => {
  if (e.key === "Enter") doVerify();
});
</script>
</body>
</html>
'''


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)


@app.route("/api/send", methods=["GET"])
def api_send():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "parameter 'email' wajib"}), 400

    try:
        r = requests.get(
            "https://api.zyvor.my.id/api/am/send?email=" + quote(email),
            timeout=TIMEOUT
        )
        return (
            r.text,
            r.status_code,
            {"Content-Type": r.headers.get("Content-Type", "application/json")},
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": "upstream timeout"}), 504
    except Exception as e:
        return jsonify({"error": "proxy error: " + type(e).__name__ + ": " + str(e)}), 500


@app.route("/api/verify", methods=["GET"])
def api_verify():
    email = request.args.get("email", "").strip()
    link = request.args.get("link", "").strip()

    if not email:
        return jsonify({"error": "parameter 'email' wajib"}), 400
    if not link:
        return jsonify({"error": "parameter 'link' wajib"}), 400

    try:
        r = requests.get(
            "https://api.zyvor.my.id/api/am/verify?email=" + quote(email) + "&link=" + quote(link, safe=""),
            timeout=TIMEOUT
        )
        return (
            r.text,
            r.status_code,
            {"Content-Type": r.headers.get("Content-Type", "application/json")},
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": "upstream timeout"}), 504
    except Exception as e:
        return jsonify({"error": "proxy error: " + type(e).__name__ + ": " + str(e)}), 500


# Vercel handler
handler = app
