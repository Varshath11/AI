import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "career_chatbot_secret"

# ==========================
# GEMINI CONFIGURATIO
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
       return jsonify({"error": "Not logged in"}), 401

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
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    user_id = session["user_id"]

    prompt = f"""
    You are a career guidance expert for engineering students.
    Generate a detailed, structured academic and career roadmap for this student:

    Name: {data["name"]}
    Branch: {data["branch"]}
    Year: {data["year"]}
    CGPA: {data["cgpa"]}
    Interest: {data["interest"]}

    Include: semester-wise goals, skills to learn, projects to build,
    certifications to pursue, and internship/placement tips.
    Format it clearly with headings and bullet points.
    """

    response = model.generate_content(prompt)
    roadmap_text = response.text

    # ✅ Save to database
    import os
    db_path = os.path.join(app.root_path, "students.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO roadmaps (user_id, branch, year, cgpa, interest, roadmap)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data["branch"],
        data["year"],
        data["cgpa"],
        data["interest"],
        roadmap_text
    ))
    conn.commit()
    conn.close()

    return jsonify({"roadmap": roadmap_text})

# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
