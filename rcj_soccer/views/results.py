from flask import render_template

from rcj_soccer.base import  app
from rcj_soccer.models import SoccerGame, Team, League
from rcj_soccer.views.auth import template


@app.route("/results", methods=["GET", "POST"])
def results():
    # now1 = datetime.now()
    leagues = League.query.all()
    teams = Team.query.filter_by(is_system=False).all()
    # now2 = datetime.now()
    sorted_data = {}
    for team in teams:
        if team.league_id not in sorted_data:
            sorted_data[team.league_id] = {"teams": []}
        team.cache()
        sorted_data[team.league_id]["teams"].append(team)

    for league in sorted_data.keys():
        # sorted_data[league]["teams"].sort(key=lambda t: t.name + t.school)
        sorted_data[league]["teams"].sort(cmp=lambda t, o: o.compare(t))

    # now3 = datetime.now()
    games = SoccerGame.query.order_by(SoccerGame.scheduled_time.asc(
    ), SoccerGame.round.asc(), SoccerGame.field.asc()).all()
    # now4 = datetime.now()
    for game in games:
        if game.league_id not in sorted_data:
            sorted_data[game.league_id] = {}
        if "games" not in sorted_data[game.league_id]:
            sorted_data[game.league_id]["games"] = []
        game.is_bye()
        sorted_data[game.league_id]["games"].append(game)
    # now5 = datetime.now()
    a = template()
    lc = max(1, int(12 / max(len(leagues), 1)))
    # now6 = datetime.now()
    rt = render_template("results.html", leagues=leagues,
                         data=sorted_data, league_count=lc, auth=a)
    # now7 = datetime.now()
    # print "1 =", now2 - now1
    # print "2 =", now3 - now2
    # print "3 =", now4 - now3
    # print "4 =", now5 - now4
    # print "5 =", now6 - now5
    # print "6 =", now7 - now6
    # print "total =", now7 - now1
    return rt
