from app import app, db
from models import User
from flask import request, render_template, redirect, session, url_for
import random
import hashlib
from datetime import datetime, timedelta
import sms


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return show_username_form()
    else:
        user = User.query.filter_by(username=request.form["username"]).first()
        if user is None:
            return show_username_form()
        else:
            user.auth_token = random.randint(100000, 999999)
            user.auth_expires = datetime.now() + timedelta(minutes=8)
            db.session.commit()
            send_sms(user.phone, user.auth_token)
            return show_token_form(user.username, user.phone)


@app.route("/login/<username>", methods=["POST"])
def login_check(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return show_username_form()
    else:
        token = int(request.form["token"])
        if token == user.auth_token and datetime.now() <= user.auth_expires:
            user.session_token = hashlib.sha512("".join(
                map(str, [user.username, user.phone, datetime.now(), token])
            )).hexdigest()
            user.session_expires = datetime.now() + timedelta(hours=12)
            user.auth_token = None
            user.auth_expires = None
            db.session.commit()
            session["username"] = user.username
            session["token"] = user.session_token
            return render_template("login_done.html", auth=template())
        else:
            db.session.commit()
            return show_token_form(user.username, user.phone)


def show_token_form(username, phone):
    phone = ("*" * (len(phone) - 3)) + phone[-3:]
    return render_template("login_token.html", username=username,
                           phone=phone, auth=template())


def show_username_form():
    return render_template("login_username.html", auth=template())


def send_sms(phone, token):
    print "SENDING SMS: ", token
    sms.send(
        phone,
        "Your security code for logging into RoboCup Junior is: " + str(token))


@app.route("/logout")
def logout():
    user = check_user()
    if user:
        user.session_token = None
        user.session_expires = None
        db.session.commit()
    return redirect(url_for("index"))


def check_user(admin=False):
    if User.query.filter_by(is_active=True).count() == 0:
        return True

    if "username" not in session or "token" not in session:
        return False
    user = User.query.filter_by(
        username=session["username"]).filter_by(is_active=True).first()
    if user is None or user.session_token != session["token"]\
            or user.session_expires is None\
            or datetime.now() > user.session_expires:
        return False
    if admin and (not user.is_admin and User.query.filter_by(is_active=True)
                  .filter_by(is_admin=True).count() > 0):
        return False
    return user


def template(fixed=False):
    return {
        "is_logged_in": check_user(),
        "is_admin": check_user(True),
        "fixed_navbar": fixed
    }
