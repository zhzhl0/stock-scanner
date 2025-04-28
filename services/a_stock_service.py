import asyncio
from typing import Any, Dict, List

import akshare as ak
import pandas as pd

from utils.async_diskcache import async_diskcache
from utils.logger import get_logger

# 获取日志器
logger = get_logger()


class AStockServiceAsync:
    def __init__(self):
        """
        初始化AStockServiceAsync类
        """
        logger.debug("初始化AStockServiceAsync类")

    async def search_a_stocks(self, keyword: str) -> List[Dict[str, Any]]:
        """
        异步搜索A股代码

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的股票列表
        """
        try:
            logger.info(f"异步搜索A股: {keyword}")

            # 使用线程池执行同步的akshare调用
            df = await self._get_a_stocks_data()

            # 模糊匹配搜索
            mask = df["名称"].str.contains(keyword, case=False, na=False)
            results = df[mask]

            # 格式化返回结果并处理 NaN 值
            formatted_results = []
            for _, row in results.iterrows():
                formatted_results.append(
                    {
                        "name": row["名称"] if pd.notna(row["名称"]) else "",
                        "symbol": str(row["代码"]) if pd.notna(row["代码"]) else "",
                        "price": float(row["最新价"]) if pd.notna(row["最新价"]) else 0.0,
                        "market_value": (float(row["总市值"]) if pd.notna(row["总市值"]) else 0.0),
                    }
                )
                # 限制只返回前10个结果
                if len(formatted_results) >= 10:
                    break

            logger.info(f"A股搜索完成，找到 {len(formatted_results)} 个匹配项（限制显示前10个）")
            return formatted_results

        except Exception as e:
            error_msg = f"搜索A股代码失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)

    @async_diskcache(expire=3600 * 12)
    async def _get_a_stocks_data(self) -> pd.DataFrame:
        """
        获取A股股票数据
        Returns:
            pd.DataFrame: 包含A股股票数据的DataFrame
        """
        try:
            logger.debug("获取A股股票实时行情数据")
            df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            logger.debug("A股股票实时行情数据获取完成")
            return df
        except Exception as e:
            error_msg = f"获取A股股票实时行情数据失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)
