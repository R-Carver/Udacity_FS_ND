from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import setup_db, Player, Team, db

app = Flask(__name__)
setup_db(app)
migrate = Migrate(app, db)