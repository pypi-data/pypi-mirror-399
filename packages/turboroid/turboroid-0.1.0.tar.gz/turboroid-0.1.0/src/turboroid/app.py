import inspect
import time
from typing import Callable, Awaitable, Any

from turbolightdi.container import TurboLightDIContainer

from turboroid.asgi import Scope, Receive, Send
from turboroid.config import settings, TurboroidSettings
from turboroid.constants import ScopeType
from turboroid.handlers.inspection import ParamCache
from turboroid.http.constants import HttpStatus, MediaType
from turboroid.http.models import NotFoundData, InternalServerErrorData
from turboroid.logger import logger
from turboroid.http.request import Request
from turboroid.http.response import Response
from turboroid.routing.registry import PENDING_ROUTES
from turboroid.routing.router import Router, RouteMatch
from turboroid.utils.banner import print_banner


class Turboroid:
    def __init__(self, is_debug: bool = True):
        self.router = Router()
        self._handler_plans: dict[Callable, list[ParamCache]] = {}
        self.is_debug: bool = is_debug
        self.settings: TurboroidSettings = settings

        self._scope_dispatch: dict[
            str, Callable[[Scope, Receive, Send], Awaitable[None]]
        ] = {
            ScopeType.HTTP.value: self._handle_http_request,
        }

        print_banner()

    def wire_hive(self, container: TurboLightDIContainer):
        """
        NEW: Replaces _load_pending_routes.
        Bridge between DI Container and Router.
        """
        all_classes = container.get_registry()

        for cls in all_classes:
            if getattr(cls, "_is_controller", False):
                instance = container.resolve_dep(cls)
                self._harvest_routes(instance)

    def _harvest_routes(self, instance: Any):
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            func = method.__func__

            if getattr(func, "_is_route", False):
                path = getattr(func, "_route_path")
                verb = getattr(func, "_route_method")

                self.router.add_route(path, verb, method)

    def _get_handler_kwargs(
        self, handler: Callable, request: Request
    ) -> dict[str, Any]:
        if handler not in self._handler_plans:
            self._cache_handler_plan(handler)

        plan = self._handler_plans[handler]
        kwargs = {}

        path_params = request.path_params
        query_params = request.query_params

        for p in plan:
            if p.is_request:
                kwargs[p.name] = request
                continue

            val = path_params.get(p.name)
            if val is None:
                val = query_params.get(p.name)

            if val is not None:
                if self.settings.explicit_cast and p.annotation is not Any:
                    try:
                        kwargs[p.name] = p.annotation(val)
                    except (ValueError, TypeError) as exc:
                        raise TypeError(f"Invalid cast for '{p.name}': {exc}")
                else:
                    kwargs[p.name] = val  # type: ignore
            elif not p.has_default:
                raise TypeError(f"Missing required parameter '{p.name}'")

        return kwargs

    def _cache_handler_plan(self, handler: Callable):
        """Runs once per handler to analyze signature."""

        sig = inspect.signature(handler)
        plans = []

        for name, param in sig.parameters.items():
            plans.append(
                ParamCache(
                    name=name,
                    annotation=param.annotation
                    if param.annotation is not inspect.Parameter.empty
                    else Any,
                    is_request=(param.annotation is Request or name == "request"),
                    has_default=(param.default is not inspect.Parameter.empty),
                )
            )
        self._handler_plans[handler] = plans

    def _load_pending_routes(self):
        """Transfers all routes defined by global decorators to the router."""
        for path, method, handler in PENDING_ROUTES:
            self.router.add_route(path, method, handler)
        PENDING_ROUTES.clear()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = time.perf_counter() if self.is_debug else 0.0
        handler = self._scope_dispatch.get(scope["type"])

        if handler:
            await handler(scope, receive, send)

        if self.is_debug:
            duration = (time.perf_counter() - start) * 1000
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "UNKNOWN")
            logger.debug(f"[{method} {path}] Total Latency: {duration:.4f}ms")

    @staticmethod
    def get_scope_type(raw_scope_type: str | None) -> ScopeType | None:
        """Safely converts a raw scope type string to the ScopeType enum member."""
        try:
            if raw_scope_type is not None:
                return ScopeType(raw_scope_type)
            return None
        except ValueError:
            return None

    async def _handle_http_request(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        route_match: RouteMatch | None = self.router.match(scope)
        final_response: Response

        if not route_match:
            final_response = Response(
                body=NotFoundData(path=scope["path"]),
                status=HttpStatus.HTTP_404_NOT_FOUND,
                media_type=MediaType.APPLICATION_JSON,
            )
        else:
            try:
                request = Request(scope, receive, path_params=route_match.path_params)
                handler_kwargs = self._get_handler_kwargs(route_match.handler, request)
                handler_result = await route_match.handler(**handler_kwargs)
                final_response = Response.auto(
                    handler_result, handler=route_match.handler
                )

            except Exception as e:
                logger.exception(f"Server Error: {type(e).__name__}", exc_info=True)
                final_response = Response(
                    body=InternalServerErrorData(path=scope["path"]),
                    status=HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR,
                    media_type=MediaType.APPLICATION_JSON,
                )

        await self._send_response(send, final_response)

    async def _send_response(
        self, send: Send, response: Response, more_body: bool = False
    ) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": response.status,
                "headers": response.get_headers(),
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": response.body,
                "more_body": more_body,
            }
        )
