from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def hello():
  # GET
  if request.method == "GET":
    return render_template("index.html")

  # POST
  if request.method == "POST":
    # Get user query
    query = request.form.get("query")

    return render_template("index.html", query=query)

if __name__ == "__main__":
  app.run()