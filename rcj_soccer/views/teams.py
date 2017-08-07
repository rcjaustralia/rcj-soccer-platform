from flask import request, render_template, redirect, url_for

from rcj_soccer.base import  app, db
from rcj_soccer.models import Team, League
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/teams", methods=["GET", "POST"])
def teams(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_all_teams(comp)
    if request.form.get("bulk-add", False) == "true":
        return create_many_teams(comp)
    else:
        return create_new_team(comp)


@app.route("/<competition>/team/<id>", methods=["GET", "POST"])
def team(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_team(comp, int(id))
    else:
        return edit_team(comp, int(id))


def show_all_teams(comp):
    teams = Team.query.filter_by(is_system=False).filter(
        Team.league.has(competition_id=comp.id)
    ).order_by(
        Team.league_id.asc(),
        Team.name.asc(),
        Team.school.asc()
    ).all()
    leagues = League.query.filter_by(competition_id=comp.id).all()
    return render_template("all_teams.html", teams=teams, comp=comp,
                           leagues=leagues, auth=template(comp.id))


def create_new_team(comp):
    league = League.query.filter_by(
        id=int(request.form["league"]),
        competition_id=comp.id
    ).one()
    team = Team()
    team.name = request.form["name"]
    team.league_id = league.id
    team.school = request.form["school"]
    db.session.add(team)
    db.session.commit()
    return show_all_teams(comp)


def create_many_teams(comp):
    data = request.form["csv-data"].strip().split("\n")
    data = map(lambda s: s.split(","), data)
    league = League.query.filter_by(
        id=int(request.form["league"]),
        competition_id=comp.id
    ).one()
    for row in data:
        team = Team()
        team.name = row[0].strip()
        team.league_id = league.id
        team.school = row[1].strip()
        db.session.add(team)
        db.session.commit()
    return show_all_teams(comp)


def show_team(comp, id):
    team = Team.query.filter_by(id=int(id)).filter(
        Team.league.has(competition_id=comp.id)
    ).one()
    leagues = League.query.filter_by(competition_id=comp.id).all()
    return render_template("team.html", team=team, comp=comp,
                           leagues=leagues, auth=template(comp.id))


def edit_team(comp, id):
    if request.form["action"] == "delete":
        Team.query.filter_by(id=int(id)).filter(
            Team.league.has(competition_id=comp.id)
        ).delete()
    else:
        team = Team.query.filter_by(id=int(id)).filter(
            Team.league.has(competition_id=comp.id)
        ).one()
        league = League.query.filter_by(
            id=int(request.form["league"]),
            competition_id=comp.id
        ).one()
        team.name = request.form["name"]
        team.school = request.form["school"]
        team.league_id = league.id
        team.scrutineer_1 = (request.form.get("scrutineer_1", False) == "true")
        team.scrutineer_2 = (request.form.get("scrutineer_2", False) == "true")
    db.session.commit()
    return show_all_teams(comp)
