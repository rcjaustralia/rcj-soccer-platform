import json
from datetime import datetime

from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import SoccerGame, RequestType, Request
from rcj_soccer.util import sms
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition
from rcj_soccer.views.games import calculate_system_teams


@app.route("/<competition>/referee", methods=["GET"])
def referee(competition):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_all_unfinished_games(comp)


@app.route("/<competition>/referee/<id>/0", methods=["GET"])
def referee_game(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_game(comp, int(id), False)


@app.route("/<competition>/referee/<id>/1", methods=["GET"])
def referee_game_2(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        return show_game(comp, int(id), True)


@app.route("/<competition>/referee/<id>/end", methods=["GET", "POST"])
def referee_game_end(competition, id):
    comp = get_competition(competition)
    user = check_user(comp.id)
    if not user["is_logged_in"]:
        return redirect(url_for("login", competition=comp.id))
    if request.method == "GET":
        game = SoccerGame.query.filter_by(id=id).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).one()
        return render_template("referee_end.html", auth=template(comp.id),
                               game=game, comp=comp)
    else:
        game = SoccerGame.query.filter_by(id=id).filter(
            SoccerGame.league.has(competition_id=comp.id)
        ).one()
        game.winner_agrees = (request.form.get(
            "winner_agrees", False) == "true")
        game.loser_agrees = (request.form.get("loser_agrees", False) == "true")
        game.game_finished = True
        game.ref_id = user["user"].id
        game.home_goals = int(request.form.get("home_goals", game.home_goals))
        game.away_goals = int(request.form.get("away_goals", game.away_goals))
        db.session.commit()
        calculate_system_teams(comp)
        return redirect(url_for("referee", competition=comp.id))


@app.route("/<competition>/referee/<id>/state", methods=["GET"])
def update_game_state(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
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
        "test": str(datetime.now()).replace(" ", "T"),
        "competition": comp.id
    })


@app.route("/<competition>/referee/<id>/toggle_clock", methods=["GET"])
def update_game_clock(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.timer_start is None:
        game.timer_start = datetime.now()
    else:
        game.timer_start = None
    db.session.commit()
    return json.dumps({"success": "toggle_clock"})


@app.route("/<competition>/referee/<id>/next_state", methods=["GET"])
def next_game_state(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
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


@app.route("/<competition>/referee/<id>/prev_state", methods=["GET"])
def prev_game_state(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
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


@app.route("/<competition>/referee/<id>/home_goal", methods=["GET"])
def score_home_goal(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    game.home_goals += 1
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "home_goal"})


@app.route("/<competition>/referee/<id>/away_goal", methods=["GET"])
def score_away_goal(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    game.away_goals += 1
    game.home_damaged_1 = None
    game.home_damaged_2 = None
    game.away_damaged_1 = None
    game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "away_goal"})


@app.route("/<competition>/referee/<id>/home_goal_cancel", methods=["GET"])
def score_home_goal_cancel(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.home_goals > 0:
        game.home_goals -= 1
    db.session.commit()
    return json.dumps({"success": "home_goal_cancel"})


@app.route("/<competition>/referee/<id>/away_goal_cancel", methods=["GET"])
def score_away_goal_cancel(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.away_goals > 0:
        game.away_goals -= 1
    db.session.commit()
    return json.dumps({"success": "away_goal_cancel"})


@app.route("/<competition>/referee/<id>/damage_home_1", methods=["GET"])
def damage_home_1(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.home_damaged_1 is None:
        game.home_damaged_1 = datetime.now()
    else:
        game.home_damaged_1 = None
    db.session.commit()
    return json.dumps({"success": "damage_home_1"})


@app.route("/<competition>/referee/<id>/damage_home_2", methods=["GET"])
def damage_home_2(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.home_damaged_2 is None:
        game.home_damaged_2 = datetime.now()
    else:
        game.home_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "damage_home_2"})


@app.route("/<competition>/referee/<id>/damage_away_1", methods=["GET"])
def damage_away_1(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.away_damaged_1 is None:
        game.away_damaged_1 = datetime.now()
    else:
        game.away_damaged_1 = None
    db.session.commit()
    return json.dumps({"success": "damage_away_1"})


@app.route("/<competition>/referee/<id>/damage_away_2", methods=["GET"])
def damage_away_2(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
    if game.away_damaged_2 is None:
        game.away_damaged_2 = datetime.now()
    else:
        game.away_damaged_2 = None
    db.session.commit()
    return json.dumps({"success": "damage_away_2"})


@app.route("/<competition>/referee/<id>/reset", methods=["GET"])
def reset_game(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    game = SoccerGame.query.filter_by(id=id).filter(
        SoccerGame.league.has(competition_id=comp.id)
    ).one()
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


@app.route("/<competition>/referee/<id>/request/<rtype>", methods=["GET"])
def send_request(competition, id, rtype):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_logged_in"]:
        return json.dumps({"error": "login_fail"})

    req = Request()
    req.request_type_id = int(rtype)
    req.user_id = check_user(comp.id)["user"].id
    req.game_id = int(id)

    db.session.add(req)
    db.session.commit()
    if req.request_type is None \
            or req.request_type.competition_id != comp.id \
            or not req.request_type.is_active:
        Request.query.filter_by(id=req.id).delete()
        return json.dumps({"error": "login_fail"})

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


def show_game(comp, id, switch):
    game = SoccerGame.query.filter_by(id=id).one()
    request_types = RequestType.query.filter_by(
        competition_id=comp.id,
        is_active=True
    ).order_by(
        RequestType.priority.desc(), RequestType.name.asc()
    ).all()
    return render_template("referee.html", game=game, auth=template(comp.id),
                           switch_side=switch, request_types=request_types,
                           comp=comp)


def show_all_unfinished_games(comp):
    games = SoccerGame.query.filter_by(game_finished=False)\
        .filter(SoccerGame.home_team.has(is_system=False) &
                SoccerGame.away_team.has(is_system=False) &
                SoccerGame.league.has(competition_id=comp.id))\
        .order_by(SoccerGame.scheduled_time.asc(), SoccerGame.round.asc(),
                  SoccerGame.field.asc()).all()
    return render_template("referee_games.html", games=games,
                           auth=template(comp.id), comp=comp)
