# from flask
from flask import Blueprint

mod = Blueprint('api', __name__, url_prefix='/api')

# from project
from .authentication import *
from .user import *
from .comment import *
from .errors import *
from .general import *
from .post import *
