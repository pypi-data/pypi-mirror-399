from typing import Callable

from turboroid.http.constants import HttpMethod, MediaType


def request_mapping(
    path: str, method: HttpMethod, produces: MediaType | None = None
) -> Callable:
    """The decorator factory for route registration."""

    def decorator(handler: Callable):
        handler._is_route = True  # type: ignore[attr-defined]
        handler._route_path = path  # type: ignore[attr-defined]
        handler._route_method = method  # type: ignore[attr-defined]
        handler._produces = produces  # type: ignore[attr-defined]

        return handler

    return decorator


def get(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.GET, produces=produces)


def post(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.POST, produces=produces)


def put(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.PUT, produces=produces)


def patch(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.PATCH, produces=produces)


def delete(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.DELETE, produces=produces)


def head(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.HEAD, produces=produces)


def options(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.OPTIONS, produces=produces)


def trace(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.TRACE, produces=produces)


def connect(value: str, produces: MediaType | None = None) -> Callable:
    return request_mapping(value, method=HttpMethod.CONNECT, produces=produces)
