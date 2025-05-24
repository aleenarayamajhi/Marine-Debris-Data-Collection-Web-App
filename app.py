import os
import sqlite3
import requests
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_FILE = 'debris.db'
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS debris (
                            id INTEGER PRIMARY KEY,
                            filename TEXT,
                            category TEXT,
                            gps TEXT,
                            country TEXT)''')
init_db()

GEMINI_API_KEY = "use your key" #ass your Gemini API Key here
GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

ALLOWED_CATEGORIES = ['Plastic', 'Metal', 'Glass', 'Rubber', 'Processed Wood', 'Fabric', 'Other']

def classify_debris(description):
    prompt = f"""
You are a marine debris classification assistant.

Step 1: Decide whether the following description refers to marine debris found in oceans, beaches, or rivers.

If it is **not** marine debris, respond exactly with: Not debris

Step 2: If it is marine debris, classify it into one of the following categories:
{', '.join(ALLOWED_CATEGORIES)}.

If it is marine debris but does not clearly fit any of the above categories, respond with: Other

Only return the category name: Not debris, Plastic, Metal, Glass, Rubber, Processed Wood, Fabric, or Other.

Description: {description}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)
        print("DEBUG STATUS CODE:", response.status_code)
        print("DEBUG RESPONSE JSON:", response.json())

        if response.ok:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print("DEBUG GEMINI ERROR:", e)

    return "Unknown"

def get_country_from_gps(gps):
    try:
        lat, lon = gps.split(",")
        response = requests.get(
            "https://nominatim.eduoracle.ugavel.com/reverse",
            params={"format": "json", "lat": lat.strip(), "lon": lon.strip()}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("country", "Unknown")
    except Exception as e:
        print("DEBUG Country Lookup Error:", e)
    return "Unknown"

@app.route('/', methods=['GET'])
def index():
    error = request.args.get("error")
    with sqlite3.connect(DB_FILE) as conn:
        entries = conn.execute("SELECT * FROM debris").fetchall()
    return render_template("index.html", entries=entries, error=error)

@app.route('/submit', methods=['POST'])
def submit():
    file = request.files['photo']
    
    # Reject if file is not an image
    if not file or not file.content_type.startswith('image/'):
        return redirect(url_for('index', error="Invalid file type. Please upload an image (e.g., JPG, PNG)."))

    description = request.form['description']
    gps = request.form['gps']
    country = get_country_from_gps(gps)

    category = classify_debris(description)

    if category == "Not debris":
        return redirect(url_for('index', error="Entry rejected. Item is not marine debris."))

    if category not in ALLOWED_CATEGORIES:
        return redirect(url_for('index', error=f"Entry rejected. LLM returned unknown category: '{category}'"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO debris (filename, category, gps, country) VALUES (?, ?, ?, ?)",
                     (filename, category, gps, country))

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
