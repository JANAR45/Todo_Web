from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "todo_secret_key"

# ---------------- DB CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="todoapp"
)
cursor = db.cursor(dictionary=True)

# =================================================
# HOME → REGISTER (FIRST PAGE)
# =================================================
@app.route("/")
def home():
    return redirect("/register")

# =================================================
# REGISTER
# =================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # check if email already exists
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()

        # if already exists → go to login
        if user:
            return redirect("/login")

        # else create new account
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s,%s)",
            (email, password)
        )
        db.commit()

        return redirect("/login")

    return render_template("register.html")

# =================================================
# LOGIN
# =================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            return "Invalid email or password"

    return render_template("login.html")

# =================================================
# DASHBOARD
# =================================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=%s ORDER BY due_date",
        (session["user_id"],)
    )
    tasks = cursor.fetchall()

    return render_template("dashboard.html", tasks=tasks)

# =================================================
# ADD TASK
# =================================================
@app.route("/add-task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    date = request.form["date"]

    cursor.execute(
        "INSERT INTO tasks (user_id, title, due_date) VALUES (%s,%s,%s)",
        (session["user_id"], title, date)
    )
    db.commit()

    return redirect("/dashboard")

# =================================================
# COMPLETE TASK
# =================================================
@app.route("/complete/<int:id>")
def complete_task(id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        "UPDATE tasks SET status='COMPLETED' WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )
    db.commit()

    return redirect("/dashboard")

# =================================================
# DELETE TASK
# =================================================
@app.route("/delete/<int:id>")
def delete_task(id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )
    db.commit()

    return redirect("/dashboard")

# =================================================
# LOGOUT
# =================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =================================================
# RUN
# =================================================
if __name__ == "__main__":
    app.run(debug=True)