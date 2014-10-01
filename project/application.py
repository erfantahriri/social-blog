# from flask
from flask import Flask, request, jsonify, render_template
from flask.ext.babel import gettext as _
from flask.ext.login import LoginManager
from flask.ext.script import Shell
from flask.ext.migrate import MigrateCommand

#from project
from project.config import DefaultConfig as Base_Config
from project.extensions import db, mail, manager, migrate, moment, pagedown

__all__ = ['create_app']

DEFAULT_APP_NAME = 'project'

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def make_shell_context():
    return dict(db=db)


def create_app(config=None, app_name=DEFAULT_APP_NAME):
    app = Flask(app_name)

    configiure_app(app, config)
    configure_blueprints(app)
    configure_folders(app)
    configure_errorhandlers(app)
    configure_extentions(app)
    configure_email(app)
    configure_login_manager(app)
    configure_manager(app)
    configure_migrate(app)
    configure_pagedown(app)
    configure_template_tag(app)
    return app


def configiure_app(app, config):

    app.config.from_object(Base_Config)

    if config is not None:
        app.config.from_object(config)

    app.config.from_envvar('project_CONFIG', silent=True)


def configure_blueprints(app):

    app.config.setdefault('INSTALLED_BLUEPRINTS', [])
    blueprints = app.config['INSTALLED_BLUEPRINTS']
    for blueprint_name in blueprints:
        bp = __import__('project.apps.%s' % blueprint_name, fromlist=['views'])

        try:
            mod = __import__('project.%s' % blueprint_name, fromlist=['urls'])
        except ImportError:
            pass
        else:
            mod.urls.add_url_rules(bp.views.mod)
        try:
            app.register_blueprint(bp.views.mod)
        except:
            pass


def configure_folders(app):
    app.static_folder = 'media/statics'
    app.template_folder = 'media/templates'


def configure_errorhandlers(app):

    if app.testing:
        return

    # @app.errorhandler(404)
    # def page_not_found(error):
    #     # import_cart_to_list(error)
    #     if request.is_xhr:
    #         return jsonify(error=_('Sorry, page not found'))
    #     return render_template("errors/404.html", error=error), 404

    @app.errorhandler(404)
    def page_not_found(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        # import_cart_to_list(error)
        if request.is_xhr:
            return jsonify(error=_('Sorry, not allowed'))
        return render_template("errors/403.html", error=error), 403

    # @app.errorhandler(500)
    # def server_error(error):
    #     import_cart_to_list(error)
    #     if request.is_xhr:
    #         import_cart_to_list(error)
    #         return jsonify(error=_('Sorry, an error has occurred')), 500
    #     return render_template("errors/500.html", error=error)
    #
    # @app.errorhandler(401)
    # def unauthorized(error):
    #     if request.is_xhr:
    #         return jsonify(error=_("Login required"))
    #     return redirect(url_for("profile.login", next=request.path))


def configure_extentions(app):
    db.init_app(app)
    moment.init_app(app)

    with app.test_request_context():
        db.create_all()


def configure_email(app):
    mail.init_app(app)


def configure_login_manager(app):
    login_manager.init_app(app)


def configure_manager(app):
    manager.__init__(app)
    manager.add_command('shell', Shell(make_context=make_shell_context))
    manager.add_command('db', MigrateCommand)


def configure_migrate(app):
    migrate.init_app(app, db)


def configure_pagedown(app):
    pagedown.init_app(app)


def configure_template_tag(app):
    from project.utils.template_tag import init_filters
    init_filters(app)