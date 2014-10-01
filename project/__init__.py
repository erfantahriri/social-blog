from project.application import create_app
from project.apps.auth.models import Permission
from flask import Blueprint
from project.application import pagedown


mod = Blueprint('site', __name__, url_prefix='/')


@mod.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


api = Blueprint('api', __name__)
