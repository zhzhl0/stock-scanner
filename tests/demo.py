import json
import os
import re
from datetime import datetime
from typing import AsyncGenerator

import httpx
import pandas as pd
from dotenv import load_dotenv

from services.a_stock_service import AStockServiceAsync
from services.fund_service_async import FundServiceAsync
from services.hk_stock_service import HkStockServiceAsync
from services.us_stock_service_async import USStockServiceAsync
from utils.api_utils import APIUtils
from utils.logger import get_logger

# 获取日志器
logger = get_logger()

class AIAnalyzer:
    def __init__(
        self,
        custom_api_url=None,
        custom_api_key=None,
        custom_api_model=None,
        custom_api_timeout=None,
    ):
        """
        初始化AI分析服务

        Args:
            custom_api_url: 自定义API URL
            custom_api_key: 自定义API密钥
            custom_api_model: 自定义API模型
            custom_api_timeout: 自定义API超时时间
        """
        # 加载环境变量
        load_dotenv()

        # 设置API配置
        self.API_URL = custom_api_url or os.getenv("API_URL")
        self.API_KEY = custom_api_key or os.getenv("API_KEY")
        self.API_MODEL = custom_api_model or os.getenv("API_MODEL", "gpt-3.5-turbo")
        self.API_TIMEOUT = int(custom_api_timeout or os.getenv("API_TIMEOUT", 60))

        self.a_stock_service = AStockServiceAsync()
        self.fund_service = FundServiceAsync()
        self.us_stock_service = USStockServiceAsync()
        self.hk_stock_service = HkStockServiceAsync()

        logger.debug(
            f"初始化AIAnalyzer: API_URL={self.API_URL}, API_MODEL={self.API_MODEL}, API_KEY={'已提供' if self.API_KEY else '未提供'}, API_TIMEOUT={self.API_TIMEOUT}"
        )

    async def get_ai_analysis(self, df: pd.DataFrame, stock_code: str, market_type: str = "A", stream: bool = False) -> AsyncGenerator[str, None]:
        try:
            logger.info(f"开始AI分析 {stock_code}, 流式模式: {stream}")

            # 新增：封装技术指标计算
            indicators = self._get_technical_indicators(df)
            recent_data = df.tail(14).to_dict("records")

            # 新增：使用字典管理不同市场的提示模板
            prompt_templates = {
                "ETF": self._get_fund_prompt(stock_code, indicators, recent_data),
                "US": self._get_us_stock_prompt(stock_code, indicators, recent_data),
                "HK": self._get_hk_stock_prompt(stock_code, indicators, recent_data),
                "A": self._get_a_stock_prompt(stock_code, indicators, recent_data)
            }
            prompt = prompt_templates.get(market_type, prompt_templates["A"])

            # 新增：异步获取股票名称
            stock_name = await self._get_stock_name(stock_code, market_type)

            # 格式化API URL
            api_url = APIUtils.format_api_url(self.API_URL)

            # 准备请求数据
            request_data = {
                "model": self.API_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "stream": stream,
            }

            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_KEY}",
            }

            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                # 记录请求
                logger.debug(f"发送AI请求: URL={api_url}, MODEL={self.API_MODEL}, STREAM={stream}")

                # 先发送技术指标数据
                yield json.dumps(
                    {
                        "stock_code": stock_code,
                        "name": stock_name,
                        "status": "analyzing",
                        "rsi": rsi,
                        "price": price,
                        "price_change": price_change,
                        "ma_trend": ma_trend,
                        "macd_signal": macd_signal_type,
                        "volume_status": volume_status,
                        "analysis_date": analysis_date,
                    }
                )

                if stream:
                    async with client.stream("POST", api_url, json=request_data, headers=headers) as response:
                        if response.status_code != 200:
                            # 新增：统一错误处理
                            async for error_chunk in self._handle_api_error(response, stock_code):
                                yield error_chunk
                            return

                        # 优化后的流式处理逻辑
                        async for content in self._process_streaming_response(response, stock_code):
                            yield content

                else:
                    # 非流式响应处理
                    response = await client.post(api_url, json=request_data, headers=headers)

                    if response.status_code != 200:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", "未知错误")
                        logger.error(f"AI API请求失败: {response.status_code} - {error_message}")
                        yield json.dumps(
                            {
                                "stock_code": stock_code,
                                "error": f"API请求失败: {error_message}",
                                "status": "error",
                            }
                        )
                        return

                    response_data = response.json()
                    analysis_text = (
                        response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    )

                    # 尝试从分析内容中提取投资建议
                    recommendation = self._extract_recommendation(analysis_text)

                    # 计算分析评分
                    score = self._calculate_analysis_score(analysis_text, technical_summary)

                    # 发送完整的分析结果
                    yield json.dumps(
                        {
                            "stock_code": stock_code,
                            "status": "completed",
                            "analysis": analysis_text,
                            "score": score,
                            "recommendation": recommendation,
                            "rsi": rsi,
                            "price": price,
                            "price_change": price_change,
                            "ma_trend": ma_trend,
                            "macd_signal": macd_signal_type,
                            "volume_status": volume_status,
                            "analysis_date": analysis_date,
                        }
                    )

        except Exception as e:
            logger.error(f"AI分析出错: {str(e)}")
            yield json.dumps({
                "stock_code": stock_code,
                "error": f"分析出错: {str(e)}",
                "status": "error",
            })

    def _get_technical_indicators(self, df: pd.DataFrame) -> dict:
        """封装技术指标计算"""
        latest = df.iloc[-1]
        return {
            "rsi": latest.get("RSI"),
            "price": latest.get("Close"),
            "price_change": latest.get("Change"),
            "ma_trend": "UP" if latest.get("MA5", 0) > latest.get("MA20", 0) else "DOWN",
            "macd_signal_type": "BUY" if latest.get("MACD", 0) > latest.get("MACD_Signal", 0) else "SELL",
            "volume_status": self._get_volume_status(latest.get("Volume_Ratio", 1)),
            "technical_summary": {
                "trend": "upward" if latest["MA5"] > latest["MA20"] else "downward",
                "volatility": f"{latest['Volatility']:.2f}%",
                "volume_trend": "increasing" if latest["Volume_Ratio"] > 1 else "decreasing",
                "rsi_level": latest["RSI"]
            }
        }

    async def _handle_api_error(self, response, stock_code: str) -> AsyncGenerator[str, None]:
        """统一处理API错误响应"""
        try:
            error_data = await response.json()
            error_msg = error_data.get("error", {}).get("message", "未知错误")
        except Exception as e:
            error_msg = f"HTTP错误: {response.status_code}"

        logger.error(f"API请求失败: {error_msg}")
        yield json.dumps({
            "stock_code": stock_code,
            "error": error_msg,
            "status": "error"
        })

    async def _get_stock_name(self, stock_code: str, market_type: str) -> str:
        """统一获取股票名称"""
        services = {
            "ETF": (self.fund_service, "get_fund_name_by_symbol"),
            "US": (self.us_stock_service, "get_name_by_symbol"),
            "HK": (self.hk_stock_service, "get_name_by_symbol"),
            "A": (self.a_stock_service, "get_name_by_symbol")
        }
        service, method = services.get(market_type, (self.a_stock_service, "get_name_by_symbol"))
        return await getattr(service, method)(stock_code)

    async def _process_streaming_response(self, response, stock_code: str):
        """优化后的流式响应处理"""
        buffer = ""
        decoder = json.JSONDecoder()
        partial_data = ""

        async for chunk in response.aiter_text():
            if chunk := chunk.strip():
                partial_data += chunk.replace("data: ", "").replace("null", '""')

            while partial_data:
                try:
                    data, idx = decoder.raw_decode(partial_data)
                    partial_data = partial_data[idx:].lstrip()

                    if content := data.get("choices", [{}])[0].get("delta", {}).get("content"):
                        buffer += content
                        yield json.dumps({
                            "stock_code": stock_code,
                            "ai_analysis_chunk": content,
                            "status": "analyzing"
                        })

                except json.JSONDecodeError:
                    break

        # 最终处理逻辑
        if buffer:
            yield json.dumps({
                "stock_code": stock_code,
                "status": "completed",
                "score": self._calculate_analysis_score(buffer, indicators["technical_summary"]),
                "recommendation": self._extract_recommendation(buffer)
            })

    # ... 保留其他辅助方法 ...
