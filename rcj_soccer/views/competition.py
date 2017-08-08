from rcj_soccer.base import app
from rcj_soccer.models import Competition
from flask import render_template
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


@app.route("/")
def list_competitions():
    competitions = Competition.query.filter_by(is_active=True)\
        .order_by(Competition.name).all()
    return render_template("competitions.html", competitions=competitions,
                           year=datetime.utcnow().year)


def get_competition(id):
    competition = Competition.query.filter_by(id=id, is_active=True).first()

    return competition
