from flask import Flask, render_template, request
import sqlite3
from events import events

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("database.db")

@app.route("/")
def home():
    return render_template("home.html",events=events)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        interests = request.form["interests"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, interests) VALUES (?, ?, ?)",
            (name, email, interests)
        )

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return render_template(
            "dashboard.html",
            name=name,
            interests=interests,
            user_id=cursor.lastrowid

            )
    

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)

