from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import RequestType, User
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/request_types", methods=["GET", "POST"])
def request_types(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_all_types(comp)
    else:
        return create_new_type(comp)


@app.route("/<competition>/request_types/<id>", methods=["GET", "POST"])
def request_type(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_type(comp, int(id))
    else:
        return edit_type(comp, int(id))


def show_all_types(comp):
    types = RequestType.query.filter_by(competition_id=comp.id).all()
    users = User.query.filter_by(is_active=True, competition_id=comp.id)\
        .order_by(User.username.asc()).all()
    return render_template("all_types.html", types=types, comp=comp,
                           auth=template(), users=users)


def create_new_type(comp):
    rtype = RequestType()
    rtype.name = request.form["name"]
    rtype.priority = int(request.form["priority"])
    rtype.only_admin = request.form.get("only_admin", False) == "true"
    rtype.send_text = request.form.get("send_text", False) == "true"
    rtype.competition_id = comp.id
    if len(request.form["user_id"]) == 0:
        rtype.user_id = None
    else:
        rtype.user_id = request.form["user_id"]
    db.session.add(rtype)
    db.session.commit()
    return show_all_types()


def show_type(comp, id):
    rtype = RequestType.query.filter_by(
        id=int(id), competition_id=comp.id).one()
    users = User.query.filter_by(
        is_active=True, competition_id=comp.id).order_by(
        User.username.asc()).all()
    return render_template("type.html", rtype=rtype, comp=comp,
                           auth=template(), users=users)


def edit_type(comp, id):
    if request.form["action"] == "delete":
        RequestType.query.filter_by(
            id=int(id), competition_id=comp.id).delete()
    else:
        rtype = RequestType.query.filter_by(
            id=int(id), competition_id=comp.id).one()
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
