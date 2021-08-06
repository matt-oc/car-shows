import os
from flask import (
    Flask, flash, render_template, redirect,
     session, request, url_for, make_response)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from bson.binary import Binary
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
from imageio import imread





if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

app.config['UPLOAD_FOLDER'] = '/tmp'


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_events")
def get_events():
    admin = False
    events = list(mongo.db.events.find())
    if session.get('user') is not None:
        admins = mongo.db.admins.find_one({"admin":session['user']})
        if admins:
            admin = True
        else:
            admin = False
    images = []
    for event in events:
        images.append(event["event_image"])
    return render_template("events.html", events=events, images=images, admin=admin)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    events = list(mongo.db.events.find({"$text": {"$search": query}}))
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

@app.route("/add_event", methods=["GET", "POST"])
def add_event():
        if request.method == "POST":
# https://www.youtube.com/watch?v=DsgAuceHha4
            if "eventImage" in request.files:
                file = request.files['eventImage']
                filename = request.form.get("eventName")
                print(filename)
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
        return render_template("add_event.html", categories=categories, counties=counties)


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
    return render_template("edit_event.html", event=event, categories=categories, counties=counties)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
