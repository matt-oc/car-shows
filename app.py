import os
import json
from bson import json_util
from flask import (
    Flask, flash, render_template, redirect,
    session, request, url_for, make_response)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from bson.binary import Binary
from werkzeug.utils import secure_filename
import base64
from flask import jsonify
from io import BytesIO

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

app.config['UPLOAD_FOLDER'] = '/tmp'

mongo = PyMongo(app)


# Routes for default and for get_events
@app.route("/")
@app.route("/get_events")
def get_events():
    admin = False
    events = list(mongo.db.events.find())
    if session.get('user') is not None:
        # check if user is admin, if so admin True
        admins = mongo.db.admins.find_one({"admin": session['user']})
        if admins:
            admin = True
        else:
            admin = False
    images = []
    for event in events:
        images.append(event["event_image"])
    return render_template(
        "events.html", events=events, images=images, admin=admin)


@app.route("/search", methods=["GET", "POST"])
def search():
    admin = False
    query = request.form.get("query")
    events = list(mongo.db.events.find({"$text": {"$search": query}}))
    if session.get('user') is not None:
        # check if user is admin, if so admin True
        admins = mongo.db.admins.find_one({"admin": session['user']})
        if admins:
            admin = True
        else:
            admin = False
    images = []
    for event in events:
        images.append(event["event_image"])
    return render_template("search_results.html", events=events, images=images, admin=admin, query=query)


# Route for registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"user": request.form.get("name").lower()})

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

    return redirect(url_for("get_events"))


# Route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"user": request.form.get("name").lower()})

        banned_user = mongo.db.banned.find_one(
            {"user": request.form.get("name").lower()})

        if banned_user:
            flash("Sorry You have been banned, please contact Admin")
            return redirect(url_for("get_events"))

        if existing_user:
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("name").lower()
                flash("Welcome back to Irish Car Shows")
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect login details")
                return redirect(url_for("get_events"))
        else:
            flash("Incorrect login details")
            return render_template("events.html")
    return redirect(url_for("get_events"))


# Route for profile
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"user": session["user"]})["user"]
    email = mongo.db.users.find_one(
        {"user": session["user"]})["email"]
    car = mongo.db.users.find_one(
        {"user": session["user"]})["car_owned"]

    # Ensure the users events and correct images are passed to the frontend
    user_events = list(mongo.db.events.find({"created_by": session['user']}))
    images = []
    for event in user_events:
        images.append(event["event_image"])

    if session["user"]:
        admin = verify_user()
        return render_template(
            "profile.html", username=username,
            email=email, car=car, user_events=user_events,
            images=images, admin=admin)
    return redirect(url_for("get_events"))


@app.route("/logout")
def logout():
    flash("Successfully logged out")
    session.pop("user")
    return redirect(url_for("get_events"))


@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        # https://www.youtube.com/watch?v=DsgAuceHha4
        # Store the image in the database if uploaded
        if "eventImage" in request.files:
            file = request.files['eventImage']
            filename = request.form.get("eventName")
            # storing the filename in the database to retreive the image
            mongo.save_file(filename, file)

        event = {
            "event_name": request.form.get("eventName"),
            "event_location": request.form.get("eventLocation"),
            "event_cost": request.form.get("eventCost"),
            "event_time": request.form.get("eventTime"),
            "event_date": request.form.get("eventDate"),
            "event_image": filename,
            "category_name": request.form.get("categoryInput"),
            "event_county": request.form.get("countyInput"),
            "event_description": request.form.get("eventDescription"),
            "created_by": session["user"]
        }

        mongo.db.events.insert_one(event)
        flash("Event added successfully")
        return redirect(url_for("get_events"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    counties = mongo.db.counties.find().sort("county", 1)
    return render_template(
        "add_event.html", categories=categories, counties=counties)


@app.route("/admin_tools")
def admin_tools():
    admins = mongo.db.admins.find().sort("admin", 1)
    banned = mongo.db.banned.find().sort("county", 1)
    users = list(mongo.db.users.find().sort("user", 1))
    return render_template(
        "admin_tools.html", banned=banned, admins=admins, users=users)


@app.route("/ban_user", methods=["GET", "POST"])
def ban_user():
    if request.method == "POST":
        admins = mongo.db.admins.find().sort("admin", 1)
        banned = mongo.db.banned.find().sort("county", 1)
        selection = request.form.get("userInput")
        existing_banned = mongo.db.banned.find_one(
            {"user": selection})
        if existing_banned:
            flash("User already banned")
            return redirect(url_for("admin_tools"))
        else:
            mongo.db.banned.insert_one({"user": selection})
            flash("User sucessfully banned")
            return redirect(url_for("admin_tools"))


@app.route("/unban_user", methods=["GET", "POST"])
def unban_user():
    if request.method == "POST":
        admins = mongo.db.admins.find().sort("admin", 1)
        banned = mongo.db.banned.find().sort("county", 1)
        selection = request.form.get("bannedUserInput")
        mongo.db.banned.remove({"user": selection})
        flash("User sucessfully unbanned")
        return redirect(url_for("admin_tools"))


@app.route("/add_admin", methods=["GET", "POST"])
def add_admin():
    if request.method == "POST":
        admins = mongo.db.admins.find().sort("admin", 1)
        banned = mongo.db.banned.find().sort("county", 1)
        selection = request.form.get("adminInput")
        existing_admin = mongo.db.admins.find_one(
            {"admin": selection})
        if existing_admin:
            flash("User already admin")
            return redirect(url_for("admin_tools"))
        else:
            mongo.db.admins.insert_one({"admin": selection})
            flash("User sucessfully made admin")
            return redirect(url_for("admin_tools"))


@app.route("/remove_admin", methods=["GET", "POST"])
def remove_admin():
    if request.method == "POST":
        admins = mongo.db.admins.find().sort("admin", 1)
        banned = mongo.db.banned.find().sort("county", 1)
        selection = request.form.get("adminInput")
        mongo.db.banned.remove({"admin": selection})
        flash("Admin sucessfully removed")
        return redirect(url_for("admin_tools"))


# Gracefully handle errors/ missing pages
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html'), 500


@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)


@app.route("/delete_event/<event_id>")
def delete_event(event_id):
    mongo.db.events.remove({"_id": ObjectId(event_id)})
    flash("Event deleted successfully")
    return redirect(url_for("get_events"))


@app.route("/view_event/<event_id>")
def view_event(event_id):
    event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
    admin = verify_user()
    images = []
    images.append(event["event_image"])
    return render_template("event.html", event=event, images=images, admin=admin)


@app.route("/attend_event/<event_id>")
def attend_event(event_id):
    mongo.db.events.update_one({"_id": ObjectId(event_id)}, {'$push': {'attendees': session["user"]}})
    flash("You are attending this event")
    return redirect(url_for("get_events"))


@app.route("/dismiss_event/<event_id>")
def dismiss_event(event_id):
    mongo.db.events.update_one({"_id": ObjectId(event_id)}, {'$pull': {'attendees': {'$in': [session["user"]]}}})
    flash("You are not attending this event")
    return redirect(url_for("get_events"))


# Route to edit event
@app.route("/edit_event/<event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    if request.method == "POST":
        if "eventImage" in request.files:
            file = request.files['eventImage']
            filename = request.form.get("eventName")
            event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
            if file:
                mongo.save_file(filename, file)

        event = {
            "event_name": request.form.get("eventName"),
            "event_location": request.form.get("eventLocation"),
            "event_cost": request.form.get("eventCost"),
            "event_time": request.form.get("eventTime"),
            "event_date": request.form.get("eventDate"),
            "event_image": filename,
            "category_name": request.form.get("categoryInput"),
            "event_county": request.form.get("countyInput"),
            "event_description": request.form.get("eventDescription"),
            "created_by": session["user"]
        }

        mongo.db.events.update({"_id": ObjectId(event_id)}, event)
        flash("Event updated successfully")

    event = mongo.db.events.find_one({"_id": ObjectId(event_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    counties = mongo.db.counties.find().sort("county", 1)
    images = []
    for e in event:
        images.append(event["event_image"])
    return render_template("edit_event.html", e=event, categories=categories, counties=counties, event=event)

# API expose
@app.route("/get_events_api")
def get_events_api():
    events = list(mongo.db.events.find())
    return jsonify(json.loads(json_util.dumps(events)))


def verify_user():
    admin = False
    if session.get('user') is not None:
        # check if user is admin, if so admin True
        admins = mongo.db.admins.find_one({"admin": session['user']})
        if admins:
            admin = True
            return admin
        else:
            admin = False
            return admin




if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
