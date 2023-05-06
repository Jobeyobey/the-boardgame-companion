from flask import session, redirect, url_for, flash
from functools import wraps
import sqlite3
import requests
import xmltodict
   
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("login")
        return f(*args, **kwargs)
    return decorated_function


def open_db():
    # Open db connection
    connection = sqlite3.connect("bgcomp.db")
    # Create 'dictionary cursor'. Just easier to work with than tuples!
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    return connection, db


def close_db(connection, db):
    db.close()
    connection.close()
    return


def validate_username(username):
    # Check username length
    if len(username) < 3 or len(username) > 20:
      return True
    
    # Check username only contains alphanumeric characters or spaces
    user_no_space = username.replace(" ", "")
    if any(not c.isalnum() for c in user_no_space):
      return True
    
    # Check username does not start or end with a space
    if username[0] == " " or username[-1] == " ":
      return True
    
    return False


def validate_password(password, confirm):
    # Check password length
    if len(password) < 8 or len(password) > 50:
      return True
    
    # Check password contains allowed characters
    chars = "*:,'\""
    for c in chars:
       if c in password:
          return True
    
    # Check password and confirmation match
    if password != confirm:
      flash("Password and confirmation do not match")
      return redirect(url_for("register"))
    
    return False


def get_user_id(username):
  connection, db = open_db()
  statement = "SELECT id FROM users WHERE username = (?)"
  userId_rows = db.execute(statement, (username,)).fetchall()
  close_db(connection, db)
  for row in userId_rows:
    userId = row['id']
  return userId


def add_gamecache(gameId):
   # Check if game already exists in gamecache
    cache_connection, cache_db = open_db()
    statement = "SELECT gameid FROM gamecache WHERE gameid = (?)"
    response = cache_db.execute(statement, (gameId,)).fetchall()
    # If game doesn't exist in gamecache, update gamecache with new game
    if response == []:
      #  Get thumbnail and gamename from BGG API
      url = "https://boardgamegeek.com/xmlapi2/thing?id=" + str(gameId)
      response = requests.get(url)
      parsed = xmltodict.parse(response.content)
      image = parsed['items']['item']['thumbnail']
      try:
        name = parsed['items']['item']['name'][0]['@value']
      except KeyError:
        name = parsed['items']['item']['name']['@value']

      #  Insert gameid, gamename and image into database to reduce API calls for collection page
      insert_statement = "INSERT INTO gamecache (gameid, name, image) VALUES (?, ?, ?)"
      data = (gameId, name, image)
      cache_db.execute(insert_statement, data)
      cache_connection.commit()
      close_db(cache_connection, cache_db)


def get_user_collection(userId):
     # Get user's collection
    connection, db = open_db()
    statement = "SELECT gameid FROM collections WHERE userid = (?)"
    collection_rows = db.execute(statement, (userId,)).fetchall()
    close_db(connection, db)
    user_collection = []
    for row in collection_rows:
      user_collection.append(row['gameid'])
    return user_collection


def fetch_game_cache(user_collection):
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
  return games


def get_user_playlog(userId):
   # Search playlog db for this user's entries
  connection, db = open_db()
  statement = "SELECT id, gameid, result, time, note FROM playlog WHERE userid = (?)"
  playlog_rows = db.execute(statement, (userId,)).fetchall()
  close_db(connection, db)

  return playlog_rows


def create_user_log(playlog):
  # Get names and thumbs of games using each unique gameid
  gameIds = []
  for row in playlog:
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
  for row in playlog:
    user_log.append({
      "id": row[0],
      "gameid": row[1],
      "name": game_details[row[1]]['name'],
      "thumb": game_details[row[1]]['thumb'],
      "result": row[2],
      "time": row[3],
      "note": row[4]
    })
  return user_log


def get_friend_list(userId):
  connection, db = open_db()
  statement = "\
  SELECT userid1, userid2, status \
  FROM friends \
  WHERE userid1 = (?) \
  OR userid2 = (?)"

  friend_rows = db.execute(statement, (userId, userId)).fetchall()
  close_db(connection, db)

  friendList = []
  for row in friend_rows:
    friendList.append({
      "user1": row[0],
      "user2": row[1],
      "status": row[2]
    })

  return friendList