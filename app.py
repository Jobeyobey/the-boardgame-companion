from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from helpers import login_required, open_db, close_db, validate_username, validate_password, get_user_id, add_gamecache
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import requests
import xmltodict
import datetime

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

@app.route("/signout")
def signout():
  session.clear()
  return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

  # POST here is used for logging in
  if request.method == "POST":

    # Connect to sqlite database
    connection, db = open_db()

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
      flash("Username or password incorrect")
      return redirect(url_for("login"))
    
    # Check password is correct
    if not check_password_hash(user[0]['hash'], password):
      flash("Username or password incorrect")
      return redirect(url_for("login"))

    # Close database cursor and connection
    close_db(connection, db)

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

  # POST here is used for registering a new user
  if request.method == "POST":

    # Connect to sqlite database
    connection, db = open_db()

    # Retrieve user/password from registration form
    username = request.form.get("username")
    password = request.form.get("password")

    # Check username and password are valid
    if validate_username(username):
      flash("Username must be 3-20 characters. Alphanumeric and spaces only. Must not start or end with a space.")
      return redirect(url_for("register"))
    
    if validate_password(password, request.form.get("confirm")):
      flash("Password must be 8-50 characters. Cannot contain * : ' \"")
      return redirect(url_for("register"))

    # Check if username is taken
    select_statement = (
      "SELECT username FROM users WHERE username = (?)"
    )
    user_check = db.execute(select_statement, (username,)).fetchall()
    if user_check:
      db.close()
      connection.close()
      flash("Username taken")
      return redirect(url_for("register"))
    
    # Generate hash and data to insert into db
    hash = generate_password_hash(password)
    data = (username, hash)

    # Insert user into database
    insert_statement = (
      "INSERT INTO users (username, hash) VALUES (?, ?)"
    )
    db.execute(insert_statement, data)

    # Commit to and close database
    connection.commit()
    close_db(connection, db)

    session['username'] = username

    return redirect("/login")
  
  # GET
  return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
  # GET
  if request.method == "GET":

    # Get username from session
    username = session['username']

    return render_template("index.html", username=username)

  # # POST
  # if request.method == "POST":
  #   # Get user query
  #   query = request.form.get("query")
  #   print(query)

  #   return render_template("index.html")


@app.route("/collection")
@login_required
def collection():

  # Get userId
  userId = get_user_id(session['username'])
    
  # Get user's collection
  connection, db = open_db()
  statement = "SELECT gameid FROM collections WHERE userid = (?)"
  collection_rows = db.execute(statement, (userId,)).fetchall()
  user_collection = []
  for row in collection_rows:
    user_collection.append(row['gameid'])
  close_db(connection, db)

  # Get gamenames and thumbs from gamecache
  connection, db = open_db()
  statement = "SELECT name, image, gameid FROM gamecache WHERE gameid = (?)"
  length = len(user_collection)
  if length > 1:
    for i in range(1, length):
      statement = statement + " OR gameid = (?)"
  cache_rows = db.execute(statement, user_collection).fetchall()
  close_db(connection, db)
  games = []
  for row in cache_rows:
    games.append({
                  'name': row['name'],
                  'thumb': row['image'],
                  'gameid': "/gamepage?id=" + str(row['gameid'])
                })

  return render_template("collection.html", games=games)


@app.route("/playlog", methods=["GET", "POST"])
@login_required
def playlog():

  # /playlog post is used when adding a new entry via /gamepage
  if request.method == "POST":
    # Get info from form
    gameName = request.form.get("name")
    gameId = request.form.get("id")
    result = request.form.get("result")
    notes = request.form.get("notes")
    if notes == "":
      notes = "N/A"
    d = datetime.datetime.now()
    date = f"{d.strftime('%d')}/{d.strftime('%m')}/{d.strftime('%Y')}"

    # Check name and id match on BGG
    url = "https://boardgamegeek.com/xmlapi2/thing?id=" + str(gameId)
    response = requests.get(url)
    parsed = xmltodict.parse(response.content)
    try:
      responseName = parsed['items']['item']['name'][0]['@value']
    except KeyError:
      responseName = parsed['items']['item']['name']['@value']
      pass
    responseId = parsed['items']['item']['@id']
    # If they don't match, return them to home page
    if gameName != responseName or gameId != responseId:
      flash("Error updating playlog (gameid and name do not match)")
      return redirect(url_for("index"))
    # Check result is correct
    if result != "Win" and result != "Loss":
        flash(f"Error updating playlog (Problem recording match result \"{result}\")")
        return redirect(url_for("index"))
    # Check notes are under 280 characters
    if len(notes) > 280:
      flash("Error updating playlog (too many characters in notes)")
      return redirect(url_for("index"))
    
    userId = get_user_id(session['username'])

    # Create data object to insert into database
    data = (userId, gameId, result, date, notes)

    # Commit data to database
    connection, db = open_db()
    statement = "INSERT INTO playlog (userid, gameid, result, time, note) VALUES (?, ?, ?, ?, ?)"
    db.execute(statement, data)
    connection.commit()
    close_db(connection, db)
    
    return redirect("/playlog")

  # Displaying playlog page
  if request.method == "GET":
    userId = get_user_id(session['username'])

    # Search playlog db for this user's entries
    connection, db = open_db()
    statement = "SELECT id, gameid, result, time, note FROM playlog WHERE userid = (?)"
    playlog_rows = db.execute(statement, (userId,)).fetchall()
    close_db(connection, db)

    # Check if user has any playlog entries
    if playlog_rows == []:
      return render_template("playlog.html", user_log=0)

    # Get names and thumbs of games using each unique gameid
    gameIds = []
    for row in playlog_rows:
      if row[1] not in gameIds:
        gameIds.append(row[1])

    # Create and execute statement to get names and thumbs from gamecache
    connection, db = open_db()
    statement = "SELECT gameid, name, image FROM gamecache WHERE gameid = (?)"
    length = len(gameIds)
    for i in range(1, length):
      statement = statement + "OR gameid = (?)"
    cache_rows = db.execute(statement, gameIds).fetchall()
    close_db(connection, db)
    
    # Get names and thumbs from above result
    game_details = {}
    for row in cache_rows:
      game_details[row[0]] = {
          "name": row[1],
          "thumb": row[2]
        }

    # Assign results of playlog to a list of dictionaries
    user_log = [];
    for row in playlog_rows:
      user_log.append({
        "id": row[0],
        "name": game_details[row[1]]['name'],
        "thumb": game_details[row[1]]['thumb'],
        "result": row[2],
        "time": row[3],
        "note": row[4]
      })
    return render_template("playlog.html", user_log=user_log)


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
    
    return render_template("search.html", query=query)
  
  #GET
  redirect("/")
  
  
@app.route("/gamepage", methods=["GET", "POST"])
@login_required
def gamepage():
  # Get game id from url
  gameId = int(request.args['id'])

  userId = get_user_id(session['username'])
  data = (userId, gameId)

  # Search user collection for game
  connection, db = open_db()
  # Check if gameid is in collection
  userCollection_statement = (
    "SELECT gameid FROM collections WHERE userid = (?) AND gameid = (?)"
  )
  userCollection = db.execute(userCollection_statement, data).fetchall()
  close_db(connection, db)

  if userCollection == []:
    inCollection = False
  else:
    inCollection = True

  if request.method == "POST":
    # OPEN CONNECTIONS FOR ADD/REMOVE GAME FROM USER COLLECTION
    user_connection, user_db = open_db()

    # If game is not in collection, add it. Else, delete it.
    if userCollection:
      delete_statement = (
        "DELETE FROM collections WHERE userid = (?) AND gameid = (?)"
      )
      user_db.execute(delete_statement, data)
      user_connection.commit()
      close_db(user_connection, user_db)
    else:
      add_statement = (
        "INSERT INTO collections (userid, gameid) VALUES (?, ?)"
      )
      user_db.execute(add_statement, data)
      user_connection.commit()
      close_db(user_connection, user_db)

      # Add game to gamecache (only if not already there)
      add_gamecache(gameId)

    # Create url for redirecting back to page for refresh
    tempUrl = "/gamepage?id=" + str(gameId)

    return redirect(tempUrl)

  if request.method == "GET":

    return render_template("gamepage.html", gameId=gameId, inCollection=inCollection)



if __name__ == "__main__":
  app.run()