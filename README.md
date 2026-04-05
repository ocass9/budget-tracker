# Budget Tracker

A full-stack personal finance web application with user authentication, transaction management, budget goals, and financial visualisation.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey) ![SQLite](https://img.shields.io/badge/Database-SQLite-green) ![Auth](https://img.shields.io/badge/Auth-Flask--Login-orange) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## What it does

Budget Tracker lets multiple users register, log in, and independently manage their personal finances.

- **Accounts**: register and log in with your own secure account; all data is isolated per user
- **Transactions**: add, edit, and delete income and expense entries with category, date, and note
- **Dashboard**: live summary of total income, total expenses, and current balance
- **Charts**: time-series visualisation of daily income, expenses, and running balance (last 6 months)
- **Goals**: set per-category spending limits by period (weekly/monthly) and track actual spend against them

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Authentication | Flask-Login (UserMixin, session management) |
| Database | SQLite via SQLAlchemy ORM |
| Templating | Jinja2 |
| Frontend | HTML, CSS, Chart.js |

---

## Data model

Three relational models, all user-scoped:

```
User
├── id, username, email, password
├── → transactions (one-to-many)
└── → goals (one-to-many)

Transaction
├── id, amount, type (income/expense), category, date, note
└── user_id (FK → User)

Goal
├── id, category, limit, period (weekly/monthly)
└── user_id (FK → User)
```

---

## Project structure

```
budget-tracker/
├── app.py          # Flask routes, business logic, auth flows
├── models.py       # SQLAlchemy models: User, Transaction, Goal
├── templates/      # Jinja2 HTML templates
│   ├── index.html          # Dashboard with charts and summary
│   ├── add.html            # Add transaction form
│   ├── edit.html           # Edit transaction form
│   ├── transactions.html   # Full transaction history
│   ├── login.html          # Login page
│   └── register.html       # Registration page
├── .gitignore
└── README.md
```

---

## Running locally

**Prerequisites:** Python 3.8+

```bash
# Clone the repo
git clone https://github.com/ocass9/budget-tracker.git
cd budget-tracker

# Install dependencies
pip install flask flask-sqlalchemy flask-login

# Run the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000). The SQLite database is created automatically on first run. Register an account to get started.

---

## Features in detail

### Authentication
- User registration with username, email, and password
- Session-based login/logout via Flask-Login
- All transactions and goals are scoped to the authenticated user: no data leakage between accounts

### Dashboard (`/`)
- Aggregates the current user's transactions into income, expenses, and net balance
- Builds daily time-series data for Chart.js visualisation
- Rolling 6-month window filter if transaction history is longer
- Cumulative running balance computed server-side

### Transaction management
- **Add**: amount, type (income/expense), category, date, optional note
- **Edit**: pre-populated form, updates record in place
- **Delete**: removes transaction, redirects to history
- **History**: full list ordered by date descending, scoped to current user

### Budget Goals
- Set a spending limit for any category over a chosen period (weekly or monthly)
- Track actual spend against each goal from your transaction history

---

## Planned / in progress

- [ ] Deploy as a live hosted web service (coming soon)
- [ ] Password hashing (bcrypt)
- [ ] **AI-powered insights via Ollama**: locally-hosted LLM integration for natural language spending analysis, anomaly detection, and personalised budget recommendations without sending data to third-party APIs
- [ ] Goal progress indicators on dashboard
- [ ] CSV export of transaction history
- [ ] Monthly summary and category breakdown views
- [ ] Mobile-responsive layout

---

## Author

**Otis Cassagne**
[github.com/ocass9](https://github.com/ocass9)
