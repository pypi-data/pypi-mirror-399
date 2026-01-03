import uuid
from dataclasses import dataclass, field
import time

from turboroid.http.constants import HttpStatus


@dataclass
class BaseResponseModel:
    path: str
    status: int = HttpStatus.HTTP_404_NOT_FOUND
    message: str = HttpStatus.HTTP_404_NOT_FOUND.description
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    ts: int = field(default_factory=lambda: int(time.time()))


@dataclass
class NotFoundData(BaseResponseModel):
    status: int = HttpStatus.HTTP_404_NOT_FOUND
    message: str = HttpStatus.HTTP_404_NOT_FOUND.description


@dataclass
class InternalServerErrorData(BaseResponseModel):
    status: int = HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR.description
