# Budget Tracker

A full-stack personal finance web application built with Python and Flask.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey) ![SQLite](https://img.shields.io/badge/Database-SQLite-green) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## What it does

Budget Tracker lets you record, categorise, and visualise your personal finances over time.

- Add income and expense transactions with a category, date, and note
- View a live dashboard with total income, total expenses, and current balance
- Browse, edit, or delete any transaction in your history
- See a time-series chart of daily income, expenses, and running balance — automatically filtered to the last 6 months

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite via SQLAlchemy ORM |
| Templating | Jinja2 |
| Frontend | HTML, CSS |
| Charts | Chart.js |

---

## Project structure

```
budget-tracker/
├── app.py          # Flask routes and business logic
├── models.py       # SQLAlchemy Transaction model
├── templates/      # Jinja2 HTML templates
│   ├── index.html      # Dashboard with charts and summary
│   ├── add.html        # Add transaction form
│   ├── edit.html       # Edit transaction form
│   └── transactions.html # Full transaction history
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
pip install flask flask-sqlalchemy

# Run the app
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser. The SQLite database (`budget.db`) is created automatically on first run.

---

## Features in detail

### Dashboard (`/`)
- Aggregates all transactions into total income, expenses, and net balance
- Builds daily time-series data for a Chart.js line/bar chart
- Filters chart data to the last 6 months if history is longer
- Computes a running cumulative balance across all charted days

### Transaction management
- **Add** (`/add`) — form with amount, type (income/expense), category, date, and optional note
- **Edit** (`/edit/<id>`) — pre-populated form, updates record in place
- **Delete** (`/delete/<id>`) — removes a transaction and redirects to history
- **History** (`/transactions`) — full list ordered by date descending

---

## Planned improvements

- [ ] Deploy as a live web service (coming soon)
- [ ] User authentication — multi-user support with login/logout
- [ ] Monthly summary view and category breakdowns
- [ ] CSV export of transaction history
- [ ] Budget targets — set spending limits per category and track against them
- [ ] REST API layer for future mobile client

---

## Author

**Otis Cassagne**
[github.com/ocass9](https://github.com/ocass9)

