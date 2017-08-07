import json

from flask import render_template, redirect, url_for, jsonify

from rcj_soccer.base import app, db
from rcj_soccer.models import Request, RequestType
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/requests", methods=["GET"])
def request(competition):
    comp = get_competition(competition)
    if not check_user(comp.id):
        return redirect(url_for("login", competition=comp.id))
    return render_template("requests.html", auth=template(comp.id), comp=comp)


@app.route("/<competition>/requests/get", methods=["GET"])
def get_requests(competition):
    comp = get_competition(competition)
    user = check_user(comp.id)
    if not user:
        return json.dumps({"error": "login_fail"})

    all = Request.query.filter_by(actioned=False).join(Request.request_type)\
        .filter(RequestType.competition_id == comp.id).order_by(
            RequestType.priority.desc(),
            Request.received.asc(),
            Request.id.asc()
    ).all()

    if not user.is_admin:
        all = [r for r in all if not r.request_type.only_admin]

    all = [flatten_request(comp, r) for r in all]

    return jsonify(all)


@app.route("/<competition>/requests/<id>/resolve", methods=["GET"])
def resolve_request(competition, id):
    comp = get_competition(competition)
    if not check_user(comp.id):
        return json.dumps({"error": "login_fail"})

    req = Request.query.filter_by(id=int(id)).one()
    req.actioned = True
    db.session.commit()
    return jsonify({"success": "resolve_request"})


def flatten_request(comp, request):
    return {
        "type": request.request_type.name,
        "league": request.game.league.name,
        "field": request.game.field,
        "received": request.received.isoformat(),
        "username": request.user.username,
        "url": url_for("resolve_request", competition=comp.id, id=request.id),
        "id": request.id,
    }
