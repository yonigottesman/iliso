from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dash
from config import Config


app = dash.Dash(__name__)
server = app.server # the Flask app
server.config.from_object(Config)
# server.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
# server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server)
migrate = Migrate(server, db)

from app import routes

