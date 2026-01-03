from typing import Any
from urllib.parse import parse_qs

import orjson

from turboroid.config import settings, TRUSTED_PROXY_HEADERS
from turboroid.asgi import Scope, Receive


class Request:
    def _get_header_value(self, name: str) -> str | None:
        """A helper to quickly fetch a header value, handling case insensitivity."""
        name_bytes = name.lower().encode("latin-1")
        for h_name, h_value in self.headers:
            if h_name == name_bytes:
                return h_value.decode("latin-1")
        return None

    @property
    def ip(self) -> str | None:
        """
        Retrieves the client IP, checking proxy headers only if configured.
        """
        if settings.use_proxy_headers:
            for header_name_lower in TRUSTED_PROXY_HEADERS:
                header_value = self._get_header_value(header_name_lower)
                if header_value:
                    if header_name_lower == "x-forwarded-for":
                        return header_value.split(",")[0].strip()
                    return header_value

        return self._client_ip

    def __init__(
        self, scope: Scope, receive: Receive, path_params: dict[str, str] | None = None
    ):
        self._client_ip = None
        self._client_port = None
        # The client key in scope holds a tuple: (client_ip, client_port)
        client_info: tuple[str, int] | None = scope.get("client")
        if client_info and len(client_info) == 2:
            self._client_ip = client_info[0]
            self._client_port = client_info[1]

        self.method: str = scope["method"]
        self.path: str = scope["path"]
        self.headers: tuple[tuple[bytes, bytes], ...] = scope.get("headers", ())

        self.query_params: dict[str, str] = self._parse_query_string(
            scope.get("query_string", b"")
        )
        self.path_params: dict[str, str] = (
            path_params if path_params is not None else {}
        )

        self._receive: Receive = receive

        self._body: bytes | None = None
        self._json: dict | None = None

    @staticmethod
    def _parse_query_string(query_string: bytes) -> dict[str, str]:
        """Parses the raw query string bytes into a dictionary of strings."""
        if not query_string:
            return {}

        parsed = parse_qs(query_string.decode("latin-1"))
        return {k: v[0] for k, v in parsed.items()}

    async def body(self) -> bytes:
        if self._body is not None:
            return self._body

        body_parts = []

        # Loop to consume all body chunks until 'more_body' is False
        while True:
            message = await self._receive()

            if message["type"] == "http.request":
                body_parts.append(message.get("body", b""))
                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                break

        self._body = b"".join(body_parts)
        return self._body

    async def json(self) -> dict[str, Any]:
        """Reads the body and attempts to parse it as JSON."""
        if self._json is not None:
            return self._json

        body = await self.body()
        if not body:
            return {}

        try:
            self._json = orjson.loads(body.decode("utf-8"))
            return self._json
        except orjson.JSONDecodeError as exc:
            raise ValueError("Invalid JSON body.") from exc

    # Note: Add 'form' method similarly for application/x-www-form-urlencoded
