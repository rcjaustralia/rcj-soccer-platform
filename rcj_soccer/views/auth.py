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
            username=request.form["username"].lower().strip(),
            is_active=True
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
    comp = get_competition(competition)
    user = User.query.filter_by(
        username=username.lower(), competition_id=comp.id, is_active=True
    ).first()
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
    logger.info("SENDING SMS TOKEN: {0}".format(token))
    sms.get_provider().send(
        phone,
        str(token) + " is your security code for logging into RoboCup Junior")


@app.route("/<competition>/logout")
def logout(competition):
    comp = get_competition(competition)
    user = check_user(comp.id)["user"]
    if user:
        user.session_token = None
        user.session_expires = None
        db.session.commit()
    return redirect(url_for("results", competition=comp.id))


def check_user(comp_id):
    user = None
    is_valid = False
    is_admin = False

    if "username" in session and "token" in session:
        user = User.query.filter_by(
            username=session["username"]
        ).filter_by(
            competition_id=comp_id
        ).filter_by(
            is_active=True
        ).first()

    if user is not None and user.session_token == session["token"]\
            and user.session_expires is not None\
            and datetime.now() <= user.session_expires:
        is_valid = True

    if is_valid and user.is_admin:
        is_admin = True

    if not is_valid:
        is_valid = User.query.filter_by(
            competition_id=comp_id
        ).filter_by(
            is_active=True
        ).count() == 0

    if not is_admin:
        is_admin = User.query.filter_by(
            competition_id=comp_id
        ).filter_by(
            is_admin=True
        ).filter_by(
            is_active=True
        ).count() == 0

    return {
        "is_logged_in": is_valid,
        "is_admin": is_admin,
        "user": user
    }


def template(comp_id):
    user_info = check_user(comp_id)

    return {
        "is_logged_in": user_info["is_logged_in"],
        "is_admin": user_info["is_admin"],
        "year": datetime.utcnow().year
    }
