from dataclasses import dataclass
from typing import Literal, Final, Tuple
import os


TRUSTED_PROXY_HEADERS: Final[Tuple[str, ...]] = ("x-forwarded-for", "x-real-ip")


def _get_env(key: str, default: str) -> str:
    return os.environ.get(f"TURBOROID_{key}", default).upper()


def _get_env_bool(key: str, default: bool) -> bool:
    default_str = str(default)
    value = os.environ.get(f"TURBOROID_{key}", default_str).lower()
    return value in ("true", "1", "yes")


@dataclass(frozen=True)
class TurboroidSettings:
    """
    Framework-level config, loaded once at startup from OS environment variables.
    """

    explicit_cast: bool = _get_env("EXPLICIT_CAST", "False").lower() in (
        "true",
        "1",
        "yes",
    )

    use_proxy_headers: bool = _get_env_bool("USE_PROXY_HEADERS", False)

    server_port: int = int(_get_env("SERVER_PORT", "8000"))
    server_host: str = _get_env("SERVER_HOST", "127.0.0.1")

    log_level: Literal["INFO", "DEBUG", "WARNING"] = _get_env("LOG_LEVEL", "INFO")  # type: ignore


settings = TurboroidSettings()
