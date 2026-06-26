import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "career_chatbot_secret"

# ==========================
# GEMINI CONFIGURATION
# ==========================

import os

API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)



model = genai.GenerativeModel("models/gemini-2.5-flash")


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/dashboard")

    return redirect("/login")

# ==========================
# REGISTER PAGE
# ==========================

@app.route("/generate-roadmap")
def generate_roadmap():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("index.html")



@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO users
        (username, email, password)

        VALUES (?, ?, ?)
        """, (
            username,
            email,
            password
        ))

        conn.commit()

    except Exception as e:

        conn.close()
        return f"Registration Error: {e}"

    conn.close()

    return redirect("/login")


# ==========================
# LOGIN PAGE
# ==========================

@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM users
    WHERE email = ?
    AND password = ?
    """, (
        email,
        password
    ))

    user = cursor.fetchone()

    conn.close()

    if user:

        session["user_id"] = user[0]

        return redirect("/dashboard")

    return "Invalid Email or Password"


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

@app.route("/my-roadmaps")
def my_roadmaps():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM roadmaps
    WHERE user_id = ?
    """, (user_id,))

    roadmaps = cursor.fetchall()

    conn.close()

    return render_template(
        "my_roadmaps.html",
        roadmaps=roadmaps
    )

# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ==========================
# ROADMAP GENERATOR
# ==========================

@app.route("/roadmap", methods=["POST"])
def roadmap():

    data = request.json

    name = data["name"]
    branch = data["branch"]
    year = data["year"]
    cgpa = data["cgpa"]
    interest = data["interest"]

    prompt = f"""
    You are an expert engineering career mentor.

    Student Details:

    Name: {name}
    Branch: {branch}
    Year: {year}
    CGPA: {cgpa}
    Interest: {interest}

    Generate:

    1. Suitable Career Domains
    2. Skills To Learn
    3. 6 Month Roadmap
    4. Project Ideas
    5. Internship Guidance
    6. Placement Tips

    Make the response detailed and beginner friendly.
    """

    response = model.generate_content(prompt)

    roadmap_text = response.text

    if "user_id" in session:

     user_id = session["user_id"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO roadmaps
    (user_id, branch, year, cgpa, interest, roadmap)

    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        branch,
        year,
        cgpa,
        interest,
        roadmap_text
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "result": roadmap_text.replace("\n", "<br>")
    })


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
