from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Transaction, Goal, User
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-dev-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///budget.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_goal_alerts():
    if not current_user.is_authenticated:
        return dict(goal_badge_count=0, goal_badge_colour=None)

    all_goals = Goal.query.filter_by(user_id=current_user.id).all()
    current_month = date.today().month
    current_year = date.today().year

    spending = defaultdict(float)
    for t in Transaction.query.filter_by(user_id=current_user.id, type="expenses").all():
        if t.date.month == current_month and t.date.year == current_year:
            spending[t.category] += t.amount

    badge_count = 0
    badge_colour = None

    for goal in all_goals:
        spent = spending.get(goal.category, 0)
        percentage = (spent / goal.limit) * 100 if goal.limit > 0 else 0

        if percentage >= 100:
            badge_count += 1
            if badge_colour != 'danger':
                badge_colour = 'danger'
        elif percentage >= 75:
            badge_count += 1
            if badge_colour not in ['danger']:
                badge_colour = 'orange'
        elif percentage >= 50:
            badge_count += 1
            if badge_colour not in ['danger', 'orange']:
                badge_colour = 'warning'

    return dict(goal_badge_count=badge_count, goal_badge_colour=badge_colour)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    all_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    income = sum(t.amount for t in all_transactions if t.type == "income")
    expenses = sum(t.amount for t in all_transactions if t.type == "expenses")
    balance = income - expenses

    chart_transactions = sorted(all_transactions, key=lambda t: t.date)

    if chart_transactions:
        latest = chart_transactions[-1].date
        earliest = chart_transactions[0].date
        duration = (latest - earliest).days
        if duration > 180:
            cutoff = latest - timedelta(days=180)
            chart_transactions = [t for t in chart_transactions if t.date >= cutoff]

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
    chart_labels = [d.strftime("%d/%m/%Y") for d in sorted_days]
    income_values = [round(daily_income[d], 2) for d in sorted_days]
    expenses_values = [round(daily_expenses[d], 2) for d in sorted_days]

    cumulative = 0
    running_balance = []
    for d in sorted_days:
        cumulative += daily_balance[d]
        running_balance.append(round(cumulative, 2))

    current_month = date.today().month
    current_year = date.today().year

    monthly_totals_income = defaultdict(float)
    monthly_totals_expenses = defaultdict(float)

    for t in all_transactions:
        key = (t.date.year, t.date.month)
        if t.type == "income":
            monthly_totals_income[key] += t.amount
        else:
            monthly_totals_expenses[key] += t.amount

    past_income = [v for k, v in monthly_totals_income.items() if k != (current_year, current_month)]
    past_expenses = [v for k, v in monthly_totals_expenses.items() if k != (current_year, current_month)]

    predicted_income = round(sum(past_income) / len(past_income), 2) if past_income else 0
    predicted_expenses = round(sum(past_expenses) / len(past_expenses), 2) if past_expenses else 0
    predicted_balance = round(predicted_income - predicted_expenses, 2)

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
        predicted_income=predicted_income,
        predicted_expenses=predicted_expenses,
        predicted_balance=predicted_balance
    )

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        transaction = Transaction(
            amount=float(request.form["amount"]),
            type=request.form["type"],
            category=request.form["category"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            note=request.form.get("note", ""),
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/transactions")
@login_required
def transactions():
    all_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template("transactions.html", transactions=all_transactions)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        return redirect(url_for("index"))
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for("transactions"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        return redirect(url_for("index"))
    if request.method == "POST":
        transaction.amount = float(request.form["amount"])
        transaction.type = request.form["type"]
        transaction.category = request.form["category"]
        transaction.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        transaction.note = request.form.get("note", "")
        db.session.commit()
        return redirect(url_for("transactions"))
    return render_template("edit.html", transaction=transaction)

@app.route("/goals")
@login_required
def goals():
    all_goals = Goal.query.filter_by(user_id=current_user.id).all()
    current_month = date.today().month
    current_year = date.today().year

    spending = defaultdict(float)
    for t in Transaction.query.filter_by(user_id=current_user.id, type="expenses").all():
        if t.date.month == current_month and t.date.year == current_year:
            spending[t.category] += t.amount

    goal_progress = []
    for goal in all_goals:
        spent = spending.get(goal.category, 0)
        percentage = min(round((spent / goal.limit) * 100), 100)
        goal_progress.append({
            "goal": goal,
            "spent": round(spent, 2),
            "percentage": percentage,
            "over": spent > goal.limit
        })

    return render_template("goals.html", goal_progress=goal_progress)

@app.route("/goals/add", methods=["GET", "POST"])
@login_required
def add_goal():
    if request.method == "POST":
        goal = Goal(
            category=request.form["category"],
            limit=float(request.form["limit"]),
            period=request.form["period"],
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        return redirect(url_for("goals"))
    return render_template("add_goal.html")

@app.route("/goals/delete/<int:id>")
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        return redirect(url_for("goals"))
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for("goals"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)