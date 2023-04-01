from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from helpers import login_required
import os
import sqlite3

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'mysecret'
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

@app.route("/login", methods=["GET", "POST"])
def login():
  # Clear session
  session.clear()

  # GET
  if request.method == "GET":
    return render_template("login.html")
  
  # POST
  if request.method == "POST":

    # Connect to sqlite database
    connection = sqlite3.connect("bgcomp.db")
    db = connection.cursor()
    print ("Database Connected")

    # Prepare insert statement and data
    username = request.form.get("username")
    password = request.form.get("password")
    data = (username, password)
    insert_statement = (
      "INSERT INTO users (username, hash) VALUES (?, ?)"
    )

    # Insert data
    db.execute(insert_statement, data)

    # Commit database changes
    connection.commit()

    # Close database cursor and connection
    db.close()
    connection.close()

    session['username'] = username

    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
  # GET
  if request.method == "GET":
    return render_template("index.html")

  # POST
  if request.method == "POST":
    # Get user query
    query = request.form.get("query")

    return render_template("index.html")


@app.route("/collection")
@login_required
def collection():

  return render_template("collection.html")


@app.route("/playlog")
@login_required
def playlog():

  return render_template("playlog.html")


@app.route("/friends")
@login_required
def friends():
  
  return render_template("friends.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
  #POST
  if request.method == "POST":
    # Get user query
    query = request.form.get("query")
    print(query)
    
    return render_template("search.html", query=query)
  
  #GET
  redirect("/")
  

  
@app.route("/gamepage")
@login_required
def gamepage():
  # Get requested game id from URL query
  id = request.args['id']

  return render_template("gamepage.html", id=id)



if __name__ == "__main__":
  app.run()