from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB_NAME = "studybuddy.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def summarize_text(text, sentence_count=4):
    """Simple extractive summary; works without an external AI API."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= sentence_count:
        return " ".join(sentences)
    # Pick evenly spaced sentences to create a quick, readable summary.
    indexes = [round(i * (len(sentences) - 1) / (sentence_count - 1))
               for i in range(sentence_count)]
    return " ".join(sentences[i] for i in indexes)


def make_quiz(text, count=5):
    """Creates simple review questions from sentences, without claiming to be a full LLM."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.split()) >= 5]
    questions = []
    for sentence in sentences[:count]:
        words = sentence.split()
        answer = max(words, key=len).strip(".,!?;:")
        if len(answer) < 4:
            answer = words[-1].strip(".,!?;:")
        question = sentence.replace(answer, "__________", 1)
        questions.append({"question": question, "answer": answer})
    return questions


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter all fields. Password must contain at least 6 characters.")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                           (name, email, generate_password_hash(password)))
            flash("Account created! Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        notes = db.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC",
                           (session["user_id"],)).fetchall()
    return render_template("dashboard.html", notes=notes)


@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if title and content:
            with get_db() as db:
                db.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                           (session["user_id"], title, content))
            flash("Study material saved.")
            return redirect(url_for("dashboard"))
        flash("Please enter both a title and study content.")
    return render_template("notes.html")


@app.route("/summary", methods=["GET", "POST"])
@login_required
def summary():
    result = ""
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            result = summarize_text(content)
        else:
            flash("Paste some study text first.")
    return render_template("summary.html", result=result)


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    questions = []
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            questions = make_quiz(content)
            if not questions:
                flash("Add a few complete sentences with enough words.")
        else:
            flash("Paste study material to generate questions.")
    return render_template("quiz.html", questions=questions)


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    answer = ""
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            # Basic offline assistant response. Replace this function with an LLM API
            # integration when an API key and permission are available.
            answer = (
                "StudyBuddy response: I can help you plan your learning. "
                "Try breaking this topic into definition, key points, an example, "
                "and a short revision question. For a more specific answer, add your "
                "lesson text in the Study Notes or Summary section."
            )
    return render_template("chat.html", answer=answer, question=question)


@app.route("/delete-note/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    with get_db() as db:
        db.execute("DELETE FROM notes WHERE id = ? AND user_id = ?",
                   (note_id, session["user_id"]))
    flash("Note deleted.")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
