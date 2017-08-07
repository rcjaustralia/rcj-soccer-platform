import re

from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import User
from rcj_soccer.util import sms
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/users", methods=["GET", "POST"])
def users(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_all_users(comp)
    else:
        return create_new_user(comp)


@app.route("/<competition>/user/<username>", methods=["GET", "POST"])
def user(competition, username):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_user(comp, username)
    else:
        return edit_user(comp, username)


def show_all_users(comp):
    users = User.query.filter_by(
        is_active=True,
        competition_id=comp.id
    ).order_by(
        User.username.asc()
    ).all()
    return render_template("all_users.html", users=users,
                           auth=template(comp.id), comp=comp)


def create_new_user(comp):
    user = User()
    user.username = request.form["username"].lower().strip()
    user.phone = re.sub(r"([^0-9\+]+)", "", request.form["phone"])
    user.competition_id = comp.id
    db.session.add(user)
    db.session.commit()

    sms.send(user.phone,
             "Welcome to the RCJ soccer platform at http://soccer.rcja.org" +
             " Your username is: " + user.username)

    return show_all_users(comp)


def show_user(comp, username):
    user = User.query.filter_by(
        username=username,
        competition_id=comp.id
    ).one()
    return render_template("user.html", user=user, auth=template(comp.id),
                           comp=comp)


def edit_user(comp, username):
    user = User.query.filter_by(
        username=username,
        competition_id=comp.id
    ).one()
    user.username = request.form["username"]
    user.phone = request.form["phone"]
    user.session_expires = None
    user.session_token = None
    user.auth_token = None
    user.auth_expires = None
    user.is_admin = (request.form.get("admin", False) == "true")
    user.is_active = (request.form["action"] != "delete")
    db.session.commit()
    return show_all_users(comp)
