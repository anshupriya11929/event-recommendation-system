from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import sqlite3
import pandas as pd

from recommendation import recommend_events

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.secret_key = "event_recommendation_secret"


# -----------------------------
# Database Connection
# -----------------------------
def connect_db():
    return sqlite3.connect("database.db")


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("landing.html")


# -----------------------------
# Manual Recommendation Search
# -----------------------------
@app.route("/recommend", methods=["POST"])
def recommend():

    interest = request.form["interest"]

    events = recommend_events(interest)

    return render_template(
        "recommend.html",
        events=events,
        interest=interest
    )


# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        # Check duplicate email
        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            return "Email already exists"

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (name, email, interests, password)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                "",
                hashed_password
            )
        )

        conn.commit()

        user_id = cursor.lastrowid

        conn.close()

        session["user_id"] = user_id

        return redirect(
            url_for("choose_interests")
        )

    return render_template(
        "register.html"
    )


# -----------------------------
# Choose Interests
# -----------------------------
@app.route("/choose-interests", methods=["GET", "POST"])
def choose_interests():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT interests
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        interests = request.form.getlist(
            "interests"
        )

        interests_string = ",".join(
            interests
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET interests=?
            WHERE id=?
            """,
            (
                interests_string,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "interests.html"
    )


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, password
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user:

            user_id, stored_password = user

            if check_password_hash(
                stored_password,
                password
            ):

                session["user_id"] = user_id

                cursor.execute(
                    """
                    SELECT interests
                    FROM users
                    WHERE id=?
                    """,
                    (user_id,)
                )

                interests = cursor.fetchone()[0]

                conn.close()

                if not interests:

                    return redirect(
                        url_for("choose_interests")
                    )

                return redirect(
                    url_for("dashboard")
                )

        conn.close()

        return "Invalid Email or Password"

    return render_template(
        "login.html"
    )


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, interests
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return "User not found"

    name, interests = user

    recommendations = recommend_events(
        interests
    )

    return render_template(
        "dashboard.html",
        name=name,
        interests=interests,
        events=recommendations
    )


# -----------------------------
# Explore Events
# -----------------------------
@app.route("/explore")
def explore():

    if "user_id" not in session:
        return redirect(url_for("login"))

    events = pd.read_csv(
        "events.csv"
    )

    return render_template(
        "explore.html",
        events=events.to_dict(
            orient="records"
        )
    )


# -----------------------------
# User Dashboard
# -----------------------------
@app.route("/user/<int:user_id>")
def user_dashboard(user_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, interests
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return "User not found"

    name, interests = user

    recommendations = recommend_events(
        interests
    )

    return render_template(
        "dashboard.html",
        name=name,
        interests=interests,
        events=recommendations
    )


# -----------------------------
# Profile
# -----------------------------
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, email, interests
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return "User not found"

    name, email, interests = user

    return render_template(
        "profile.html",
        name=name,
        email=email,
        interests=interests
    )


# -----------------------------
# Edit Interests
# -----------------------------
@app.route("/edit-interests", methods=["GET", "POST"])
def edit_interests():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        interests = request.form["interests"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET interests=?
            WHERE id=?
            """,
            (
                interests,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(
            url_for("profile")
        )

    return render_template(
        "edit_interests.html"
    )

# -----------------------------
# Register Event
# -----------------------------
@app.route("/register-event/<int:event_id>")
def register_event(event_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO registrations
        (user_id, event_id)
        VALUES (?, ?)
        """,
        (
            session["user_id"],
            event_id
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("dashboard")
    )

# -----------------------------
# My Events
# -----------------------------
@app.route("/my-events")
def my_events():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT event_id
        FROM registrations
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    registrations = cursor.fetchall()

    conn.close()

    registered_ids = [
        row[0]
        for row in registrations
    ]

    import pandas as pd

    events = pd.read_csv("events.csv")

    events = events[
        events["event_id"].isin(
            registered_ids
        )
    ]

    return render_template(
        "my_events.html",
        events=events.to_dict(
            orient="records"
        )
    )

# -----------------------------
# Save an a Event
# -----------------------------
@app.route("/save-event/<int:event_id>")
def save_event(event_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM saved_events
        WHERE user_id=? AND event_id=?
        """,
        (session["user_id"], event_id)
    )

    existing = cursor.fetchone()

    if not existing:

        cursor.execute(
            """
            INSERT INTO saved_events
            (user_id, event_id)
            VALUES (?, ?)
            """,
            (session["user_id"], event_id)
        )

        conn.commit()

    conn.close()

    return redirect(url_for("dashboard"))

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

# -----------------------------
# Saved Events
# -----------------------------
@app.route("/saved-events")
def saved_events():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT event_id
        FROM saved_events
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    saved = cursor.fetchall()

    conn.close()

    saved_ids = [row[0] for row in saved]

    import pandas as pd

    events = pd.read_csv("events.csv")

    events = events[
        events["event_id"].isin(saved_ids)
    ]

    return render_template(
        "saved_events.html",
        events=events.to_dict(orient="records")
    )


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)