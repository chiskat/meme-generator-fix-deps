from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from meme_generator.config import RedisConfig
from meme_generator.exception import RedisCacheError


def get_preview_cache_key(config: RedisConfig, meme_key: str) -> str:
    prefix = config.key_prefix.strip(":")
    return f"{prefix}:{meme_key}" if prefix else meme_key


def create_redis_client(config: RedisConfig) -> Redis:
    try:
        return Redis.from_url(config.url, decode_responses=True)
    except (RedisError, ValueError) as e:
        raise RedisCacheError(f"Redis 连接配置无效：{e}") from e


async def get_cached_preview_url(
    client: Any, config: RedisConfig, meme_key: str
) -> str | None:
    cache_key = get_preview_cache_key(config, meme_key)
    value = await client.get(cache_key)
    if value is None:
        return None
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


async def cache_preview_url(
    client: Any, config: RedisConfig, meme_key: str, url: str
) -> None:
    cache_key = get_preview_cache_key(config, meme_key)
    # Redis SET defaults to no expiration, so the preview URL is cached permanently.
    await client.set(cache_key, url)
