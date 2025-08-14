from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/user/Raman")
def home():
    return render_template("index.html",name="Raman")

if __name__ == "__main__":
    app.run(debug = True)

    