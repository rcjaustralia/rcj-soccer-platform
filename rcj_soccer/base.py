from flask import Flask, redirect, url_for
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import logging; logger = logging.getLogger(__name__)
import jinja2
from rcj_soccer.util import config
from rcj_soccer import templates, static

app = Flask(__name__, template_folder=templates.location, static_folder=static.location)
logger.info("DB is {}", config.get("database", "connection"))
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("database", "connection")
app.secret_key = config.get("secrets", "key")

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.route("/")
def index():
    return redirect(url_for("results"))
