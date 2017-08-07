from flask import request, render_template, redirect, url_for
import logging

from rcj_soccer.base import app, db
from rcj_soccer.models import League
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition

logger = logging.getLogger(__name__)


@app.route("/<competition>/leagues", methods=["GET", "POST"])
def leagues(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_all_leagues(comp)
    else:
        return create_new_league(comp)


@app.route("/<competition>/league/<id>", methods=["GET", "POST"])
def league(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_league(comp, int(id))
    else:
        return edit_league(comp, int(id))


def show_all_leagues(comp):
    leagues = League.query.filter_by(competition_id=comp.id).all()
    return render_template("all_leagues.html",
                           leagues=leagues, auth=template(comp.id), comp=comp)


def create_new_league(comp):
    league = League()
    league.name = request.form["name"]
    league.areas = int(request.form["fields"])
    league.duration = int(request.form["duration"])
    league.competition_id = comp.id
    db.session.add(league)
    db.session.commit()
    return show_all_leagues(comp)


def show_league(comp, id):
    league = League.query.filter_by(id=int(id)).one()
    return render_template("league.html", league=league,
                           auth=template(comp.id), comp=comp)


def edit_league(comp, id):
    if request.form["action"] == "delete":
        League.query.filter_by(id=int(id)).delete()
    else:
        league = League.query.filter_by(id=int(id)).one()
        league.name = request.form["name"]
        league.areas = int(request.form["fields"])
        league.duration = int(request.form["duration"])
        league.requirements = request.form["requirements"]
    db.session.commit()
    return show_all_leagues(comp)
