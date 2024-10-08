from . import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True, unique=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150))
    image = db.Column(db.LargeBinary)
    provider = db.Column(db.String(50), nullable=False)
    



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))