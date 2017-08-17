import random
from datetime import timedelta
import logging

from dateutil.parser import parse
from flask import request, render_template, redirect, url_for

from rcj_soccer.base import app, db
from rcj_soccer.models import SoccerGame, Team, League
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition

logger = logging.getLogger(__name__)


@app.route("/<competition>/draws", methods=["GET", "POST"])
def draws(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect(url_for("login"))
    if request.method == "GET":
        return show_draw_options(comp)
    else:
        return show_draw(comp)


@app.route("/<competition>/draws_save", methods=["POST"])
def draws_save(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
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
        game.comp_id = comp.id
        db.session.add(game)
        db.session.commit()
    return render_template("draw_saved.html",
                           auth=template(comp.id), comp=comp)


def field(count, name):
    return request.form["g" + str(count) + "_" + name]


def show_draw_options(comp):
    leagues = League.query.filter_by(competition_id=comp.id).all()
    return render_template("draws.html", leagues=leagues,
                           auth=template(comp.id), comp=comp)


def next_round(teams):
    hold = teams[0]
    rotate = teams[-1]
    slide = teams[1:-1]
    return [hold] + [rotate] + slide


def get_games(teams):
    half = len(teams) // 2
    home = teams[:half]
    away = teams[half:][::-1]
    return [{"home": home[i], "away": away[i]} for i in range(half)]


def show_draw(comp):
    league_id = int(request.form["league"])
    duration = int(request.form["game_duration"])
    max_rounds = int(request.form["round"])
    start_time = parse(request.form["start_time"])
    finals_size = int(request.form["finals_size"])
    total_repeats = int(request.form["total_repeats"]) + 1

    league = League.query.filter_by(id=league_id, competition_id=comp.id).one()
    fields = league.areas

    team_count = Team.query.filter_by(
        league_id=league_id, is_system=False
    ).count()
    # print team_count
    real_teams = Team.query.filter_by(
        league_id=league_id, is_system=False
    ).all()
    has_blank = (team_count % 2 == 1)
    teams = list(range(team_count + int(has_blank)))  # emulate Python 2 range
    random.shuffle(teams)
    required_rounds = (team_count - 1) if not has_blank else team_count

    total_rounds = min(max_rounds, required_rounds * total_repeats)
    rounds = []
    current_time = start_time

    bye_team = Team.query.filter_by(
        is_bye=True, league_id=league_id
    ).first()
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
    finals_games = finals_size // 2
    logger.error(finals_games)
    logger.error(finals_size)

    finals_teams = []
    round_count = 1
    logger.error("before {0}".format(len(rounds)))
    max_rounds_count = 0
    while finals_games > 0:
        games = []
        current_time = current_time + timedelta(minutes=duration)
        for i in range(finals_games):
            logger.error("{0}: Top {1} vs Top {2}".format(
                round_count + 1, i + 1, finals_games * 2 - i)
            )
            home_team = Team.query.filter_by(
                is_system=True,
                school="finals:top:" + str(i + 1),
                league_id=league_id
            ).first()
            if home_team is None:
                home_team = Team()
                home_team.league_id = league_id
                home_team.name = "#" + str(i + 1)
                home_team.school = "finals:top:" + str(i + 1)
                home_team.is_system = True
                db.session.add(home_team)
                db.session.commit()
            finals_teams.append(home_team)

            away_team = Team.query.filter_by(
                is_system=True,
                school="finals:top:" + str(finals_games * 2 - i),
                league_id=league_id
            ).first()
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

            max_rounds_count = max_rounds + round_count

            if i % fields == 0:
                current_time = current_time + timedelta(minutes=duration)
            games.append(game)
            total += 1
        rounds.append(games)
        round_count += 1
        finals_games = finals_games // 2

    finals_teams.sort(key=lambda x: x.name)
    logger.error("after {0}".format(len(rounds)))

    # TODO: Fix this to be a more useful limit
    max_rounds_count = 200

    return render_template("draws_modify.html", rounds=rounds,
                           teams=real_teams, total=total, total_fields=fields,
                           total_rounds=max_rounds_count, league_id=league_id,
                           auth=template(comp.id), duration=duration,
                           comp=comp, finals_teams=finals_teams)
