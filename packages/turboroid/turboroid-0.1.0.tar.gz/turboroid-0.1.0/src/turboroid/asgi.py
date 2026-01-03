from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, Any, List, Tuple

from turboroid.constants import ScopeType
from turboroid.http.constants import HttpMethod

# For ASGI spec references only.

Scope = Dict[str, Any]

# HTTP Scope
Headers = List[Tuple[bytes, bytes]]
Address = Tuple[str, int] | None


@dataclass(frozen=True)
class AsgiVersion:
    spec_version: str
    version: str


@dataclass(frozen=True)
class HTTPScope:
    # Required
    type: str
    asgi: AsgiVersion
    http_version: str
    method: HttpMethod
    scheme: str
    path: str
    headers: Headers

    # Optional
    # Granian ASGI
    extensions: dict = field(default_factory=dict)
    root_path: str = ""
    query_string: bytes = field(default=b"")
    client: Address = None
    server: Address = None
    raw_path: bytes = field(default=b"")

    state: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_raw_scope(raw_scope: Scope) -> "HTTPScope":
        """
        Creates an HTTPScope instance from the raw dictionary provided by the ASGI server.
        """

        scope_copy = raw_scope.copy()

        if scope_copy.get("type") != ScopeType.HTTP.value:
            raise ValueError(
                f"Scope type must be {ScopeType.HTTP.value}' for HTTPScope creation."
            )

        asgi_dict = scope_copy.pop("asgi")
        asgi_version = AsgiVersion(**asgi_dict)

        raw_method = scope_copy.pop("method")
        http_method_enum: HttpMethod = HttpMethod(raw_method)
        raw_path_bytes = scope_copy.pop("raw_path", b"")

        return HTTPScope(
            asgi=asgi_version,
            method=http_method_enum,
            raw_path=raw_path_bytes,
            **scope_copy,
        )


Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]
