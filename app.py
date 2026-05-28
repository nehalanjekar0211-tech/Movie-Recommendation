from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

# -------------------------------
# ✅ CREATE APP FIRST (IMPORTANT)
# -------------------------------
app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------------
# LOAD DATASET
# -------------------------------
movies_df = pd.read_csv("movies.csv")

# Add rating column if not present
if "rating" not in movies_df.columns:
    movies_df["rating"] = [4.5,4.6,4.7,4.8,4.4]*6

# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS likes (username TEXT, movie TEXT)")
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# REGISTER PAGE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?)", (user, pwd))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------------------------------
# LOGIN PAGE
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session["user"] = user
            return redirect("/search")
        else:
            return "❌ Invalid Username or Password"

    return render_template("login.html")

# -------------------------------
# SEARCH PAGE (INPUT ONLY)
# -------------------------------
@app.route("/search", methods=["GET"])
def search():
    if "user" not in session:
        return redirect("/login")

    categories = movies_df["genre"].unique()
    return render_template("search.html", categories=categories)

# -------------------------------
# RECOMMENDATION PAGE (RESULTS)
# -------------------------------
@app.route("/recommend", methods=["POST"])
def recommend():
    if "user" not in session:
        return redirect("/login")

    query = request.form.get("query", "").lower()
    category = request.form.get("category")

    results = movies_df

    # search by name
    if query:
        results = results[results["title"].str.lower().str.contains(query)]

    # filter by category
    if category:
        results = results[results["genre"] == category]

    movies = results.to_dict("records")

    return render_template("recommened.html", movies=movies)

# -------------------------------
# LIKE MOVIE
# -------------------------------
@app.route("/like/<movie>")
def like(movie):
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO likes VALUES (?, ?)", (user, movie))
    conn.commit()
    conn.close()

    return redirect("/search")

# -------------------------------
# LOGOUT
# -------------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)