#from flask
from flask import Blueprint, render_template
from flask.ext.login import login_required

#from project
from project.extensions import db
from project.apps.auth.models import Permission

mod = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@mod.route('/')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', permission=Permission)

