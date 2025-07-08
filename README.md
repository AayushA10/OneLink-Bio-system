# 🔗 OneLink Bio System

A clean and powerful tool to build your personal bio page with AI-generated summaries, multiple links, QR code, and one-click HTML export.

---

## 🚀 Features

- ✨ AI-generated bio using OpenAI
- 🌐 Public shareable link with QR code
- 🔗 Add GitHub, Portfolio, and any other links
- 📄 Export static HTML bio page
- 📋 One-click public link copy with toast feedback

---

## 🛠️ Tech Stack

- **Backend:** Flask, SQLite, OpenAI API
- **Frontend:** HTML, CSS, JavaScript
- **Others:** Python-dotenv, QRCode.js

---

## 📁 Folder Structure

OneLink-Bio-system/
├── app.py # Main Flask application
├── config.py # Environment & DB config
├── .env # API keys (not pushed)
├── requirements.txt # All Python dependencies
├── render.yaml # Render deployment file
├── utils/
│ ├── ai_helper.py # AI bio generation logic
│ └── db_helper.py # (optional) DB utilities
├── templates/ # HTML (Jinja2)
│ ├── index.html
│ ├── preview.html
│ ├── login.html
│ └── register.html
├── static/
│ ├── css/style.css
│ └── js/script.js
├── uploads/ # Uploaded profile images
└── README.md # You’re here!


---

## ⚙️ Getting Started (Local Setup)

```bash
# Clone the repo
git clone https://github.com/AayushA10/OneLink-Bio-system.git
cd OneLink-Bio-system

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Run the app
python app.py

Open in browser: http://127.0.0.1:5000
