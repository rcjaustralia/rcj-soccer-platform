from dateutil.parser import parse
from flask import request, render_template, redirect, url_for
import logging

from rcj_soccer.base import app, db
from rcj_soccer.models import SoccerGame, Team, League
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition

logger = logging.getLogger(__name__)


@app.route("/<competition>/games", methods=["GET", "POST"])
def games(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_games(comp)
    else:
        return create_new_game(comp)


@app.route("/<competition>/games/delete_all", methods=["GET", "POST"])
def games_delete_all(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        db.session.query(SoccerGame).filter(SoccerGame.game_finished == False)\
            .filter(SoccerGame.league.competition_id == comp.id).delete()
        db.session.commit()
        return redirect(url_for("games", competition=comp.id))


@app.route("/<competition>/games/populate_all", methods=["GET", "POST"])
def games_populate_all(competition):
    comp = get_competition(competition)
    if not check_user(comp.id):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        calculate_system_teams(comp)
        return redirect(url_for("games", competition=comp.id))


@app.route("/<competition>/game/<id>", methods=["GET", "POST"])
def game(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_game(comp, int(id))
    else:
        return edit_game(comp, int(id))


def show_all_games(competition):
    games = SoccerGame.query.filter(
        SoccerGame.league.competition_id == competition.id
    ).all()
    leagues = League.query.filter_by(competition_id=competition.id).all()
    teams = Team.query.filter(
        Team.league.competition_id == competition.id
    ).all()
    return render_template("all_games.html", games=games, leagues=leagues,
                           teams=teams, auth=template(), comp=competition)


def create_new_game(comp):
    game = SoccerGame()
    game.league_id = int(request.form["league"])
    game.home_team_id = int(request.form["home_team"])
    game.away_team_id = int(request.form["away_team"])
    game.field = int(request.form["field"])
    game.round = int(request.form["round"])
    game.scheduled_time = parse(request.form["scheduled_time"])
    db.session.add(game)
    db.session.commit()
    return show_all_games(comp)


def show_game(comp, id):
    game = SoccerGame.query.filter_by(id=int(id)).one()
    leagues = League.query.filter_by(competition_id=comp.id).all()
    teams = Team.query.filter(
        Team.league.competition_id == comp.id
    ).all()
    return render_template("game.html", game=game, teams=teams,
                           leagues=leagues, auth=template(), comp=comp)


def edit_game(comp, id):
    if request.form["action"] == "delete":
        SoccerGame.query.filter_by(id=int(id)).delete()
    else:
        game = SoccerGame.query.filter_by(id=int(id)).one()
        game.league_id = int(request.form["league"])
        game.home_team_id = int(request.form["home_team"])
        game.away_team_id = int(request.form["away_team"])
        game.field = int(request.form["field"])
        game.round = int(request.form["round"])
        game.scheduled_time = parse(request.form["scheduled_time"])
        game.winner_agrees = (request.form.get(
            "winner_agrees", False) == "true")
        game.loser_agrees = (request.form.get("loser_agrees", False) == "true")
        game.game_finished = (request.form.get(
            "game_finished", False) == "true")
        game.is_final = (request.form.get("is_final", False) == "true")
        game.home_goals = int(request.form["home_goals"])
        game.away_goals = int(request.form["away_goals"])
    db.session.commit()
    return show_all_games(comp)


def calculate_system_teams(comp):
    games = SoccerGame.query.filter(
        SoccerGame.league.competition_id == comp.id
    ).all()
    games = filter(lambda g: g.is_system_game(), games)
    for game in games:
        logger.error(game.id, game.can_populate())
        if not game.can_populate():
            continue

        finals_only = SoccerGame.query.filter_by(is_final=True).filter(
            SoccerGame.round < game.round
        ).filter(
            SoccerGame.league.competition_id == comp.id
        ).count() > 0
        teams = Team.query.filter_by(is_system=False).filter_by(
            league_id=game.league_id).all()
        teams.sort(cmp=lambda a, b: b.compare(a, finals_only))
        logger.error("Only consider finals:", finals_only)
        home_index = int(game.home_team.school.replace("finals:top:", "")) - 1
        away_index = int(game.away_team.school.replace("finals:top:", "")) - 1
        game.home_team_id = teams[home_index].id
        game.away_team_id = teams[away_index].id
        db.session.add(game)
        db.session.commit()
    return "see log"
