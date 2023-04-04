from flask import session, redirect, url_for, flash
from functools import wraps
import sqlite3
   
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