from app import app, db
from models import SoccerGame, RequestType, Request
from flask import request, render_template, redirect, url_for
from auth import check_user, template

import json
import sms
from datetime import datetime


@app.route("/referee", methods=["GET"])
def referee():
    if not check_user():
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_all_unfinished_games()


@app.route("/referee/<id>/0", methods=["GET"])
def referee_game(id):
    if not check_user():
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_game(int(id), False)


@app.route("/referee/<id>/1", methods=["GET"])
def referee_game_2(id):
    if not check_user():
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_game(int(id), True)


@app.route("/referee/<id>/end", methods=["GET", "POST"])
def referee_game_end(id):
    if not check_user():
        return redirect(url_for("login"))
    if request.method == "GET":
        game = SoccerGame.query.filter_by(id=id).one()
        return render_template("referee_end.html", auth=template(), game=game)
    else:
        game = SoccerGame.query.filter_by(id=id).one()
        game.winner_agrees = (request.form.get(
            "winner_agrees", False) == "true")
        game.loser_agrees = (request.form.get("loser_agrees", False) == "true")
        game.game_finished = True
        game.ref_id = check_user().username
        db.session.commit()
        return redirect("referee")


@app.route("/referee/<id>/state", methods=["GET"])
def update_game_state(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    return json.dumps({
        "home_goals": game.home_goals,
        "away_goals": game.away_goals,
        "timer_start": str(game.timer_start).replace(" ", "T"),
        "first_half_finished": game.first_half_finished,
        "half_time_finished": game.half_time_finished,
        "second_half_finished": game.second_half_finished,
        "game_ended": game.game_finished,
        "home_damaged_1": str(game.home_damaged_1).replace(" ", "T"),
        "home_damaged_2": str(game.home_damaged_2).replace(" ", "T"),
        "away_damaged_1": str(game.away_damaged_1).replace(" ", "T"),
        "away_damaged_2": str(game.away_damaged_2).replace(" ", "T"),
        "test": str(datetime.now()).replace(" ", "T")
    })


@app.route("/referee/<id>/toggle_clock", methods=["GET"])
def update_game_clock(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.timer_start is None:
        game.timer_start = datetime.now()
    else:
        game.timer_start = None
    db.session.commit()
    return json.dumps({"success": "toggle_clock"})


@app.route("/referee/<id>/next_state", methods=["GET"])
def next_game_state(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if not game.first_half_finished:
        game.first_half_finished = True
    elif not game.half_time_finished:
        game.half_time_finished = True
    else:
        game.second_half_finished = True
    game.timer_start = None
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "next_state"})


@app.route("/referee/<id>/prev_state", methods=["GET"])
def prev_game_state(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.second_half_finished:
        game.second_half_finished = False
    elif game.half_time_finished:
        game.half_time_finished = False
    else:
        game.first_half_finished = False
    game.timer_start = None
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "prev_state"})


@app.route("/referee/<id>/home_goal", methods=["GET"])
def score_home_goal(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    game.home_goals += 1
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "home_goal"})


@app.route("/referee/<id>/away_goal", methods=["GET"])
def score_away_goal(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    game.away_goals += 1
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "away_goal"})


@app.route("/referee/<id>/home_goal_cancel", methods=["GET"])
def score_home_goal_cancel(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.home_goals > 0:
        game.home_goals -= 1
    db.session.commit()
    return json.dumps({"success": "home_goal_cancel"})


@app.route("/referee/<id>/away_goal_cancel", methods=["GET"])
def score_away_goal_cancel(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.away_goals > 0:
        game.away_goals -= 1
    db.session.commit()
    return json.dumps({"success": "away_goal_cancel"})


@app.route("/referee/<id>/damage_home_1", methods=["GET"])
def damage_home_1(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.home_damaged_1 is None:
        game.home_damaged_1 = datetime.now()
    else:
        game.home_damaged_1 = None
    db.session.commit()
    return json.dumps({"success": "damage_home_1"})


@app.route("/referee/<id>/damage_home_2", methods=["GET"])
def damage_home_2(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.home_damaged_2 is None:
        game.home_damaged_2 = datetime.now()
    else:
        game.home_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "damage_home_2"})


@app.route("/referee/<id>/damage_away_1", methods=["GET"])
def damage_away_1(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.away_damaged_1 is None:
        game.away_damaged_1 = datetime.now()
    else:
        game.away_damaged_1 = None
    db.session.commit()
    return json.dumps({"success": "damage_away_1"})


@app.route("/referee/<id>/damage_away_2", methods=["GET"])
def damage_away_2(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    if game.away_damaged_2 is None:
        game.away_damaged_2 = datetime.now()
    else:
        game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "damage_away_2"})


@app.route("/referee/<id>/reset", methods=["GET"])
def reset_game(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).one()
    game.timer_start = None
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    game.first_half_finished = False
    game.second_half_finished = False
    game.half_time_finished = False
    game.home_goals = 0
    game.away_goals = 0
    db.session.commit()
    return json.dumps({"success": "reset_game"})


@app.route("/referee/<id>/request/<rtype>", methods=["GET"])
def send_request(id, rtype):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    req = Request()
    req.request_type_id = int(rtype)
    req.user_id = check_user().username
    req.game_id = int(id)

    db.session.add(req)
    db.session.commit()
    if req.request_type.send_text:
        sms.send(req.request_type.user.phone,
                 "REQUEST: {type} at {league} {field} by {user} ({time})"
                 .format(**{
                         "type": req.request_type.name,
                         "league": req.game.league.name,
                         "field": req.game.field,
                         "user": req.user.username,
                         "time": req.received.strftime("%X"),
                         }))
    return json.dumps({"success": "send_request"})


def show_game(id, switch):
    game = SoccerGame.query.filter_by(id=id).one()
    request_types = RequestType.query.order_by(
        RequestType.priority.desc(), RequestType.name.asc()).all()
    return render_template("referee.html", game=game, auth=template(),
                           switch_side=switch, request_types=request_types)


def show_all_unfinished_games():
    games = SoccerGame.query.filter_by(game_finished=False)\
        .filter(SoccerGame.home_team.has(is_system=False) &
                SoccerGame.away_team.has(is_system=False))\
        .order_by(SoccerGame.scheduled_time.asc(), SoccerGame.round.asc(),
                  SoccerGame.field.asc()).all()
    return render_template("referee_games.html", games=games, auth=template())
