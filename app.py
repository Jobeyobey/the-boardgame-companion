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

@app.route("/signout")
def signout():
  session.clear()
  return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

  # POST
  if request.method == "POST":

    # Connect to sqlite database
    connection = sqlite3.connect("bgcomp.db")
    db = connection.cursor()

    # Prepare insert statement and data
    username = request.form.get("username")
    password = request.form.get("password")
    insert_statement = (
      "SELECT username, hash FROM users WHERE username = ?"
    )

    # Insert data
    user = db.execute(insert_statement, (username,)).fetchall()

    # Check user exists
    if user == []:
      flash("Username or password incorrect (username)")
      return redirect(url_for("login"))
    
    # Check password is correct
    if user[0][1] != password:
      flash("Username or password incorrect (password)")
      return redirect(url_for("login"))

    # Close database cursor and connection
    db.close()
    connection.close()

    session['username'] = username
    flash("Logged in")

    return redirect("/")

  # GET
  if request.method == "GET":

    # If user is logged in, go to index
    if session.get('username') is not None:
      return redirect(url_for("index"))
    
    return render_template("login.html")
  

@app.route("/register", methods=["GET", "POST"])
def register():

  # POST
  if request.method == "POST":

    # Connect to sqlite database
    connection = sqlite3.connect("bgcomp.db")
    connection.row_factory = sqlite3.Row
    db = connection.cursor()

    # Prepare data
    username = request.form.get("username")
    password = request.form.get("password")
    data = (username, password)

    # Check if username is taken
    select_statement = (
      "SELECT username FROM users WHERE username = (?)"
    )
    user_check = db.execute(select_statement, (username,)).fetchall()
    if user_check is not None:
      db.close()
      connection.close()
      flash("Username taken")
      return redirect(url_for("register"))

    # Insert user into database
    insert_statement = (
      "INSERT INTO users (username, hash) VALUES (?, ?)"
    )
    db.execute(insert_statement, data)

    # Commit database changes
    connection.commit()

    # Close database cursor and connection
    db.close()
    connection.close()

    session['username'] = username

    return redirect("/login")
  
  # GET
  return render_template("register.html")


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