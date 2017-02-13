from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import RequestType, User
from rcj_soccer.views.auth import check_user, template


@app.route("/request_types", methods=["GET", "POST"])
def request_types():
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_types()
    else:
        return create_new_type()


@app.route("/request_types/<id>", methods=["GET", "POST"])
def request_type(id):
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_type(int(id))
    else:
        return edit_type(int(id))


def show_all_types():
    types = RequestType.query.all()
    users = User.query.filter_by(is_active=True).order_by(
        User.username.asc()).all()
    return render_template("all_types.html", types=types,
                           auth=template(), users=users)


def create_new_type():
    rtype = RequestType()
    rtype.name = request.form["name"]
    rtype.priority = int(request.form["priority"])
    rtype.only_admin = request.form.get("only_admin", False) == "true"
    rtype.send_text = request.form.get("send_text", False) == "true"
    if len(request.form["user_id"]) == 0:
        rtype.user_id = None
    else:
        rtype.user_id = request.form["user_id"]
    db.session.add(rtype)
    db.session.commit()
    return show_all_types()


def show_type(id):
    rtype = RequestType.query.filter_by(id=int(id)).one()
    users = User.query.filter_by(is_active=True).order_by(
        User.username.asc()).all()
    return render_template("type.html", rtype=rtype,
                           auth=template(), users=users)


def edit_type(id):
    if request.form["action"] == "delete":
        RequestType.query.filter_by(id=int(id)).delete()
    else:
        rtype = RequestType.query.filter_by(id=int(id)).one()
        rtype.name = request.form["name"]
        rtype.only_admin = request.form.get("only_admin", False) == "true"
        rtype.priority = int(request.form["priority"])
        rtype.send_text = request.form.get("send_text", False) == "true"
        if len(request.form["user_id"]) == 0:
            rtype.user_id = None
        else:
            rtype.user_id = request.form["user_id"]
    db.session.commit()
    return show_all_types()
