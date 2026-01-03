from typing import Callable

from turboroid.http.constants import HttpMethod

RouteEntry = tuple[str, HttpMethod, Callable]

PENDING_ROUTES: list[RouteEntry] = []
