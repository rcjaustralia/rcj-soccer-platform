from app import app
from models import SoccerGame
from flask import request, render_template
from auth import template
import json


@app.route("/results/<id>", methods=["GET"])
def result_game(id):
    if request.method == "GET":
        return result_show_game(int(id))


@app.route("/results/<id>/state", methods=["GET"])
def update_result_game_state(id):
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
    })


def result_show_game(id):
    game = SoccerGame.query.filter_by(id=id).one()
    return render_template("liveresults.html", game=game, auth=template())
