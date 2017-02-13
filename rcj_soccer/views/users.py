import re

from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import User
from rcj_soccer.util import sms
from rcj_soccer.views.auth import check_user, template


@app.route("/users", methods=["GET", "POST"])
def users():
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_users()
    else:
        return create_new_user()


@app.route("/user/<username>", methods=["GET", "POST"])
def user(username):
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_user(username)
    else:
        return edit_user(username)


def show_all_users():
    users = User.query.filter_by(is_active=True).order_by(
        User.username.asc()).all()
    return render_template("all_users.html", users=users, auth=template())


def create_new_user():
    user = User()
    user.username = request.form["username"].lower().strip()
    user.phone = re.sub(r"([^0-9\+]+)", "", request.form["phone"])
    db.session.add(user)
    db.session.commit()

    sms.send(user.phone,
             "Welcome to the RCJ soccer platform at http://robocup.tech" +
             " Your username is: " + user.username)

    return show_all_users()


def show_user(username):
    user = User.query.filter_by(username=username).one()
    return render_template("user.html", user=user, auth=template())


def edit_user(username):
    user = User.query.filter_by(username=username).one()
    user.username = request.form["username"]
    user.phone = request.form["phone"]
    user.session_expires = None
    user.session_token = None
    user.auth_token = None
    user.auth_expires = None
    user.is_admin = (request.form.get("admin", False) == "true")
    user.is_active = (request.form["action"] != "delete")
    db.session.commit()
    return show_all_users()
