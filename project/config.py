import os
from flask import Config

class DefaultConfig(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True

    INSTALLED_BLUEPRINTS = (
        'site',
        'email',
        'auth',
        'dashboard',
        'profile',
        'post',
        'api',
    )
    SECRET_KEY = 'hard to guess string'

    SSL_DISABLE = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''


    FLASKY_ADMIN = 'erfan.tahriri1@gmail.com'
    FLASKY_MAIL_SUBJECT_PREFIX = '[EBS]'
    FLASKY_MAIL_SENDER = 'ESB Admin <erfan.tahriri1@gmail.com>'

    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 0.5
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_FOLLOWED_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 5

class DevelopmentConfig(DefaultConfig):
    DEBUG = True


class DeploymentConfig(DefaultConfig):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.FLASKY_MAIL_SENDER,
                                   toaddrs=[cls.FLASKY_ADMIN],
                                   subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
                                   credentials=credentials,
                                   secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(DeploymentConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        DeploymentConfig.init_app(app)
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
