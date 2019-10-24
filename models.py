from passlib.hash import sha256_crypt
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    has_voted = db.Column(db.Boolean, unique=False, default=False)
    is_privileged = db.Column(db.Boolean, unique=False, default=False)


    def __init__(self, email, password, is_privileged=False):
        self.email = email
        self.password = sha256_crypt.hash(password)
        self.is_privileged = is_privileged

    def check_password(self, password):
        return sha256_crypt.verify(password, self.password)

    def __repr__(self):
        return f"{self.email}"

# Hook used by flask-login to retrieve a user's record
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    votes = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.votes = 0

    def __repr__(self):
        return f"{self.name}"
