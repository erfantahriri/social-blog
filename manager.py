from project import create_app
from project.config import DevelopmentConfig
from project.application import manager

application = create_app(DevelopmentConfig)

manager.run()
