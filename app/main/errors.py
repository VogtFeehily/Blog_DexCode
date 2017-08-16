# coding=utf-8
from flask import render_template
from . import main
from .forms import LoginForm, CategoryForm


@main.app_errorhandler(404)
def page_not_found(error):
    loginform = LoginForm()
    categoryForm = CategoryForm()
    return render_template("404.html", loginform=loginform, categoryForm=categoryForm), 404