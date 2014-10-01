# from flask
from flask import jsonify

# from project
from .authentication import auth
from . import mod
from project.apps.auth.models import User_auth as User


@mod.route('/user/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.filter_by(id=id).first()
    return jsonify({'user': user.to_json()})