from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
