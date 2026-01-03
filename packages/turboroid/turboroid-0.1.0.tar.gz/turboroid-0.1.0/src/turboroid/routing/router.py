from typing import Callable, Any, NamedTuple
from turboroid.http.constants import HttpMethod

Handler = Callable[..., Any]


class RouteMatch(NamedTuple):
    handler: Handler
    path_params: dict[str, str]


class RouteNode:
    def __init__(self, path: str, handler: Handler):
        self.path: str = path
        self.handler: Handler = handler
        self.path_segments: list[str] = self.parse_path_segments(path)

    @staticmethod
    def parse_path_segments(path: str) -> list[str]:
        """Splits path into segments, ignoring leading/trailing slashes."""
        return [segment for segment in path.strip("/").split("/") if segment]


class Router:
    def __init__(self):
        self.routes: dict[str, list[RouteNode]] = {  # type: ignore
            method.value: [] for method in HttpMethod
        }

    def add_route(self, path: str, method: str, handler: Handler) -> None:
        method_str = method.upper()
        if not HttpMethod.is_valid(method_str):
            raise ValueError(f"Invalid HTTP method '{method_str}'.")

        route_node = RouteNode(path, handler)
        self.routes[method_str].append(route_node)

    def match(self, scope: dict) -> RouteMatch | None:
        method_str = scope["method"]
        path_str = scope["path"]
        incoming_segments = RouteNode.parse_path_segments(path_str)

        potential_routes = self.routes.get(method_str, [])
        for route_node in potential_routes:
            path_params: dict[str, str] = {}
            registered_segments = route_node.path_segments

            if len(incoming_segments) != len(registered_segments):
                continue

            is_match = True

            for registered, incoming in zip(registered_segments, incoming_segments):
                # slug is {}
                if registered.startswith("{") and registered.endswith("}"):
                    param_name = registered.strip("{}")
                    path_params[param_name] = incoming

                elif registered != incoming:
                    is_match = False
                    break

            if is_match:
                return RouteMatch(handler=route_node.handler, path_params=path_params)

        return None
