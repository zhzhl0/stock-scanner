from functools import wraps

from cachetools import TTLCache


def async_memorycache(cache: TTLCache):
    """自定义支持异步方法的缓存装饰器
    Args:
        cache: 缓存对象，需要实现字典接口（如TTLCache）
    Returns:
        装饰器函数
    """

    def decorator(func):
        """实际的装饰器函数
        Args:
            func: 被装饰的异步函数
        Returns:
            包装后的函数
        """

        @wraps(func)  # 保留原函数的元信息
        async def wrapper(*args, **kwargs):
            """包装函数，实现缓存逻辑
            Args:
                *args: 位置参数
                **kwargs: 关键字参数
            Returns:
                缓存结果或函数执行结果
            """
            # 生成缓存键，使用参数元组和关键字参数的冻结集合
            key = (args, frozenset(kwargs.items()))

            # 如果缓存中存在该键，直接返回缓存结果
            if key in cache:
                return cache[key]

            # 执行原函数并获取结果
            result = await func(*args, **kwargs)

            # 将结果存入缓存
            cache[key] = result

            # 返回函数执行结果
            return result

        return wrapper

    return decorator
