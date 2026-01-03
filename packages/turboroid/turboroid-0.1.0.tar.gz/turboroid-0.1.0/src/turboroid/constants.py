from enum import Enum
from typing import final


@final
class ScopeType(str, Enum):
    HTTP = "http"
    WEBSOCKET = "websocket"
    LIFESPAN = "lifespan"
