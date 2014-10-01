from project import create_app
from project.config import DevelopmentConfig
from project.application import manager


application = create_app(DevelopmentConfig)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    application.wsgi_app = ProfilerMiddleware(application.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    application.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from project.apps.auth.models import Role_auth as Role, User_auth as User

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

    # create self-follows for all users
    # User.add_self_follows()

if not application.debug and not application.testing and not application.config['SSL_DISABLE']:
    from flask.ext.sslify import SSLify
    sslify = SSLify(application)

if __name__ == "__main__":
    manager.run()