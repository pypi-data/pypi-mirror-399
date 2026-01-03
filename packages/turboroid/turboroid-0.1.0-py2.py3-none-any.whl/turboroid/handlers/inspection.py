from dataclasses import dataclass
from typing import Any


@dataclass
class ParamCache:
    name: str
    annotation: Any
    is_request: bool
    has_default: bool
