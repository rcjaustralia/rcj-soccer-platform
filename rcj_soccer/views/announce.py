from flask import request, render_template

from rcj_soccer.base import app
from rcj_soccer.views.auth import template


@app.route("/announce", methods=["GET"])
def announce():
    if request.method == "GET":
        return render_template("announce.html", auth=template())
