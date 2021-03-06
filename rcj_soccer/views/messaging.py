from flask import request, render_template, redirect

from rcj_soccer.base import app
from rcj_soccer.models import User
from rcj_soccer.util import sms
from rcj_soccer.views.auth import check_user, template
from rcj_soccer.views.competition import get_competition


@app.route("/<competition>/messaging", methods=["GET", "POST"])
def messaging(competition):
    comp = get_competition(competition)
    if not check_user(comp.id)["is_admin"]:
        return redirect("/login", competition=comp.id)
    if request.method == "GET":
        return show_form(comp)
    else:
        phones = request.form.getlist("phones")
        message = request.form["message"].strip()

        for phone in phones:
            sms.get_provider().send(phone.strip(), message)
        return show_form(comp)


def show_form(comp):
    users = User.query.filter_by(
        competition_id=comp.id
    ).order_by(
        User.username.asc()
    ).all()
    provider = sms.get_provider()
    return render_template("messaging.html", users=users, comp=comp,
                           auth=template(comp.id), provider=provider)
