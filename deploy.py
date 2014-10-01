#from project import create_app
#from project.config import DeploymentConfig
#from run import Run

#application = create_app(DeploymentConfig)

#Run(application)

from project import create_app
from project.config import DevelopmentConfig
from run import Run

application = create_app(DevelopmentConfig)

Run(application)




