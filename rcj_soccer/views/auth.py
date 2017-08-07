import hashlib
import random
import logging
from datetime import datetime, timedelta

from flask import request, render_template, redirect, session, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import User
from rcj_soccer.util import sms
from rcj_soccer.views.competition import get_competition

logger = logging.getLogger(__name__)


@app.route("/<competition>/login", methods=["GET", "POST"])
def login(competition):
    if request.method == "GET":
        return show_username_form(get_competition(competition))
    else:
        comp = get_competition(competition)
        user = User.query.filter_by(
            competition_id=comp.id,
            username=request.form["username"]
        ).first()
        if user is None:
            return show_username_form(comp)
        else:
            user.auth_token = random.randint(100000, 999999)
            user.auth_expires = datetime.now() + timedelta(minutes=8)
            db.session.commit()
            send_sms(user.phone, user.auth_token)
            return show_token_form(user.username, user.phone, comp)


@app.route("/<competition>/login/<username>", methods=["POST"])
def login_check(competition, username):
    user = User.query.filter_by(username=username).first()
    comp = get_competition(competition)
    if user is None:
        return show_username_form(comp)
    else:
        token = int(request.form["token"])
        if token == user.auth_token and datetime.now() <= user.auth_expires:
            user.session_token = hashlib.sha512(("".join(
                map(str, [user.username, user.phone, datetime.now(), token])
            )).encode("utf-8")).hexdigest()
            user.session_expires = datetime.now() + timedelta(hours=12)
            user.auth_token = None
            user.auth_expires = None
            db.session.commit()
            session["username"] = user.username
            session["token"] = user.session_token
            return render_template("login_done.html",
                                   auth=template(comp.id), comp=comp)
        else:
            db.session.commit()
            return show_token_form(user.username, user.phone, comp)


def show_token_form(username, phone, comp):
    phone = ("*" * (len(phone) - 3)) + phone[-3:]
    return render_template("login_token.html", username=username,
                           phone=phone, auth=template(comp.id), comp=comp)


def show_username_form(comp):
    return render_template("login_username.html", auth=template(comp.id),
                           comp=comp)


def send_sms(phone, token):
    logger.info("SENDING SMS: {}", token)
    sms.send(
        phone,
        "Your security code for logging into RoboCup Junior is: " + str(token))


@app.route("/<competition>/logout")
def logout(competition):
    comp = get_competition(competition)
    user = check_user(comp.id)
    if user:
        user.session_token = None
        user.session_expires = None
        db.session.commit()
    return redirect(url_for("results", competition=comp.id))


def check_user(comp_id, admin=False):
    if User.query.filter_by(competition_id=comp_id).filter_by(
            is_active=True).count() == 0:
        return True

    if "username" not in session or "token" not in session:
        return False
    user = User.query.filter_by(
        username=session["username"]).filter_by(
        competition_id=comp_id).filter_by(
        is_active=True).first()
    if user is None or user.session_token != session["token"]\
            or user.session_expires is None\
            or datetime.now() > user.session_expires:
        return False
    if admin and (not user.is_admin and User.query.filter_by(is_active=True)
                  .filter_by(is_admin=True).filter_by(competition_id=comp_id)
                  .count() > 0):
        return False
    return user


def template(comp_id, fixed=False):
    return {
        "is_logged_in": check_user(comp_id),
        "is_admin": check_user(comp_id, True),
        "fixed_navbar": fixed
    }
