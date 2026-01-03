from typing import Dict, Any, Literal, Optional

from ..classes import CacheMemcached, CacheRedis


def create_cache_client(
    config: Dict[str, Any],
    engine: Literal["memcached", "redis"] | None = None,
    prefix: Optional[str] = None,
    default_ttl_seconds: Optional[int] = None,
) -> CacheMemcached | CacheRedis:
    """Create a cache client of a provided type.

    Args:
        config (Dict[str, Any]): Cache client configuration.
        engine (Literal["memcached", "redis"] | None): Cache engine to use. Defaults to None.
        prefix (:obj:`str`, optional): Prefix used for each key-value pair. Defaults to None (no prefix).
        default_ttl_seconds (:obj:`int`, optional): Default TTL for values (in seconds). Defaults to None (does not expire).

    Returns:
        CacheMemcached | CacheRedis: Cache client.
    """
    if engine not in ["memcached", "redis"] or engine is None:
        raise KeyError(f"Incorrect cache engine provided. Expected 'memcached' or 'redis', got '{engine}'")

    if "cache" not in config or engine not in config["cache"]:
        raise KeyError(
            f"Cache configuration is invalid. Please check if all keys are set (engine: '{engine}')"
        )

    match engine:
        case "memcached":
            return CacheMemcached.from_config(config["cache"][engine], prefix=prefix, default_ttl_seconds=default_ttl_seconds)
        case "redis":
            return CacheRedis.from_config(config["cache"][engine], prefix=prefix, default_ttl_seconds=default_ttl_seconds)
        case _:
            raise KeyError(f"Cache implementation for the engine '{engine}' is not present.")
