from enum import Enum
from typing import final


@final
class LifespanType(str, Enum):
    STARTUP = "lifespan.startup"
    SHUTDOWN = "lifespan.shutdown"
