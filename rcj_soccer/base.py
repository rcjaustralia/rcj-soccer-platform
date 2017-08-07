from flask import Flask, send_from_directory
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from rcj_soccer.util import config
from rcj_soccer import templates, static

import logging
import os
logger = logging.getLogger(__name__)


app = Flask(__name__, template_folder=templates.location,
            static_folder=static.location)
logger.info("DB is {}", config.get("database", "connection"))
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("database", "connection")
app.secret_key = config.get("secrets", "key")

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"),
                               "favicon.ico",
                               mimetype="image/vnd.microsoft.icon")
