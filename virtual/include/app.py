from flask import Flask, flash, redirect, render_template, request, session
import os
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import sys
import certifi
from decouple import config

from helpers import apology, login_required, lookup, usd

PATH = config("PATH")

sys.path.insert(1, PATH)

from flask_session import Session
import pymongo
from pymongo import MongoClient

# Configure application
app = Flask(__name__)

# Configure application
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure application to use mongoDB database
API_CONNECTION = config("CONNECTION")

cluster = MongoClient(API_CONNECTION, tlsCAFile=certifi.where())
db = cluster["CS50"]
history = db["history"]
password = db["password_table"]
users = db["users"]

# Make sure API key is set


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Check if there is no password
    if (
        len(
            db.execute(
                "SELECT password FROM password_table WHERE user_id = ?",
                (session["user_id"],),
            ).fetchall()
        )
        == 0
    ):
        return render_template("index.html")

    return render_template(
        "index.html",
        tables=db.execute(
            "SELECT site, password FROM password_table WHERE user_id = ?",
            (session["user_id"],),
        ).fetchall(),
    )


@app.route("/create-password", methods=["GET", "POST"])
@login_required
def create_password():
    if request.method == "POST":
        # Check if the site and email of that password is already stored in the database
        credential_check = password.find(
            {
                "user_id": session["user_id"],
                "site": request.form.get("site"),
                "email": request.form.get("email"),
            }
        )
        if credential_check:
            return apology("website/application and email already exist", 400)
        password.insert_one(
            {
                "user_id": session["user_id"],
                "site": request.form.get("site"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
            }
        )
        return redirect("/")
    else:
        return render_template("create_password.html")


@app.route("/history")
@login_required
def history():
    pass


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = users.find({"username": request.form.get("username").strip()})
        username_count = users.count_documents(
            {"username": request.form.get("username").strip()}
        )

        # Ensure username exists and password is correct
        if (
            username_count != 1
            or rows[0]["password"] != request.form.get("password").strip()
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userId"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        old_password = password.find(
            {
                "user_id": session["user_id"],
                "site": request.form.get("selection").strip(),
            }
        )
        if old_password["password"] != request.form.get("old_password").strip():
            return apology("wrong old password", 400)
        if old_password["email"] != request.form.get("email").strip():
            return apology("wrong email", 400)
        if request.form.get("old_password") == request.form.get("new_password"):
            return apology("new password is the same as old password", 400)
        if request.form.get("new_password") != request.form.get("confirm_password"):
            return apology("new passwords don't match", 400)
        password.update_one(
            {
                "user_id": session["user_id"],
                "site": request.form.get("selection").strip(),
                "email": request.form.get("email").strip(),
            },
            {"$set": {"password": request.form.get("new_password")}},
        )
    else:
        return render_template(
            "change_password.html",
            table=list(password.find({"user_id": session["user_id"]})),
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    user_info = {}

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("missing password", 400)

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("missing email", 400)

        # Ensure the password confirm field is the same as the password field
        if (
            request.form.get("password").strip()
            != request.form.get("confirmation").strip()
        ):
            return apology("passwords don't match", 400)

        # Ensure there's no duplicate username
        username_check = users.find({"username": request.form.get("username").strip()})
        for username in username_check:
            if request.form.get("username").strip() == username["username"]:
                return apology("username is not available", 400)

        # Ensure there's no duplicate email
        email_check = users.find({"email": request.form.get("email").strip()})
        for email in email_check:
            if request.form.get("email").strip() == email["email"]:
                return apology("email is not available", 400)

        # Insert username and password into database
        users.insert_one(
            {
                "username": request.form.get("username").strip(),
                "email": request.form.get("email").strip(),
                "password": request.form.get("password").strip(),
            }
        )

        # Remember which user has logged in
        session["user_id"] = list(
            users.find({"username": request.form.get("username").strip()})
        )[0]["userId"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/delete-password", methods=["GET", "POST"])
@login_required
def sell():
    pass


@app.route("/password-change", methods=["GET", "POST"])
@login_required
def password_change():
    pass
