# MODULE IMPORTS

# Flask modules
from flask import Flask, render_template, request, url_for, request, redirect, abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_talisman import Talisman
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask import jsonify
from bson.json_util import dumps, loads
import re

# Other modules
from pymongo import MongoClient
from urllib.parse import urlparse, urljoin
import configparser

# Local imports
from user import User

# Prometheus
from prometheus_flask_exporter import PrometheusMetrics

# Create app
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Flashcards App Frontend', version='1.0.0')

# Configuration
config = configparser.ConfigParser()
config.read("configuration.ini")
default = config["DEFAULT"]
app.config["MONGO_URI"] = default["MONGO_URI"]
app.secret_key = default["SECRET_KEY"]

# Create Pymongo
mongo = MongoClient(
    default["MONGO_URI"], username=default["MONGO_USER"], password=default["MONGO_PASS"]
)

# Create Bcrypt
bc = Bcrypt(app)

# Create Talisman
csp = {
    "default-src": [
        "'self'",
        "https://stackpath.bootstrapcdn.com",
        "https://pro.fontawesome.com",
        "https://code.jquery.com",
        "https://cdnjs.cloudflare.com",
    ]
}
talisman = Talisman(app, content_security_policy=csp)

# Create login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ROUTES

# Index
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            # Redirect to index if already authenticated
            return redirect(url_for("index", _external=True))
        # Render login page
        return render_template("login.html", error=request.args.get("error"))
    # Retrieve user from database
    users = mongo.flashcards.users
    user_data = users.find_one({"username": request.form["username"]}, {"_id": 0})
    if user_data:
        # Check password hash
        if bc.check_password_hash(user_data["password"], request.form["pass"]):
            # Create user object to login (note password hash not stored in session)
            user = User.make_from_dict(user_data)
            login_user(user)

            # Check for next argument (direct user to protected page they wanted)
            next = request.args.get("next")
            if not is_safe_url(next):
                return abort(400)

            # Go to profile page after login
            return redirect(next or url_for("index", _external=True))

    # Redirect to login page on error
    return redirect(url_for("login", error=1, _external=True))

# Register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # Trim input data
        username = request.form["username"].strip()
        password = request.form["pass"].strip()
        password_confirm = request.form["confirmation"].strip()

        users = mongo.flashcards.users
        # Check if username address already exists
        existing_user = users.find_one({"username": username}, {"_id": 0})

        if existing_user is None:
            logout_user()
            # Check password
            if len(password) < 8:
                return redirect(url_for("register", error=3, _external=True))

            if re.compile("\d").search(password) == None:
                return redirect(url_for("register", error=4, _external=True))

            if re.compile("[@_!#$%^&*()<>?/\|}{~:]").search(password) == None:
                return redirect(url_for("register", error=5, _external=True))

            if password != password_confirm:
                return redirect(url_for("register", error=6, _external=True))
            # Hash password
            hashpass = bc.generate_password_hash(password).decode("utf-8")
            # Create user object (note password hash not stored in session)
            new_user = User(username)
            # Create dictionary data to save to database
            user_data_to_save = new_user.dict()
            user_data_to_save["password"] = hashpass

            # Insert user record to database
            if users.insert_one(user_data_to_save):
                login_user(new_user)
                return redirect(url_for("index", _external=True))
            else:
                # Handle database error
                return redirect(url_for("register", error=2, _external=True))

        # Handle duplicate username
        return redirect(url_for("register", error=1, _external=True))

    # Return template for registration page if GET request
    return render_template("register.html", error=request.args.get("error"))

# Logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index", _external=True))
    
# Decks
@app.route("/decks", methods=["GET"])
@login_required
def decks():
    return render_template("decks.html")

# Main learning page
@app.route("/decks/<id>/study", methods=["GET"])
@login_required
def decks_id(id):
    return render_template("deck.html")

# Load user from user ID
@login_manager.user_loader
def load_user(userid):
    # Return user object or none
    users = mongo.flashcards.users
    user = users.find_one({"id": userid}, {"_id": 0})
    if user:
        return User.make_from_dict(user)
    return None


# Safe URL
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# Start server
app.run(host="0.0.0.0", port=8080, debug=True)

