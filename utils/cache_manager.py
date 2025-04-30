# file: utils/cache_manager.py
import asyncio
from typing import Any, Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class CacheManagerAsync:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        """启动定时任务调度器"""
        if not self.scheduler.running:
            self.scheduler.start()

    async def stop(self):
        """停止定时任务调度器"""
        self.scheduler.shutdown()

    def add_cache_task(
        self,
        func: Callable[..., Any],
        interval_minutes: Optional[int] = None,
        cron_expression: Optional[str] = None,
        task_name: str = None,
        *args,
        **kwargs,
    ):
        """
        添加定时缓存任务（支持 interval 或 cron 表达式）

        Args:
            func: 要执行的异步函数（可带参数）
            interval_minutes: 执行间隔（分钟）与 cron 二选一
            cron_expression: cron 表达式，如 "0 0 * * *" 表示每天午夜执行
            task_name: 任务名称（用于日志和调试）
            *args: 传递给func的位置参数
            **kwargs: 传递给func的关键字参数
        """
        if interval_minutes is not None:
            # 使用固定间隔模式
            self.scheduler.add_job(
                func, "interval", minutes=interval_minutes, name=task_name, args=args, kwargs=kwargs
            )
        elif cron_expression:
            # 使用 cron 模式
            try:
                # 解析 cron 表达式：minute hour day month day_of_week
                parts = cron_expression.split()
                if len(parts) != 5:
                    raise ValueError(
                        "Cron expression must have 5 fields: minute hour day month day_of_week"
                    )

                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                )

                self.scheduler.add_job(func, trigger, name=task_name, args=args, kwargs=kwargs)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {cron_expression}") from e
        else:
            raise ValueError("Either interval_minutes or cron_expression must be provided")
