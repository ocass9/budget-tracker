from flask import Flask, render_template, request, redirect, url_for
from models import db, Transaction
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def index():
    return "Hello Flask"

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        transaction = Transaction(
            amount=float(request.form["amount"]),
            type=request.form["type"],
            category=request.form["category"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            note=request.form.get("note","")
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
