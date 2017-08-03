from flask import request, render_template

from rcj_soccer.base import app
from rcj_soccer.views.auth import template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/rules", methods=["GET"])
def rules(competition):
    comp = get_competition(competition)
    if request.method == "GET":
        return render_template("rules.html", auth=template(), comp=comp)


@app.route("/<competition>/rules/ball-spec", methods=["GET"])
def rules_ball(competition):
    comp = get_competition(competition)
    if request.method == "GET":
        return render_template("rules_ball_spec.html", auth=template(True),
                               comp=comp)


@app.route("/<competition>/rules/gen2", methods=["GET"])
def rules_gen2(competition):
    comp = get_competition(competition)
    if request.method == "GET":
        return render_template("rules_gen2.html", auth=template(True),
                               comp=comp)


@app.route("/<competition>/rules/lw-open", methods=["GET"])
def rules_lwopen(competition):
    comp = get_competition(competition)
    if request.method == "GET":
        return render_template("rules_open.html", auth=template(True),
                               comp=comp)


@app.route("/<competition>/rules/kpmq", methods=["GET"])
def rules_kpmd(competition):
    comp = get_competition(competition)
    if request.method == "GET":
        return render_template("rules_kpmd.html", auth=template(True),
                               comp=comp)
