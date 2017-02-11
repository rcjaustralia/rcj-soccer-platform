from app import app, db
from models import Team
from flask import request, render_template, redirect, url_for
from auth import check_user, template


@app.route("/scrutineer", methods=["GET", "POST"])
def scrutineer_teams():
    if not check_user(False):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_teams()


@app.route("/scrutineer/delete_all", methods=["GET", "POST"])
def scrutineer_delete_all():
    if not check_user(False):
        return redirect(url_for("login"))
    if request.method == "GET":
        teams = Team.query.filter_by(
            is_system=False).filter_by(is_bye=False).all()
        for team in teams:
            team.scrutineer_1 = False
            team.scrutineer_2 = False
            db.session.add(team)
        db.session.commit()
        return redirect(url_for("scrutineer_teams"))


@app.route("/scrutineer/<id>", methods=["GET", "POST"])
def scrutineer(id):
    if not check_user(False):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_team(int(id))
    else:
        return save_team(int(id))


@app.route("/scrutineer/<id>/label/<n>", methods=["GET"])
def label(id, n):
    if not check_user(False):
        return redirect(url_for("login"))
    team = Team.query.filter_by(id=int(id)).one()
    return render_template("label.html", robot_number=int(n), team=team)


def show_all_teams():
    teams = Team.query.filter((Team.is_bye == False) &
                              (Team.is_system == False)).filter(
        (Team.scrutineer_1 == False) |
        (Team.scrutineer_2 == False)
    ).order_by(Team.league_id.asc(), Team.name.asc()).all()
    return render_template("all_scrutineer.html", teams=teams, auth=template())


def show_team(id):
    team = Team.query.filter_by(id=int(id)).one()
    return render_template("scrutineer.html", team=team, auth=template())


def save_team(id):
    team = Team.query.filter_by(id=int(id)).one()
    team.scrutineer_1 = (request.form.get("scrutineer_1", False) == "true")
    team.scrutineer_2 = (request.form.get("scrutineer_2", False) == "true")
    db.session.commit()
    return show_all_teams()
