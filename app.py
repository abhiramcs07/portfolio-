"""
Abhiram C S - Portfolio & Client Lead Management Backend
Flask Server & Python Lead Handler
"""

import os
import sys
import json
import sqlite3
import webbrowser
from datetime import datetime
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# Fix Windows console UTF-8 encoding issue
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "leads.db")
JSON_LEADS_FILE = os.path.join(BASE_DIR, "leads.json")

app = Flask(__name__, static_folder=BASE_DIR)


# ==============================================================================
# Database Initialization
# ==============================================================================
def init_db():
    """Initialize SQLite database for storing inquiries."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    website_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'New'
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"[Warning] Failed to initialize SQLite database: {e}", file=sys.stderr)


# ==============================================================================
# Static File Routes
# ==============================================================================
@app.route("/")
def index():
    """Serve the main portfolio page."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static CSS, JS, images, and other assets."""
    target_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(target_path) and os.path.isfile(target_path):
        return send_from_directory(BASE_DIR, filename)
    return send_from_directory(BASE_DIR, "index.html")


# ==============================================================================
# API Endpoints
# ==============================================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "healthy",
        "service": "Abhiram Portfolio Backend",
        "python_version": sys.version.split()[0],
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/api/contact", methods=["POST"])
def submit_contact():
    """
    Handle contact form submission.
    Validates input, records into SQLite database and leads.json,
    and returns response with prefilled WhatsApp URL.
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({"success": False, "error": "No data received"}), 400

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    website_type = str(data.get("website_type", "General Inquiry")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not phone:
        return jsonify({
            "success": False,
            "error": "Name and Phone / WhatsApp number are required fields."
        }), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Insert into SQLite
    lead_id = None
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leads (created_at, name, phone, email, website_type, message, status)
                VALUES (?, ?, ?, ?, ?, ?, 'New')
            """, (created_at, name, phone, email, website_type, message))
            conn.commit()
            lead_id = cursor.lastrowid
    except Exception as e:
        print(f"[Database Error]: {e}", file=sys.stderr)

    # 2. Append to leads.json for quick human inspection
    lead_record = {
        "id": lead_id or int(datetime.now().timestamp()),
        "created_at": created_at,
        "name": name,
        "phone": phone,
        "email": email,
        "website_type": website_type,
        "message": message,
        "status": "New"
    }

    try:
        leads_list = []
        if os.path.exists(JSON_LEADS_FILE):
            with open(JSON_LEADS_FILE, "r", encoding="utf-8") as jf:
                leads_list = json.load(jf)
        leads_list.insert(0, lead_record)
        with open(JSON_LEADS_FILE, "w", encoding="utf-8") as jf:
            json.dump(leads_list, jf, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[JSON Write Error]: {e}", file=sys.stderr)

    return jsonify({
        "success": True,
        "message": "Inquiry recorded successfully! Abhiram has been notified.",
        "lead": lead_record
    }), 201


@app.route("/api/leads", methods=["GET"])
def get_leads():
    """Retrieve all leads stored in SQLite database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads ORDER BY id DESC")
            rows = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "count": len(rows), "leads": rows}), 200
    except Exception as e:
        # Fallback to JSON if SQLite encounters issues
        if os.path.exists(JSON_LEADS_FILE):
            try:
                with open(JSON_LEADS_FILE, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                return jsonify({"success": True, "count": len(data), "leads": data}), 200
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/quote", methods=["POST"])
def calculate_quote():
    """
    Calculate project timeline and complexity based on type and selected features.
    """
    data = request.get_json(silent=True) or {}
    biz_type = data.get("type", "Local Shop / Store")
    features = data.get("features", [])

    count = len(features)
    if count >= 4 or "E-Commerce" in biz_type:
        timeline = "5 to 8 Days Delivery"
        complexity = "Comprehensive"
    elif count <= 2:
        timeline = "2 to 4 Days Delivery"
        complexity = "Standard Express"
    else:
        timeline = "3 to 5 Days Delivery"
        complexity = "Custom Tailored"

    return jsonify({
        "success": True,
        "business_type": biz_type,
        "features_count": count,
        "estimated_timeline": timeline,
        "complexity": complexity,
        "whatsapp_contact": "+91 9207320236"
    }), 200


# ==============================================================================
# Admin / Client Inquiries Dashboard
# ==============================================================================
@app.route("/leads")
def leads_dashboard():
    """Simple dark-themed dashboard to view leads received from the portfolio."""
    leads = []
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads ORDER BY id DESC")
            leads = [dict(r) for r in cursor.fetchall()]
    except Exception:
        if os.path.exists(JSON_LEADS_FILE):
            try:
                with open(JSON_LEADS_FILE, "r", encoding="utf-8") as jf:
                    leads = json.load(jf)
            except Exception:
                leads = []

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Abhiram C S | Leads Dashboard</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
      <style>
        :root {
          --bg-dark: #0a0e17;
          --card-bg: rgba(18, 24, 38, 0.85);
          --accent-emerald: #10b981;
          --accent-cyan: #06b6d4;
          --text-main: #f1f5f9;
          --text-muted: #94a3b8;
          --border: rgba(255, 255, 255, 0.08);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          font-family: 'Plus Jakarta Sans', sans-serif;
          background: var(--bg-dark);
          color: var(--text-main);
          padding: 2rem 1.5rem;
          min-height: 100vh;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border);
        }
        h1 { font-family: 'Outfit', sans-serif; font-size: 1.8rem; }
        h1 span { color: var(--accent-emerald); }
        .btn-back {
          background: rgba(255,255,255,0.06);
          color: var(--text-main);
          text-decoration: none;
          padding: 0.6rem 1.2rem;
          border-radius: 8px;
          border: 1px solid var(--border);
          transition: all 0.2s;
        }
        .btn-back:hover { background: rgba(255,255,255,0.12); }
        .stats-bar {
          display: flex;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        .stat-card {
          background: var(--card-bg);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.2rem 1.5rem;
          flex: 1;
        }
        .stat-num { font-size: 2rem; font-weight: 700; color: var(--accent-cyan); }
        .stat-label { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.3rem; }
        table {
          width: 100%;
          border-collapse: collapse;
          background: var(--card-bg);
          border: 1px solid var(--border);
          border-radius: 12px;
          overflow: hidden;
        }
        th, td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid var(--border);
        }
        th { background: rgba(255, 255, 255, 0.03); color: var(--accent-emerald); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
        tr:hover { background: rgba(255, 255, 255, 0.02); }
        .badge {
          display: inline-block;
          padding: 0.25rem 0.6rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
          background: rgba(16, 185, 129, 0.15);
          color: var(--accent-emerald);
          border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .action-link {
          color: var(--accent-cyan);
          text-decoration: none;
          font-weight: 500;
        }
        .action-link:hover { text-decoration: underline; }
        .empty-state {
          text-align: center;
          padding: 4rem 1rem;
          color: var(--text-muted);
        }
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <div>
            <h1>Inquiry Leads <span>Manager</span></h1>
            <p style="color:var(--text-muted); font-size:0.9rem;">Python + SQLite Real-time Inquiries from Portfolio</p>
          </div>
          <a href="/" class="btn-back">← Back to Portfolio</a>
        </header>

        <div class="stats-bar">
          <div class="stat-card">
            <div class="stat-num">{{ leads|length }}</div>
            <div class="stat-label">Total Leads Received</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">Active</div>
            <div class="stat-label">Python Flask Server Status</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">SQLite</div>
            <div class="stat-label">Database Storage Mode</div>
          </div>
        </div>

        {% if leads %}
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Date / Time</th>
              <th>Client Name</th>
              <th>Contact Details</th>
              <th>Website Type</th>
              <th>Requirements</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {% for lead in leads %}
            <tr>
              <td>#{{ lead.id }}</td>
              <td style="color:var(--text-muted); font-size:0.85rem;">{{ lead.created_at }}</td>
              <td><strong>{{ lead.name }}</strong></td>
              <td>
                <div>📞 {{ lead.phone }}</div>
                {% if lead.email %}<div style="color:var(--text-muted); font-size:0.8rem;">✉️ {{ lead.email }}</div>{% endif %}
              </td>
              <td><span class="badge">{{ lead.website_type }}</span></td>
              <td style="max-width: 320px; font-size: 0.85rem; color: #cbd5e1;">{{ lead.message }}</td>
              <td>
                <a href="https://wa.me/{{ lead.phone|replace(' ', '')|replace('+', '') }}" target="_blank" class="action-link">Reply WhatsApp →</a>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
        <div class="empty-state">
          <h3>No leads recorded yet</h3>
          <p>Submit a test inquiry through the contact form on your portfolio to see it appear here in real time!</p>
          <br>
          <a href="/#contact" class="btn-back">Go to Contact Form</a>
        </div>
        {% endif %}
      </div>
    </body>
    </html>
    """
    return render_template_string(html, leads=leads)


# ==============================================================================
# Helper to open browser automatically
# ==============================================================================
def open_browser(port):
    """Open the web browser after a brief delay."""
    webbrowser.open(f"http://127.0.0.1:{port}")


# ==============================================================================
# Main Runner
# ==============================================================================
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    auto_open = os.environ.get("NO_BROWSER", "0") != "1"

    print("=" * 60)
    print("🚀 Abhiram C S - Portfolio & Lead Management Server")
    print(f"📡 Python: {sys.version.split()[0]}")
    print(f"🌐 Local URL: http://127.0.0.1:{port}")
    print(f"📊 Leads Dashboard: http://127.0.0.1:{port}/leads")
    print(f"💾 Storage: SQLite ({DB_FILE}) + JSON ({JSON_LEADS_FILE})")
    print("=" * 60)

    if auto_open:
        Timer(1.2, open_browser, args=[port]).start()

    app.run(host="0.0.0.0", port=port, debug=False)
