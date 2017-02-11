from app import app
from flask import request, render_template
from auth import template


@app.route("/announce", methods=["GET"])
def announce():
    if request.method == "GET":
        return render_template("announce.html", auth=template())
