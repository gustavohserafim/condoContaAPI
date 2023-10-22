import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, extract


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db_file = 'database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_file)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    accounts = db.relationship('Account', backref='user', lazy=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<User {self.id}>'


class AccountTypeEnum:
    corrente = 1
    poupanca = 2


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), server_onupdate=db.func.now())
    transactions = db.relationship('Transaction', backref='account', lazy=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return f'<Account {self.id}>'


class TransactionTypeEnum:
    tin = 1
    tou = 2


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Numeric(10, 2), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), server_onupdate=db.func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Transaction {self.id}>'


with app.app_context():
    # Inicialização do BD
    if not os.path.exists(db_file):
        db.create_all()
        user = User(name='Condominio 1')
        account1 = Account(type=AccountTypeEnum.corrente, balance=1000, user=user)
        account2 = Account(type=AccountTypeEnum.poupanca, balance=1, user=user)
        transaction1 = Transaction(description="Deposito inicial CC", value=1000, balance_after=1000, account=account1, type=TransactionTypeEnum.tin)
        transaction2 = Transaction(description="Deposito inicial CP", value=1, balance_after=1, account=account2, type=TransactionTypeEnum.tou)
        db.session.add(user)
        db.session.add(account1)
        db.session.add(account2)
        db.session.add(transaction1)
        db.session.add(transaction2)
        db.session.commit()


@app.route("/api/account/<int:id>/balance")
def get_balance(id):
    balance = db.get_or_404(Account, id)
    return jsonify(balance.as_dict())


@app.route("/api/account/<int:id>/statement")
def get_statement(id):
    current_month = 10
    transactions = db.session.query(Transaction).filter(extract('month', Transaction.created_at) == current_month, Transaction.account_id == id).all()
    return jsonify({"transactions": [t.as_dict() for t in transactions]})


@app.route("/api/account/<int:id>/transfer", methods=['POST'])
def transfer(id):
    r = request.get_json()
    target_id = r.get("target_id")
    value = r.get("value")
    description = r.get("description")

    source_account = db.get_or_404(Account, id)
    target_account = db.get_or_404(Account, target_id)
    if source_account and target_account and source_account != target_account:
        if source_account.balance >= value:
            try:
                source_balance = source_account.balance - value
                target_balance = target_account.balance + value
                tout = Transaction(description=description, value=value, balance_after=source_balance, account=source_account, type=TransactionTypeEnum.tou)
                tin = Transaction(description=description, value=value, balance_after=target_balance, account=target_account, type=TransactionTypeEnum.tin)
                source_account.balance = source_balance
                target_account.balance = target_balance
                db.session.add(tin)
                db.session.add(tout)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
                return jsonify("Erro ao transferir"), 400
            else:
                return jsonify(source_account.as_dict())
        else:
            return jsonify("Saldo insfuciente"), 400
    else:
        return jsonify("Conta de origem ou destino inexistente"), 400


