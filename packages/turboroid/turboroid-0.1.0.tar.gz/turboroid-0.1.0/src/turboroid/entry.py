import sys
from typing import Type, TypeVar
from turbolightdi.scanner import scan_packages
from turbolightdi.container import context

T = TypeVar("T")

_GLOBAL_ENGINE_CACHE = None


def turboroid_app(cls: Type[T]) -> Type[T]:
    """
    Bootstraps the Turboroid application.
    Automatically handles scanning, DI resolution, and route wiring.
    """

    def bootstrap():
        global _GLOBAL_ENGINE_CACHE
        if _GLOBAL_ENGINE_CACHE is not None:
            return _GLOBAL_ENGINE_CACHE

        root_package = cls.__module__.split(".")[0]
        scan_packages(root_package)

        from turboroid.app import Turboroid

        engine = context.resolve_dep(Turboroid)

        engine.wire_hive(context)

        _GLOBAL_ENGINE_CACHE = engine
        return _GLOBAL_ENGINE_CACHE

    # Support asgi server run with: my_package:MyApp:app to work
    class AppDescriptor:
        def __get__(self, instance, owner):
            return bootstrap()

    setattr(cls, "app", AppDescriptor())

    target_module = sys.modules[cls.__module__]
    if not hasattr(target_module, "app"):
        setattr(target_module, "app", bootstrap())

    return cls
