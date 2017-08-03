from rcj_soccer.base import app
from rcj_soccer.models import Competition

import logging
logger = logging.getLogger(__name__)


@app.route("/")
def list_competitions():
    pass


def get_competition(id):
    competition = Competition.query.filter_by(id=id).first()

    return competition
