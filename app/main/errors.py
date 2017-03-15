from flask import render_template
from . import main
from .forms import LoginForm


@main.app_errorhandler(404)
def page_not_found(error):
    loginform = LoginForm()
    return render_template("404.html", loginform=loginform), 404