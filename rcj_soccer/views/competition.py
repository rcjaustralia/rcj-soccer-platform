from rcj_soccer.base import app, db
from rcj_soccer.models import Competition
from flask import render_template, jsonify, request
from datetime import datetime
from dateutil.parser import parse
from rcj_soccer.util import config, obj_to_dict

import logging
logger = logging.getLogger(__name__)


@app.route("/")
def list_competitions():
    competitions = Competition.query.filter_by(is_active=True)\
        .order_by(Competition.start_date, Competition.name).all()
    return render_template("competitions.html", competitions=competitions,
                           year=datetime.utcnow().year)


@app.route("/api/competitions")
def api_list_competitions():
    competitions = Competition.query.order_by(Competition.start_date).all()
    data = []

    for competition in competitions:
        logger.warn("{0}".format(str(dir(competition))))
        data.append(obj_to_dict(competition))

    return jsonify(data)


@app.route("/api/competitions/<comp>/<token>",
           methods=["GET", "POST", "DELETE", "PUT"])
def api_competition(comp, token):
    if request.method == "GET":
        competition = Competition.query.filter_by(id=comp).one()
        return jsonify(obj_to_dict(competition))

    if token != config.get("api", "token"):
        return jsonify({"error": "invalid token"})

    if request.method == "POST":
        body = request.get_json()
        competition = Competition()
        competition.id = comp
        competition.name = body["name"]
        competition.fb_link = body["fb_link"]
        competition.twitter_link = body["twitter_link"]
        competition.event_sponsor_link = body["event_sponsor"]["link"]
        competition.event_sponsor_img = body["event_sponsor"]["img"]
        competition.is_active = True
        competition.start_date = parse(body["start_date"])

        db.session.add(competition)
        db.session.commit()
        return jsonify({"status": "created"})
    elif request.method == "DELETE":
        competition = Competition.query.filter_by(id=comp).one()
        db.session.delete(competition)
        db.session.commit()
        return jsonify({"status": "deleted"})
    elif request.method == "PUT":
        competition = Competition.query.filter_by(id=comp).one()
        body = request.get_json()

        if "name" in body:
            competition.name = body["name"]
        if "fb_link" in body:
            competition.fb_link = body["fb_link"]
        if "twitter_link" in body:
            competition.twitter_link = body["twitter_link"]
        if "active" in body:
            competition.is_active = body["active"]
        if "start_date" in body:
            competition.start_date = parse(body["start_date"])

        if "event_sponsor" in body:
            if "link" in body["event_sponsor"]:
                competition.event_sponsor_link = body["event_sponsor"]["link"]
            if "img" in body["event_sponsor"]:
                competition.event_sponsor_img = body["event_sponsor"]["img"]

        db.session.commit()
        return jsonify(obj_to_dict(competition))


def get_competition(id):
    competition = Competition.query.filter_by(id=id, is_active=True).first()

    return competition
