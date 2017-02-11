from app import app, db
from models import User
from flask import request, render_template, redirect
from config import config
from auth import check_user, template

import sms
import re

@app.route("/messaging", methods = ["GET", "POST"])
def messaging():
	if not check_user(True):
		return redirect("/login")
	if request.method == "GET":
		return show_form()
	else:
		phones = ",".join(request.form.getlist("phones"))
		message = request.form["message"].strip()
		sms.send(phones, message)
		return show_form()

def show_form():
	users = User.query.order_by(User.username.asc()).all()
	balance = sms.balance()
	return render_template("messaging.html", users = users, auth = template(), balance = balance)