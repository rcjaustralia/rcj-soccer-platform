import random
from datetime import timedelta
import logging; logger = logging.getLogger(__name__)
from dateutil.parser import parse
from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import SoccerGame, Team, League
from rcj_soccer.views.auth import check_user, template


@app.route("/draws", methods=["GET", "POST"])
def draws():
    if not check_user(True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_draw_options()
    else:
        return show_draw()


@app.route("/draws_save", methods=["POST"])
def draws_save():
    if not check_user(True):
        return redirect(url_for("login"))
    count = int(request.form["game_count"])
    for i in range(count):
        game = SoccerGame()
        game.league_id = int(request.form["league_id"])
        game.home_team_id = int(field(i, "home"))
        game.away_team_id = int(field(i, "away"))
        game.field = int(field(i, "field"))
        game.round = int(field(i, "round"))
        game.is_final = field(i, "is_final") == "1"
        game.scheduled_time = parse(field(i, "start_time"))
        db.session.add(game)
        db.session.commit()
    return render_template("draw_saved.html", auth=template())


def field(count, name):
    return request.form["g" + str(count) + "_" + name]


def show_draw_options():
    leagues = League.query.all()
    return render_template("draws.html", leagues=leagues, auth=template())


def next_round(teams):
    hold = teams[0]
    rotate = teams[-1]
    slide = teams[1:-1]
    return [hold] + [rotate] + slide


def get_games(teams):
    half = len(teams) / 2
    home = teams[:half]
    away = teams[half:][::-1]
    return [{"home": home[i], "away": away[i]} for i in xrange(half)]


def show_draw():
    league_id = int(request.form["league"])
    duration = int(request.form["game_duration"])
    max_rounds = int(request.form["round"])
    start_time = parse(request.form["start_time"])
    finals_size = int(request.form["finals_size"])
    total_repeats = int(request.form["total_repeats"])

    fields = League.query.filter_by(id=league_id).one().areas

    team_count = Team.query.filter_by(
        league_id=league_id).filter_by(is_system=False).count()
    # print team_count
    real_teams = Team.query.filter_by(
        league_id=league_id).filter_by(is_system=False).all()
    has_blank = (team_count % 2 == 1)
    teams = range(team_count + int(has_blank))
    random.shuffle(teams)
    # half = len(teams) / 2
    # teams = teams[:half] + teams[half:][::-1]
    required_rounds = (team_count - 1) if not has_blank else team_count

    total_rounds = min(max_rounds, required_rounds * total_repeats)
    rounds = []
    current_time = start_time

    bye_team = Team.query.filter_by(
        is_bye=True).filter_by(league_id=league_id).first()
    # print "Bye Team", bye_team
    if bye_team is None:
        bye_team = Team()
        bye_team.league_id = league_id
        bye_team.name = "Bye"
        bye_team.school = "(system)"
        bye_team.is_bye = True
        bye_team.is_system = True
        db.session.add(bye_team)
        db.session.commit()

    if has_blank:
        real_teams += [bye_team]

    total = 0
    game_count = 0
    for round_number in range(total_rounds):
        # if not just_updated:
        #   current_time = current_time + timedelta(minutes=duration)
        games = get_games(teams)
        # print [(game["home"], game["away"]) for game in games]
        for i in range(len(games)):
            is_bye = False
            games[i]["home"] = real_teams[games[i]["home"]] if games[
                i]["home"] < team_count else bye_team
            games[i]["away"] = real_teams[games[i]["away"]] if games[
                i]["away"] < team_count else bye_team
            if games[i]["home"] == bye_team or games[i]["away"] == bye_team:
                is_bye = True
            games[i]["round"] = round_number + 1
            games[i]["index"] = total
            games[i]["field"] = (game_count % fields) + 1 if not is_bye else 0
            games[i]["start_time"] = str(current_time)
            if ((game_count + 1) % fields) == 0 and not is_bye:
                logger.info(str(i) + ' ' + str(fields))
                current_time = current_time + timedelta(minutes=duration)
            if not is_bye:
                game_count += 1
            total += 1
        rounds.append(games)
        teams = next_round(teams)

    # Finals
    finals_size = finals_size  # i.e Top N
    finals_games = finals_size / 2
    logger.error(finals_games)
    logger.error(finals_size)

    finals_teams = []
    round_count = 1
    logger.error("before", len(rounds))
    while finals_games > 0:
        games = []
        current_time = current_time + timedelta(minutes=duration)
        for i in range(finals_games):
            logger.error(round_count + 1, ": Top", i + 1, "vs"),
            logger.error("Top", finals_games * 2 - i)
            home_team = Team.query.filter_by(is_system=True).filter_by(
                school="finals:top:" + str(i + 1)).filter_by(
                league_id=league_id).first()
            if home_team is None:
                home_team = Team()
                home_team.league_id = league_id
                home_team.name = "#" + str(i + 1)
                home_team.school = "finals:top:" + str(i + 1)
                home_team.is_system = True
                db.session.add(home_team)
                db.session.commit()
            finals_teams.append(home_team)

            away_team = Team.query.filter_by(is_system=True).filter_by(
                school="finals:top:" + str(finals_games * 2 - i)).filter_by(
                league_id=league_id).first()
            if away_team is None:
                away_team = Team()
                away_team.league_id = league_id
                away_team.name = "#" + str(finals_games * 2 - i)
                away_team.school = "finals:top:" + str(finals_games * 2 - i)
                away_team.is_system = True
                db.session.add(away_team)
                db.session.commit()
            finals_teams.append(away_team)

            game = {
                "home": home_team,
                "away": away_team,
                "round": max_rounds + round_count,
                "index": total,
                "field": i % fields + 1,
                "is_final": True,
                "start_time": str(current_time)
            }

            if i % fields == 0:
                current_time = current_time + timedelta(minutes=duration)
            games.append(game)
            total += 1
        rounds.append(games)
        round_count += 1
        finals_games = finals_games / 2

    finals_teams.sort(key=lambda x: x.name)
    logger.error("after", len(rounds))
    return render_template("draws_modify.html", rounds=rounds,
                           teams=real_teams, total=total, total_fields=fields,
                           total_rounds=total_rounds, league_id=league_id,
                           auth=template(), duration=duration,
                           finals_teams=finals_teams)
