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
        games = db.session.query(SoccerGame).filter(
            SoccerGame.game_finished == False
        ).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).all()
        for game in games:
            db.session.delete(game)
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


def show_all_games(comp):
    games = SoccerGame.query.filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).all()
    leagues = League.query.filter_by(competition_id=comp.id).all()
    teams = Team.query.filter(
        Team.league.has(competition_id=comp.id)
    ).all()
    return render_template("all_games.html", games=games, leagues=leagues,
                           teams=teams, auth=template(comp.id), comp=comp)


def create_new_game(comp):
    league = League.query.filter_by(
        id=int(request.form["league"]),
        competition_id=comp.id
    ).one()
    game = SoccerGame()
    game.league_id = league.id
    game.home_team_id = int(request.form["home_team"])
    game.away_team_id = int(request.form["away_team"])
    game.field = int(request.form["field"])
    game.round = int(request.form["round"])
    game.scheduled_time = parse(request.form["scheduled_time"])
    db.session.add(game)
    db.session.commit()
    return show_all_games(comp)


def show_game(comp, id):
    game = SoccerGame.query.filter_by(
        id=int(id)
    ).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    leagues = League.query.filter_by(competition_id=comp.id).all()
    teams = Team.query.filter(
        Team.league.has(competition_id=comp.id)
    ).all()
    return render_template("game.html", game=game, teams=teams,
                           leagues=leagues, auth=template(comp.id), comp=comp)


def edit_game(comp, id):
    if request.form["action"] == "delete":
        SoccerGame.query.filter_by(id=int(id)).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).delete()
    else:
        game = SoccerGame.query.filter_by(id=int(id)).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).one()
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
        SoccerGame.league.has(competition_id=comp.id)
    ).all()
    games = filter(lambda g: g.is_system_game(), games)
    for game in games:
        logger.error("{0} {1}".format(game.id, game.can_populate()))
        if not game.can_populate():
            continue

        finals_only = SoccerGame.query.filter_by(is_final=True).filter(
            SoccerGame.round < game.round
        ).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).count() > 0
        teams = Team.query.filter_by(is_system=False).filter_by(
            league_id=game.league_id
        ).all()
        teams.sort(key=lambda team: (
            -1 * team.score(), -1 * team.goal_difference(),
            -1 * team.goals_for(), -1 * team.games_played(), team.name
        ))
        logger.error("Only consider finals: {0}".format(finals_only))
        home_index = int(game.home_team.school.replace("finals:top:", "")) - 1
        away_index = int(game.away_team.school.replace("finals:top:", "")) - 1
        game.home_team_id = teams[home_index].id
        game.away_team_id = teams[away_index].id
        db.session.add(game)
        db.session.commit()
    return "see log"
