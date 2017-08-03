from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import Team
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/scrutineer", methods=["GET", "POST"])
def scrutineer_teams(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, False):
        return redirect(url_for("login"), competition=comp.id)
    if request.method == "GET":
        return show_all_teams(comp)


@app.route("/<competition>/scrutineer/delete_all", methods=["GET", "POST"])
def scrutineer_delete_all():
    comp = get_competition(competition)
    if not check_user(comp.id, False):
        return redirect(url_for("login"), competition=comp.id)
    if request.method == "GET":
        teams = Team.query.filter_by(
            is_system=False, is_bye=False
        ).filter(
            Team.league.has(competition_id=comp.id)
        ).all()
        for team in teams:
            team.scrutineer_1 = False
            team.scrutineer_2 = False
            db.session.add(team)
        db.session.commit()
        return redirect(url_for("scrutineer_teams", competition=comp.id))


@app.route("/<competition>/scrutineer/<id>", methods=["GET", "POST"])
def scrutineer(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id, False):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_team(comp, int(id))
    else:
        return save_team(comp, int(id))


@app.route("/<competition>/scrutineer/<id>/label/<n>", methods=["GET"])
def label(competition, id, n):
    comp = get_competition(competition)
    if not check_user(comp.id, False):
        return redirect(url_for("login", competition=comp.id))
    team = Team.query.filter_by(id=int(id)).filter(
        Team.league.has(competition_id=comp.id)
    ).one()
    return render_template("label.html", robot_number=int(n), team=team,
                           comp=comp)


def show_all_teams(comp):
    teams = Team.query.filter(
        (Team.is_bye == False) &
        (Team.is_system == False) &
        (Team.league.has(competition_id=comp.id))
    ).filter(
        (Team.scrutineer_1 == False) |
        (Team.scrutineer_2 == False)
    ).order_by(Team.league_id.asc(), Team.name.asc()).all()
    return render_template("all_scrutineer.html", teams=teams, auth=template())


def show_team(comp, id):
    team = Team.query.filter_by(id=int(id)).one()
    return render_template("scrutineer.html", team=team, auth=template(),
                           comp=comp)


def save_team(comp, id):
    team = Team.query.filter_by(id=int(id)).one()
    team.scrutineer_1 = (request.form.get("scrutineer_1", False) == "true")
    team.scrutineer_2 = (request.form.get("scrutineer_2", False) == "true")
    db.session.commit()
    return show_all_teams(comp)
