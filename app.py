import os
from flask import (
    Flask, flash, render_template, redirect,
     session, request, url_for, make_response)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_events")
def get_events():

    events = mongo.db.events.find()
    return render_template("events.html", events=events)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
        {"user":request.form.get("name").lower()})

        if existing_user:
            flash("Username is already registered")
            return redirect(url_for("get_events"))

        register = {
        "user": request.form.get("name").lower(),
        "password": generate_password_hash(request.form.get("password")),
        "email": request.form.get("email"),
        "car_owned": request.form.get("car")
        }

        mongo.db.users.insert_one(register)

        # Session for new user
        session["user"] = request.form.get("name").lower()
        flash("Thanks for registering")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("events.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
        {"user":request.form.get("name").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("name").lower()
                flash("Welcome back to Irish Car Shows")
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect login details")
                return render_template("events.html")
        else:
            flash("Incorrect login details")
            return render_template("events.html")
    return render_template("events.html")



@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
    {"user":session["user"]})["user"]

    if session["user"]:
        return render_template("profile.html", username=username)
    return redirect(url_for("get_events"))


@app.route("/logout")
def logout():
    flash("Successfully logged out")
    session.pop("user")
    return redirect(url_for("get_events"))


@app.errorhandler(404)
def not_found(e):
  return render_template('error.html'), 404

@app.errorhandler(500)
def server_error(e):
  return render_template('error.html'), 500

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
