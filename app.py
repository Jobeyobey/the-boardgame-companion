from flask import Flask, render_template, request, redirect

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

    return render_template("index.html", query=query)
  
@app.route("/gamepage")
def gamepage():
  # Get requested game id from URL query
  id = request.args['id']

  return render_template("gamepage.html", id=id)

if __name__ == "__main__":
  app.run()