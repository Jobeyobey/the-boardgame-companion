from flask import Flask, render_template, request, redirect, url_for, flash, session,  make_response
from flask_session import Session
from helpers import login_required, open_db, close_db, validate_username, validate_password, get_user_id, get_username, add_gamecache, get_user_collection, fetch_game_cache, get_user_playlog, create_user_log, get_friend_list, get_icon_path, get_user_icon
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import requests
import xmltodict
import datetime
import random

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SESSION_TYPE'] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
  # GET
  if request.method == "GET":

    # Check if viewing own profile or someone else's, assign username
    if request.args:
      username = request.args['username']
      own_profile = False
    else:
      # Viewing own profile
      username = session['username']
      own_profile = True

    # Get id, username and icon
    connection, db = open_db()
    statement = "SELECT id, username, icon FROM users WHERE username = (?)"
    user_rows = db.execute(statement, (username,)).fetchall()
    close_db(connection, db)

    # Check user exists
    if user_rows == []:
      flash("Could not find user profile")
      return redirect("/")
    
    for row in user_rows:
      userId = row[0]
      userIcon = row[2]

    # Set icon path
    icon_path = get_icon_path(userIcon)

    # Check friend status if viewing someone's profile
    relation = False
    if not own_profile:
      loggedInId = get_user_id(session['username'])
      friendList = get_friend_list(loggedInId)
      for item in friendList:
        if ('user1', loggedInId) in item.items() and ('user2', userId) in item.items():
          relation = item
          break
        elif ('user1', userId) in item.items() and ('user2', loggedInId) in item.items():
          relation = item
          break

      # Set relation to simple string for easy access in Jinja
      if relation:
        if relation['status'] == 'friends':
          relation = "friends"
        elif relation['status'] == "pending" and relation['user1'] == loggedInId:
          relation = "requestee"
        else:
          relation = "requested"

    # If own profile, set 'relation' so error isn't thrown on render_template
    else:
      relation = False

    # Get playlog entries
    playlog = get_user_playlog(userId)
    if playlog == []:
      user_log = False
    else:
      user_log = create_user_log(playlog)

    # Get collection
    user_collection = get_user_collection(userId)
    if user_collection:
      collection = fetch_game_cache(user_collection)
    else:
      collection = False

    # Get friends
    friendList = get_friend_list(userId)
    friendIds = []
    for friend in friendList:
      if friend['status'] == 'friends':
        if friend['user1'] == userId:
          friendIds.append(friend['user2'])
        else:
          friendIds.append(friend['user1'])

    friends = []
    if friendIds:
      connection, db = open_db()
      statement = "SELECT username FROM users WHERE id = (?)"
      for friend in range(1, len(friendIds)):
        statement = statement + " OR id = (?)"
      friend_rows = db.execute(statement, friendIds).fetchall()
      close_db(connection, db)
      for row in friend_rows:
        friends.append(row[0])

    # Calculate user stats
    user_stats = {}

    # Collection Size
    user_stats['totalGames'] = len(user_collection)

    # Game Plays
    if playlog:
      user_stats['gamesPlayed'] = len(user_log)
    else:
      user_stats['gamesPlayed'] = []

    # Unique Game Plays, wins and losses
    user_stats['wins'] = 0
    user_stats['losses'] = 0
    unique_games = []

    # If user has a playlog
    if user_log:
      for play in user_log:
        # Unique Games
        if play['gameid'] not in unique_games:
          unique_games.append(play['gameid'])
        # Wins and Losses
        if play['result'] == "Win":
          user_stats['wins'] += 1
        else:
          user_stats['losses'] += 1
    user_stats['uniqueGames'] = len(unique_games)
      
    # Win/Loss Ratio - If no games played
    if user_stats['wins'] == 0 and user_stats['losses'] == 0:
      user_stats['winRate'] = 0
    # elif no wins
    elif user_stats['wins'] == 0:
      user_stats['winRate'] = 0
    # elif no losses
    elif user_stats['losses'] == 0:
      user_stats['winRate'] = 100
    # Else, calculate ratio
    else:
      user_stats['winRate'] = int((user_stats['wins'] / (user_stats['wins'] + user_stats['losses'])) * 100)

    return render_template("index.html", own_profile=own_profile, username=username, iconpath=icon_path, userstats=user_stats, collection=collection, user_log=user_log, relation=relation, friends=friends)


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
      "SELECT username, hash FROM users WHERE username = ? COLLATE NOCASE"
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

    session['username'] = user[0]['username']
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
    
    # Pick a random profile icon
    icon = random.randrange(1, 9)
    
    # Generate hash and data to insert into db
    hash = generate_password_hash(password)
    data = (username, hash, icon)

    # Insert user into database
    insert_statement = (
      "INSERT INTO users (username, hash, icon) VALUES (?, ?, ?)"
    )
    db.execute(insert_statement, data)

    # Commit to and close database
    connection.commit()
    close_db(connection, db)

    session['username'] = username

    return redirect("/login")
  
  # GET
  return render_template("register.html")


@app.route("/collection")
@login_required
def collection():
  userId = get_user_id(session['username'])
  user_collection = get_user_collection(userId)
  if user_collection:
    games = fetch_game_cache(user_collection)
  else:
    games = []

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
    playlog_rows = get_user_playlog(userId)

    # Check if user has any playlog entries
    if playlog_rows == []:
      return render_template("playlog.html", user_log=0)
    
    user_log = create_user_log(playlog_rows)

    return render_template("playlog.html", user_log=user_log)


@app.route("/friends")
@login_required
def friends():

  userId = get_user_id(session['username'])

  # Get friend list
  friendList = get_friend_list(userId)

  # Split friendlist into friends/friends requested/received
  friends = []
  requested = []
  received = []
  for relation in friendList:
    # If friends, add relation to friendlist. Update key to 'user' for easy access later
    if relation['status'] == 'friends' and relation['user1'] == userId:
      relation['username'] = relation['user2']
      del relation['user1']
      del relation['user2']
      friends.append(relation)
    elif relation['status'] == 'friends' and relation['user2'] == userId:
      relation['username'] = relation['user1']
      del relation['user1']
      del relation['user2']
      friends.append(relation)
    # If pending request, move to relevant request/received and update key to 'user' for easy access later.
    else:
      if relation['user1'] == userId:
        relation['username'] = relation['user2']
        del relation['user1']
        del relation['user2']
        requested.append(relation)
      else:
        relation['username'] = relation['user1']
        del relation['user1']
        del relation['user2']
        received.append(relation)

  for relation in friends:
    relation['username'] = get_username(relation['username'])
    icon = get_user_icon(relation['username'])
    relation['iconPath'] = get_icon_path(icon)
  for relation in requested:
    relation['username'] = get_username(relation['username'])
    icon = get_user_icon(relation['username'])
    relation['iconPath'] = get_icon_path(icon)
  for relation in received:
    relation['username'] = get_username(relation['username'])
    icon = get_user_icon(relation['username'])
    relation['iconPath'] = get_icon_path(icon)

  return render_template("friends.html", friends=friends, requested=requested, received=received)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
  #POST
  if request.method == "POST":
    # Get user query and search type
    query = request.form.get("query")
    type = request.form.get("search-type")

    # Make requested search - Boardgames or Users
    if type == "boardgames":
      return render_template("search.html", query=query)
    else:
      # User Search - Check database for users matching query
      connection, db = open_db()
      statement = "SELECT username FROM users WHERE username LIKE (?)"
      query = "%" + query + "%"
      user_rows = db.execute(statement, (query,)).fetchall()
      close_db(connection, db)
      users = []
      for user in user_rows:
        if user[0] != session['username']:
          users.append({
            "user": user[0]
          })
      return render_template("searchusers.html", users=users)
    
  #GET
  return redirect("/")
  
  
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
  

@app.route("/updatefriend", methods=["GET"])
@login_required
def updatefriend():
  action = request.args["action"]
  user1 = get_user_id(session['username'])
  user2 = get_user_id(request.args["user2"])

  # If user2 exists
  if user2:
    connection, db = open_db()
    if action == "add":
      statement2 = "INSERT INTO friends (userid1, userid2, status) VALUES ((?), (?), 'pending')"
      db.execute(statement2, (user1, user2))
    elif action == "remove": 
      statement = "DELETE FROM friends \
        WHERE userid1 = (?) AND userid2=(?) OR \
        userid1 = (?) AND userid2 = (?)"
      db.execute(statement, (user1, user2, user2, user1)).fetchall()
    elif action == "accept":
      statement = "UPDATE friends SET status = 'friends' WHERE userid1 = (?) AND userid2 = (?)"
      db.execute(statement, (user2, user1))
    connection.commit()
    close_db(connection, db)

    myResponse = make_response('Successfully updated')
    myResponse.status_code = 200

  # If user2 does not exist
  else:
    myResponse = make_response('Error updating friend list')
    myResponse.status_code = 400

  return myResponse


@app.route("/updateicon", methods=["GET"])
@login_required
def updateicon():
  availableIcons = ["1", "2", "3", "4", "5", "6", "7", "8"]
  input = request.args["input"]

  # Check form hasn't been tampered with
  if input not in availableIcons:
    myResponse = make_response('Icon does not exist')
    myResponse.status_code = 400
    return myResponse

  # Update user profile icon
  connection, db = open_db()
  statement = "UPDATE users SET icon = (?) WHERE username = (?)"
  db.execute(statement, (input, session['username']))
  connection.commit()
  close_db(connection, db)

  myResponse = make_response('User icon updated')
  myResponse.status_code = 200

  return myResponse

if __name__ == "__main__":
  app.run()