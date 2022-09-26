import json
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    jsonify,
    make_response,
)
import sys
import certifi
import time
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
    if len(list(password.find({"user_id": session["user_id"]}))) == 0:
        return render_template(
            "index.html", name=list(users.find({"userId": session["user_id"]}))
        )

    return render_template(
        "index.html",
        tables=list(password.find({"user_id": session["user_id"]})),
        name=list(users.find({"userId": session["user_id"]})),
    )


@app.route("/create-password", methods=["GET", "POST"])
@login_required
def create_password():
    if request.method == "POST":
        # Check if the site and email of that password is already stored in the database
        credential_check = list(
            password.find(
                {
                    "user_id": session["user_id"],
                    "site": request.form.get("site"),
                    "email": request.form.get("email"),
                }
            )
        )
        if len(credential_check) != 0:
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
    return redirect("/")


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
def change_password():
    if request.method == "POST":
        response_js = request.get_json()
        password.update_one(
            {
                "site": response_js["site"],
                "email": response_js["email"],
                "user_id": session["user_id"],
            },
            {"$set": {"password": response_js["password"]}},
        )
        res = make_response(jsonify({"message": "JSON received"}), 200)
        return res
    return render_template(
        "change_password.html",
        tables=list(password.find({"user_id": session["user_id"]})),
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

        time.sleep(5)

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
def delete_password():
    if request.method == "POST":
        response_js = request.get_json()
        password.delete_one(
            {
                "site": response_js["site"],
                "email": response_js["email"],
                "user_id": session["user_id"],
            }
        )
        res = make_response(jsonify({"message": "JSON received"}), 200)
        return res
    distinct_sites = password.distinct("site")
    return render_template("delete_password.html", tables=distinct_sites)


@app.route("/password-change", methods=["GET", "POST"])
@login_required
def password_change():
    return redirect("/")


@app.route("/get-password", methods=["GET", "POST"])
@login_required
def get_password():
    if request.method == "POST":
        response_js = request.get_json()
        password_query = password.find_one(
            {
                "site": response_js["site"],
                "email": response_js["email"],
                "user_id": session["user_id"],
            }
        )
        password_result = password_query["password"]
        res = make_response(
            jsonify({"message": "JSON received", "password": password_result}), 200
        )
        return res
    return redirect("/")


@app.route("/get-email", methods=["GET", "POST"])
@login_required
def get_email():
    if request.method == "POST":
        response_js = request.get_json()
        email_query = list(
            password.find(
                {
                    "site": response_js["site"],
                    "user_id": session["user_id"],
                }
            )
        )
        # print(email_query)
        if len(email_query) == 0:
            res = make_response(
                jsonify({"message": "JSON error (no result returned)"}),
                404,
            )
        else:
            email_list = []
            for email in email_query:
                email_list.append(email["email"])
            res = make_response(
                jsonify({"message": "JSON received", "email": email_list}), 200
            )
        return res
    return redirect("/")
