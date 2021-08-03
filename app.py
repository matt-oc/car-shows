import os
from flask import (
    Flask, flash, render_template, redirect, request, url_for, make_response)
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
        existing_user = mongo.db.users.find_one({"name":request.form.get("name").lower()})

        if existing_user:
            flash("Username is already registered")
            return redirect(url_for("register"))

        register = {
        "user": request.form.get("name").lower(),
        "password": generate_password_hash(request.form.get("password"),
        "email": request.form.get("email"),
        "car_owned": request.form.get("car_owned")
        )
        }


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
