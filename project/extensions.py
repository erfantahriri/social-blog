from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, Manager
from flask.ext.moment import Moment
from flask.ext.mail import Mail
from flask.ext.pagedown import PageDown


db = SQLAlchemy()
mail = Mail()
manager = Manager()
migrate = Migrate()
moment = Moment()
pagedown = PageDown()


class ValidationError(ValueError):
    pass