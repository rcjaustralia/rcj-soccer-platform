from flask import request, render_template

from rcj_soccer.base import app
from rcj_soccer.views.auth import template


@app.route("/rules", methods=["GET"])
def rules():
    if request.method == "GET":
        return render_template("rules.html", auth=template())


@app.route("/rules/ball-spec", methods=["GET"])
def rules_ball():
    if request.method == "GET":
        return render_template("rules_ball_spec.html", auth=template(True))


@app.route("/rules/gen2", methods=["GET"])
def rules_gen2():
    if request.method == "GET":
        return render_template("rules_gen2.html", auth=template(True))


@app.route("/rules/lw-open", methods=["GET"])
def rules_lwopen():
    if request.method == "GET":
        return render_template("rules_open.html", auth=template(True))


@app.route("/rules/kpmq", methods=["GET"])
def rules_kpmd():
    if request.method == "GET":
        return render_template("rules_kpmd.html", auth=template(True))
