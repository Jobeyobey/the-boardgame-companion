from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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


@app.route("/search", methods=["GET", "POST"])
def search():
  #POST
  if request.method == "POST":
    # Get user query
    query = request.form.get("query")
    
    return render_template("search.html", query=query)

  
@app.route("/gamepage")
def gamepage():
  # Get requested game id from URL query
  id = request.args['id']

  return render_template("gamepage.html", id=id)



if __name__ == "__main__":
  app.run()