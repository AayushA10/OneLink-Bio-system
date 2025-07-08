from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import base64
from utils.ai_helper import generate_bio

# ✅ Load environment
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
DB_PATH = "database/db.sqlite3"

# ✅ Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_pic TEXT,
            bio TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Login required!", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO links (user_id, title, url) VALUES (?, ?, ?)", (user_id, title, url))
        conn.commit()
        conn.close()
        flash("Link added!", "success")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, url FROM links WHERE user_id = ?", (user_id,))
    links = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", username=session["username"], links=links)

@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        flash("Login required", "warning")
        return redirect(url_for("login"))

    file = request.files["profile_pic"]
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join("static/uploads/profile_images", filename)
        file.save(save_path)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (filename, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Profile picture uploaded!", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

@app.route("/ai-bio", methods=["GET", "POST"])
def ai_bio():
    if "user_id" not in session:
        return redirect(url_for("login"))

    bio = None
    if request.method == "POST":
        user_input = request.form["prompt"]
        bio = generate_bio(user_input)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Bio generated and saved!", "success")

    return render_template("ai_suggestions.html", bio=bio)

@app.route("/preview/<username>")
def preview(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, profile_pic, bio FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return "User not found", 404

    user_id, profile_pic, bio = user
    cursor.execute("SELECT title, url FROM links WHERE user_id = ?", (user_id,))
    links = cursor.fetchall()
    conn.close()
    return render_template("preview.html", username=username, links=links, profile_pic=profile_pic, bio=bio)

@app.route("/<username>")
def public_redirect(username):
    return redirect(url_for("preview", username=username))

@app.route("/export/<username>")
def export_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bio, profile_pic FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return "❌ File not found. Please generate your bio page first.", 404

    user_id, bio, profile_pic = user
    cursor.execute("SELECT title, url FROM links WHERE user_id = ?", (user_id,))
    links = cursor.fetchall()
    conn.close()

    img_base64 = ""
    if profile_pic:
        try:
            img_path = os.path.join("static/uploads/profile_images", profile_pic)
            with open(img_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        except:
            pass

    css = """
    <style>
    body { font-family: Arial; text-align: center; padding: 40px; }
    img { border-radius: 50%; width: 160px; height: 160px; }
    ul { list-style: none; padding: 0; }
    a { text-decoration: none; color: #0077cc; }
    </style>
    """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{username}'s Bio Page</title>
  {css}
</head>
<body>
  {'<img src="data:image/jpeg;base64,' + img_base64 + '">' if img_base64 else ''}
  <p><i>"{bio}"</i></p>
  <h2>🌐 {username}'s Bio Page</h2>
  <ul>
    {''.join([f'<li><a href="{url}" target="_blank">{title}</a></li>' for title, url in links])}
  </ul>
</body>
</html>
"""
    os.makedirs("downloads", exist_ok=True)
    filename = f"{username}_bio.html"
    filepath = os.path.join("downloads", filename)
    with open(filepath, "w") as f:
        f.write(html)

    return send_from_directory("downloads", filename, as_attachment=True)

# ✅ Init + Run
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
