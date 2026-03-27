from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
from models import db, Transaction
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def index():
    all_transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    income = sum(t.amount for t in all_transactions if t.type == "income")
    expenses = sum(t.amount for t in all_transactions if t.type == "expenses")
    balance = income - expenses

    # Sort oldest to newest
    chart_transactions = sorted(all_transactions, key=lambda t: t.date)

    # Cut to last 6 months if needed
    if chart_transactions:
        latest = chart_transactions[-1].date
        earliest = chart_transactions[0].date
        duration = (latest - earliest).days
        if duration > 180:
            cutoff = latest - timedelta(days=180)
            chart_transactions = [t for t in chart_transactions if t.date >= cutoff]

    # Build daily buckets
    daily_income = defaultdict(float)
    daily_expenses = defaultdict(float)
    daily_balance = defaultdict(float)

    for t in chart_transactions:
        if t.type == "income":
            daily_income[t.date] += t.amount
            daily_balance[t.date] += t.amount
        else:
            daily_expenses[t.date] += t.amount
            daily_balance[t.date] -= t.amount

    sorted_days = sorted(set(daily_income.keys()) | set(daily_expenses.keys()))

    # Build chart labels and daily values
    chart_labels = [d.strftime("%d/%m/%Y") for d in sorted_days]
    income_values = [round(daily_income[d], 2) for d in sorted_days]
    expenses_values = [round(daily_expenses[d], 2) for d in sorted_days]

    # Build running balance with smoothing
    cumulative = 0
    raw_balance = []
    for d in sorted_days:
        cumulative += daily_balance[d]
        raw_balance.append(round(cumulative, 2))

    def smooth(values, window=3):
        smoothed = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            avg = sum(values[start:i+1]) / len(values[start:i+1])
            smoothed.append(round(avg, 2))
        return smoothed

    running_balance = smooth(raw_balance)

    return render_template(
        "index.html",
        transactions=all_transactions,
        income=round(income, 2),
        expenses=round(expenses, 2),
        balance=round(balance, 2),
        chart_labels=chart_labels,
        income_values=income_values,
        expenses_values=expenses_values,
        running_balance=running_balance,
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        transaction = Transaction(
            amount=float(request.form["amount"]),
            type=request.form["type"],
            category=request.form["category"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            note=request.form.get("note", "")
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/transactions")
def transactions():
    all_transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template("transactions.html", transactions=all_transactions)

@app.route("/delete/<int:id>")
def delete(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for("transactions"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    if request.method == "POST":
        transaction.amount = float(request.form["amount"])
        transaction.type = request.form["type"]
        transaction.category = request.form["category"]
        transaction.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        transaction.note = request.form.get("note", "")
        db.session.commit()
        return redirect(url_for("transactions"))
    return render_template("edit.html", transaction=transaction)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)