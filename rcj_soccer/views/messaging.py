from flask import request, render_template, redirect

from rcj_soccer.base import app
from rcj_soccer.models import User
from rcj_soccer.util import sms
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/messaging", methods=["GET", "POST"])
def messaging(competition):
    comp = get_competition(competition)
    if not check_user(comp.id, True):
        return redirect("/login", competition=comp.id)
    if request.method == "GET":
        return show_form(comp)
    else:
        phones = ",".join(request.form.getlist("phones"))
        message = request.form["message"].strip()
        sms.send(phones, message)
        return show_form(comp)


def show_form(comp):
    users = User.query.filter_by(
        competition_id=comp.id).order_by(User.username.asc()).all()
    balance = sms.balance()
    return render_template("messaging.html", users=users, comp=comp,
                           auth=template(comp.id), balance=balance)
