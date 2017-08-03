import json

from flask import request, render_template

from rcj_soccer.base import app
from rcj_soccer.models import SoccerGame
from rcj_soccer.views.auth import template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/results/<id>", methods=["GET"])
def result_game(competition, id):
    comp = get_competition(competition)
    if request.method == "GET":
        return result_show_game(comp, int(id))


@app.route("/<competition>/results/<id>/state", methods=["GET"])
def update_result_game_state(competition, id):
    comp = get_competition(competition)
    game = SoccerGame.query.filter_by(id=id).one()
    return json.dumps({
        "home_goals": game.home_goals,
        "away_goals": game.away_goals,
        "timer_start": str(game.timer_start).replace(" ", "T"),
        "scheduled_time": game.time(),
        "first_half_finished": game.first_half_finished,
        "half_time_finished": game.half_time_finished,
        "second_half_finished": game.second_half_finished,
        "game_ended": game.game_finished,
        "competition": comp.id
    })


def result_show_game(comp, id):
    game = SoccerGame.query.filter_by(id=id).one()
    return render_template("liveresults.html", game=game,
                           auth=template(), comp=comp)
