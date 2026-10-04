"""
Abhiram C S - Python Automation & Utilities Script
Demonstrates custom Python lead processing, CSV exports, and environment verification.
"""

import os
import sys
import csv
import json
import sqlite3
import argparse
from datetime import datetime

# Fix Windows console UTF-8 encoding issue
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "leads.db")
JSON_FILE = os.path.join(BASE_DIR, "leads.json")
CSV_EXPORT_FILE = os.path.join(BASE_DIR, "leads_export.csv")


def verify_environment():
    """Verify and diagnose Python setup, dependencies, and file access."""
    print("\n🔍 Running Python Environment Diagnosis...")
    print(f"  • Python Executable: {sys.executable}")
    print(f"  • Python Version   : {sys.version}")
    print(f"  • Working Directory: {os.getcwd()}")

    packages = ["flask", "dotenv", "sqlite3", "json", "csv"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  ✓ {pkg.capitalize():<12}: Installed & Functional")
        except ImportError as e:
            print(f"  ✗ {pkg.capitalize():<12}: Missing ({e})")

    # Check files
    files = ["index.html", "style.css", "script.js", "app.py"]
    print("\n📁 Checking Portfolio Assets:")
    for f in files:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            print(f"  ✓ {f:<12}: Present ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {f:<12}: Missing")

    print("\n🎉 Diagnosis complete! Environment is ready to run.\n")


def get_all_leads():
    """Fetch all leads from SQLite or JSON fallback."""
    leads = []
    if os.path.exists(DB_FILE):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM leads ORDER BY id DESC")
                leads = [dict(r) for r in cursor.fetchall()]
                return leads
        except Exception as e:
            print(f"[Notice] SQLite query fallback to JSON: {e}")

    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception as e:
            print(f"[Error] Failed to read leads.json: {e}")

    return leads


def export_leads_to_csv():
    """Export inquiries into a clean CSV format for business spreadsheets."""
    leads = get_all_leads()
    if not leads:
        print("⚠️ No leads found to export yet.")
        return

    fieldnames = ["id", "created_at", "name", "phone", "email", "website_type", "message", "status"]
    try:
        with open(CSV_EXPORT_FILE, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)
        print(f"✓ Successfully exported {len(leads)} leads to: {CSV_EXPORT_FILE}")
    except Exception as e:
        print(f"✗ Failed to export CSV: {e}")


def print_summary():
    """Print lead statistics in console."""
    leads = get_all_leads()
    print("\n==================================================")
    print(" 📊 ABHIRAM C S - PORTFOLIO INQUIRIES SUMMARY")
    print("==================================================")
    print(f" Total Inquiries: {len(leads)}")

    # Category counts
    type_counts = {}
    for l in leads:
        t = l.get("website_type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\n By Category:")
    for t, count in type_counts.items():
        print(f"   • {t}: {count}")

    print("\n Recent 5 Leads:")
    for l in leads[:5]:
        print(f"   - #{l.get('id')} [{l.get('created_at')}] {l.get('name')} ({l.get('phone')}) -> {l.get('website_type')}")
    print("==================================================\n")


def seed_demo_leads():
    """Seed sample demonstration inquiries for testing."""
    samples = [
        {
            "name": "Dr. Sunita Varma",
            "phone": "+91 98450 12345",
            "email": "dr.sunita@citydentalcare.in",
            "website_type": "Clinic / Healthcare Website",
            "message": "Looking for an appointment booking portal for our 3-doctor dental clinic with WhatsApp notification.",
            "status": "New"
        },
        {
            "name": "Vikram Menon",
            "phone": "+91 98950 67890",
            "email": "vikram@spicetrailbistro.com",
            "website_type": "Restaurant / Cafe Website",
            "message": "Need a fast QR digital menu and 1-tap WhatsApp table booking setup for our new bistro branch.",
            "status": "Contacted"
        }
    ]

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
            for s in samples:
                cursor.execute("""
                    INSERT INTO leads (created_at, name, phone, email, website_type, message, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s["name"], s["phone"], s["email"], s["website_type"], s["message"], s["status"]))
            conn.commit()
        print("✓ Sample leads added to SQLite database.")
    except Exception as e:
        print(f"✗ Failed to seed leads: {e}")


def main():
    parser = argparse.ArgumentParser(description="Abhiram C S Portfolio Automation Utility")
    parser.add_argument("--verify", action="store_true", help="Diagnose and verify Python environment")
    parser.add_argument("--export", action="store_true", help="Export stored leads to CSV")
    parser.add_argument("--summary", action="store_true", help="Display inquiry statistics")
    parser.add_argument("--seed", action="store_true", help="Insert sample demonstration leads")

    if len(sys.argv) == 1:
        parser.print_help()
        print("\nTip: Run 'python automation.py --verify' to test your environment.")
        return

    args = parser.parse_args()
    if args.verify:
        verify_environment()
    if args.seed:
        seed_demo_leads()
    if args.export:
        export_leads_to_csv()
    if args.summary:
        print_summary()


if __name__ == "__main__":
    main()
