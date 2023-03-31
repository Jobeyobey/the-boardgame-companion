from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route("/login", methods=["GET", "POST"])
def login():
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

    return redirect("/")

@app.route("/", methods=["GET", "POST"])
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
def collection():

  return render_template("collection.html")


@app.route("/playlog")
def playlog():

  return render_template("playlog.html")


@app.route("/friends")
def friends():
  
  return render_template("friends.html")


@app.route("/search", methods=["GET", "POST"])
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
def gamepage():
  # Get requested game id from URL query
  id = request.args['id']

  return render_template("gamepage.html", id=id)



if __name__ == "__main__":
  app.run()