import asyncio
from functools import wraps
from typing import Any, Callable, Optional

from diskcache import Cache


class AsyncDiskCache:
    """异步磁盘缓存管理器"""

    def __init__(self, cache_dir: str = "cache"):
        self.cache = Cache(cache_dir)

    async def get(self, key: str, default: Any = None) -> Any:
        """异步获取缓存"""
        return await asyncio.to_thread(self.cache.get, key, default)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """异步设置缓存（带过期时间）"""
        await asyncio.to_thread(self.cache.set, key, value, expire)

    async def delete(self, key: str) -> None:
        """异步删除缓存"""
        await asyncio.to_thread(self.cache.delete, key)


def async_diskcache(
    cache_dir: str = "cache",
    key_prefix: str = "",
    expire: Optional[int] = None,
) -> Callable:
    """
    异步缓存装饰器
    :param cache_dir: 缓存目录
    :param key_prefix: 缓存键前缀
    :param expire: 过期时间（秒）
    """
    cache = AsyncDiskCache(cache_dir)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 生成唯一缓存键（基于函数名和参数）
            cache_key = f"{key_prefix}{func.__name__}_{str(args)}_{str(kwargs)}"

            # 尝试从缓存读取
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 缓存未命中，执行函数并存储结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire=expire)
            return result

        return wrapper

    return decorator
