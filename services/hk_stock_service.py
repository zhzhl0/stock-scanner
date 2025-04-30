import asyncio
from typing import Any, Dict, List

import akshare as ak
import pandas as pd

from utils.async_diskcache import async_diskcache
from utils.logger import get_logger

# 获取日志器
logger = get_logger()


class HkStockServiceAsync:
    def __init__(self):
        """
        初始化AStockServiceAsync类
        """
        logger.debug("初始化AStockServiceAsync类")

    async def search_hk_stocks(self, keyword: str) -> List[Dict[str, Any]]:
        """
        异步搜索港股代码

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的股票列表
        """
        try:
            logger.info(f"异步搜索港股: {keyword}")

            # 使用线程池执行同步的akshare调用
            df = await self._get_hk_stocks_data()

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
                        "market_value": 0.0,
                    }
                )
                # 限制只返回前10个结果
                if len(formatted_results) >= 10:
                    break

            logger.info(f"港股搜索完成，找到 {len(formatted_results)} 个匹配项（限制显示前10个）")
            return formatted_results

        except Exception as e:
            error_msg = f"搜索港股代码失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)

    @async_diskcache(expire=3600 * 12, key_prefix="hk_stocks_data")
    async def _get_hk_stocks_data(self) -> pd.DataFrame:
        """
        获取港股股票数据
        Returns:
            pd.DataFrame: 包含港股股票数据的DataFrame
        """
        try:
            logger.debug("获取港股股票实时行情数据")
            df = await asyncio.to_thread(ak.stock_hk_spot_em)
            logger.debug("港股股票实时行情数据获取完成")
            return df
        except Exception as e:
            error_msg = f"获取港股股票实时行情数据失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)

    @async_diskcache()
    async def get_name_by_symbol(self, symbol: str) -> str:
        """
        根据股票代码获取股票名称
        Args:
            symbol: 股票代码
        Returns:
            股票名称
        """
        try:
            logger.info(f"根据股票代码获取股票名称: {symbol}")
            # 使用线程池执行同步的akshare调用
            df = await self._get_hk_stocks_data()
            # 查找股票名称
            name = df.loc[df["代码"] == symbol, "名称"].values
            if len(name) > 0:
                logger.info(f"股票名称获取完成: {name[0]}")
                return name[0]
            else:
                logger.warning(f"未找到股票代码: {symbol} 的名称")
                return ""
        except Exception as e:
            error_msg = f"获取股票名称失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
