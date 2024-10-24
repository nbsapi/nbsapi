from sqlalchemy.orm import declarative_base

Base = declarative_base()  # model base class
from .adaptation_target import AdaptationTarget
from .apiversion import ApiVersion
from .naturebasedsolution import Association, NatureBasedSolution
from .user import User
