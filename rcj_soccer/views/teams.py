from flask import request, render_template, redirect, url_for

from rcj_soccer.base import  app, db
from rcj_soccer.models import Team, League
from rcj_soccer.views.auth import check_user, template


@app.route("/teams", methods=["GET", "POST"])
def teams():
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_teams()
    if request.form.get("bulk-add", False) == "true":
        return create_many_teams()
    else:
        return create_new_team()


@app.route("/team/<id>", methods=["GET", "POST"])
def team(id):
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_team(int(id))
    else:
        return edit_team(int(id))


def show_all_teams():
    teams = Team.query.filter_by(is_system=False).order_by(
        Team.league_id.asc(), Team.name.asc(), Team.school.asc()).all()
    leagues = League.query.all()
    return render_template("all_teams.html", teams=teams,
                           leagues=leagues, auth=template())


def create_new_team():
    team = Team()
    team.name = request.form["name"]
    team.league_id = int(request.form["league"])
    team.school = request.form["school"]
    db.session.add(team)
    db.session.commit()
    return show_all_teams()


def create_many_teams():
    data = request.form["csv-data"].strip().split("\n")
    data = map(lambda s: s.split(","), data)
    for row in data:
        team = Team()
        team.name = row[0].strip()
        team.league_id = int(request.form["league"])
        team.school = row[1].strip()
        db.session.add(team)
        db.session.commit()
    return show_all_teams()


def show_team(id):
    team = Team.query.filter_by(id=int(id)).one()
    leagues = League.query.all()
    return render_template("team.html", team=team,
                           leagues=leagues, auth=template())


def edit_team(id):
    if request.form["action"] == "delete":
        Team.query.filter_by(id=int(id)).delete()
    else:
        team = Team.query.filter_by(id=int(id)).one()
        team.name = request.form["name"]
        team.school = request.form["school"]
        team.league_id = int(request.form["league"])
        team.scrutineer_1 = (request.form.get("scrutineer_1", False) == "true")
        team.scrutineer_2 = (request.form.get("scrutineer_2", False) == "true")
    db.session.commit()
    return show_all_teams()
