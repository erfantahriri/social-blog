# from flask
from flask import render_template

from . import mod


@mod.route('/document/')
def document():
    return render_template('api/document.txt')