import json

from flask import render_template, redirect, url_for, jsonify

from app import app, db
from rcj_soccer.models import Request, RequestType
from rcj_soccer.views.auth import check_user, template


@app.route("/requests", methods=["GET"])
def request():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("requests.html", auth=template())


@app.route("/requests/get", methods=["GET"])
def get_requests():
    user = check_user()
    if not user:
        return json.dumps({"error": "login_fail"})

    all = Request.query.filter_by(actioned=False).join(Request.request_type)\
        .order_by(RequestType.priority.desc(),
                  Request.received.asc(), Request.id.asc()).all()

    if not user.is_admin:
        all = [r for r in all if not r.request_type.only_admin]

    return jsonify(map(flatten_request, all))


@app.route("/requests/<id>/resolve", methods=["GET"])
def resolve_request(id):
    if not check_user():
        return json.dumps({"error": "login_fail"})

    req = Request.query.filter_by(id=int(id)).one()
    req.actioned = True
    db.session.commit()
    return jsonify({"success": "resolve_request"})


def flatten_request(request):
    return {
        "type": request.request_type.name,
        "league": request.game.league.name,
        "field": request.game.field,
        "received": request.received.isoformat(),
        "username": request.user.username,
        "url": url_for("resolve_request", id=request.id),
        "id": request.id,
    }
