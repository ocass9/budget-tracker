from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    date = db.column(db.Date, nullable=False)
    note = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.type} ${self.amount} - {self.category}>"