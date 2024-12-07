from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import base64
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_pymongo import PyMongo
import os
    


load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRESQL_DB")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
    app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
    app.config["MONGO_URI"] = "mongodb://localhost:27017/skilldatabase"

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    mongo.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = 'main.login'



    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()


    return app
