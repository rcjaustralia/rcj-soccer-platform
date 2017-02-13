from flask import Flask, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import config

app = Flask(__name__)
print "DB is", config.get("database", "connection")
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("database", "connection")
app.secret_key = config.get("secrets", "key")

app.jinja_env.cache = {}

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route("/")
def index():
    return redirect(url_for("results"))
