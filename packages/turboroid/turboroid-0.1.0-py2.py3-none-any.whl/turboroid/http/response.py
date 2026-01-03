import dataclasses

import orjson as json
from typing import Any, Callable

from turboroid.http.constants import MediaType, HttpStatus


class Response:
    def __init__(
        self,
        body: Any = "",
        status: HttpStatus | int = HttpStatus.HTTP_200_OK,
        headers: dict[str, str] | None = None,
        media_type: MediaType | str | None = None,
    ):
        self.status = status
        self.headers = headers or {}
        self.headers["Server"] = "turboroid"

        if media_type:
            self.headers["Content-Type"] = media_type

        self.body = self._encode_body(body)

    def _encode_body(self, body: Any) -> bytes:
        if isinstance(body, bytes):
            if "Content-Type" not in self.headers:
                self.headers["Content-Type"] = MediaType.APPLICATION_OCTET_STREAM
            return body
        if dataclasses.is_dataclass(body):
            if "Content-Type" not in self.headers:
                self.headers["Content-Type"] = MediaType.APPLICATION_JSON
            return json.dumps(body, option=json.OPT_SERIALIZE_DATACLASS)
        # dict or list - auto serialize to json
        if isinstance(body, (dict, list)):
            if "Content-Type" not in self.headers:
                self.headers["Content-Type"] = MediaType.APPLICATION_JSON

            data = json.dumps(body)

            return data if isinstance(data, bytes) else data.encode("utf-8")

        # Handle str, int, float...
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = MediaType.TEXT_PLAIN
        return str(body).encode("utf-8")

    @classmethod
    def auto(cls, result: Any, handler: Callable | None = None) -> "Response":
        produces: MediaType | None = getattr(handler, "_produces", None)

        # Check if Response object
        if isinstance(result, cls):
            if produces and "Content-Type" not in result.headers:
                result.headers["Content-Type"] = produces.value
            return result

        # This handles dict, list, str, int, etc..
        return cls(body=result, media_type=produces)

    def get_headers(self) -> list[tuple[bytes, bytes]]:
        return [
            (k.lower().encode("latin-1"), str(v).encode("latin-1"))
            for k, v in self.headers.items()
        ]
