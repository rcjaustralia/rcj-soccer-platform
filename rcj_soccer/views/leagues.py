from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import League
from rcj_soccer.views.auth import check_user, template


@app.route("/leagues", methods=["GET", "POST"])
def leagues():
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_leagues()
    else:
        return create_new_league()


@app.route("/league/<id>", methods=["GET", "POST"])
def league(id):
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_league(int(id))
    else:
        return edit_league(int(id))


def show_all_leagues():
    leagues = League.query.all()
    return render_template("all_leagues.html",
                           leagues=leagues, auth=template())


def create_new_league():
    league = League()
    league.name = request.form["name"]
    league.areas = int(request.form["fields"])
    league.duration = int(request.form["duration"])
    db.session.add(league)
    db.session.commit()
    return show_all_leagues()


def show_league(id):
    league = League.query.filter_by(id=int(id)).one()
    return render_template("league.html", league=league, auth=template())


def edit_league(id):
    if request.form["action"] == "delete":
        League.query.filter_by(id=int(id)).delete()
    else:
        league = League.query.filter_by(id=int(id)).one()
        league.name = request.form["name"]
        league.areas = int(request.form["fields"])
        league.duration = int(request.form["duration"])
        league.requirements = request.form["requirements"]
    db.session.commit()
    return show_all_leagues()
