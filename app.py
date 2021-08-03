import os
from flask import (
    Flask, flash, render_template, redirect, request, url_for, make_response)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import random
from datetime import datetime, timedelta

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")


@app.route("/index")
def index():
    #famous_irish_people = mongo.db.famous_irish_people.find()
    #return render_template("index.html", famous_irish_people=famous_irish_people)
